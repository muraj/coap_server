import txthings.resource as resource
import txthings.coap as coap
from twisted.internet.task import LoopingCall

class DS18B20(coap.CoAPResource):

  def __init__(self, path, rate):
    coap.CoAPResource.__init__(self)
    self.visible = True
    self.observable = True
    self.path = path
    LoopingCall(self.updatedState).start(rate)

  def render_GET(self, req):
    while 1:
      with open(self.path, 'r') as f:
        if f.readline().split()[-1] != 'YES': continue
        val = float(f.readline().split()[-1].split('=')[-1]) / 1000.0
        resp = coap.Message(code=coap.CONTENT, payload=str(val))
        return defer.succeed(resp)

def init(config, root):
  if not os.path.exists('/sys/bus/w1/devices'): return
  if not config.has_section('onewire'): return
  if not config.has_option('onewire', 'devices'): return
  if not config.has_option('onewire', 'rate'): return
  devices = [ x.strip() for x in config.get('onewire', 'devices') ]
  rate = config.getfloat('onewire', 'rate')
  onewr = coap.CoAPResource()
  for dev in devices:
    path = '/sys/bus/w1/devices/' + dev + '/w1_slave'
    if not os.path.exists(path): continue
    onewr.putChild(dev, DS18B20(path, rate))
  root.putChild('1wire', onewr)
