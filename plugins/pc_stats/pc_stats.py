try:
  import psutil
except:
  psutil = None

import txthings.resource as resource
import txthings.coap as coap
from twisted.internet.task import LoopingCall

class CBResource(resource.CoAPResource):

  def __init__(self, rate, fn):
    resource.CoAPResource.__init__(self)
    self.visible = True
    self.observable = True
    self.fn = fn
    LoopingCall(self.updatedState).start(rate)

  def render_GET(self, req):
    return defer.succeed(coap.Message(code=coap.CONTENT, payload=str(self.fn())))

def cpuResources(rate):
  cpur = resource.CoAPResource()
  for i in xrange(psutil.cpu_count()):
    cpuidxr = resource.CoAPResource()
    cpuidxr.putChild('utilization', CBResource(rate, lambda: psutil.cpu_percent(interval=0, percpu=True)[i]))
    cpur.putChild(str(i), cpuidxr)
  return cpur

def netResources(rate):
  attrs = ['bytes_sent', 'bytes_recv', 'packets_sent', 'packets_recv', 'errin',
    'errout', 'dropin', 'dropout']
  netr = resource.CoAPResource()
  for itfc,_ in psutil.net_io_counters(pernic=True).iteritems():
    itfcr = resource.CoAPResource()
    for attr in attrs:
      itfcr.putChild(attr, CBResource(rate, lambda: getattr(psutil.net_io_counters(pernic=True)[itfc], attr)))
    netr.putChild(itfc, itfcr)
  return netr

def memResources(rate):
  return CBResource(rate, lambda: psutil.virtual_memory().percent)

def swapResources(rate):
  return CBResource(rate, lambda: psutil.swap_memory().percent)

def diskResources(rate):
  disk = resource.CoAPResource()
  for d in psutil.disk_partitions():
    name = d.mountpoint.replace('/', '_').replace('\\', '_')
    disk.putChild(name, CBResource(rate, lambda: psutil.disk_usage(d.mountpoint).percent))
  return disk

def init(config, root):
  if psutil == None: return
  if not config.has_option('pc_stats', 'rate'): raise 'Missing rate'
  rate = config.getfloat('pc_stats', 'rate')
  psutilr = resource.CoAPResource()
  psutilr.putChild('cpu',  cpuResources(rate))
  psutilr.putChild('net',  netResources(rate))
  psutilr.putChild('mem',  memResources(rate))
  psutilr.putChild('swap', swapResources(rate))
  psutilr.putChild('disk', diskResources(rate))
  root.putChild('psutil', psutilr)
