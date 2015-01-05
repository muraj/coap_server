try:
  import psutil
except:
  psutil = None

import asyncio

import aiocoap.resource as resource
import aiocoap

class CBResource(resource.ObservableResource):

  def __init__(self, rate, fn):
    super(CBResource, self).__init__()
    self.fn = fn
    self.notify(rate)

  def notify(self, rate):
    self.updated_state()
    asyncio.get_event_loop().call_later(rate, self.notify, rate)

  @asyncio.coroutine
  def render_GET(self, req):
    payload = str(self.fn()).encode('ascii')
    return aiocoap.Message(code=aiocoap.CONTENT, payload=payload)

def cpuResources(root, rate):
  for i in range(psutil.cpu_count()):
    root.add_resource(('psutil', 'cpu', str(i), 'utilization'), CBResource(rate,
      lambda: psutil.cpu_percent(interval=0, percpu=True)[i]))

def netResources(root, rate):
  attrs = ['bytes_sent', 'bytes_recv', 'packets_sent', 'packets_recv', 'errin',
    'errout', 'dropin', 'dropout']
  for itfc,_ in psutil.net_io_counters(pernic=True).items():
    for attr in attrs:
      root.add_resource(('psutil', 'net', itfc, attr), CBResource(rate,
        lambda: getattr(psutil.net_io_counters(pernic=True)[itfc], attr)))

def memResources(root, rate):
  root.add_resource(('psutil', 'mem'), CBResource(rate, lambda: psutil.virtual_memory().percent))

def swapResources(root, rate):
  root.add_resource(('psutil', 'swap'), CBResource(rate, lambda: psutil.swap_memory().percent))

def diskResources(root, rate):
  for d in psutil.disk_partitions():
    # TODO: replace with quote
    name = d.mountpoint.replace('/', '%2F').replace('\\', '%5C')
    root.add_resource(('psutil', 'disk', name), CBResource(rate,
      lambda: psutil.disk_usage(d.mountpoint).percent))

def init(config, root):
  if psutil == None: return
  rate = config.getfloat('pc_stats', 'rate')
  cpuResources(root,  rate)
  netResources(root,  rate)
  memResources(root,  rate)
  swapResources(root, rate)
  diskResources(root, rate)
