import os
import asyncio

import aiocoap.resource as resource
import aiocoap

class DS18B20(resource.ObservableResource):

  def __init__(self, path, rate):
    super(DS18B20, self).__init__()
    self.path = path
    self.notify()

  def notify(self, rate):
    self.updated_state()
    asyncio.get_event_loop().call_later(rate, self.notify, rate)

  @asyncio.coroutine
  def render_GET(self, req):
    while 1: # ick...
      with open(self.path, 'r') as f:
        if f.readline().split()[-1] != 'YES': continue
        val = float(f.readline().split()[-1].split('=')[-1]) / 1000.0
        return aiocoap.Message(code=aiocoap.CONTENT, payload=str(val).encode('ascii'))

def init(config, root):
  if not os.path.exists('/sys/bus/w1/devices'): return
  devices = [ x.strip() for x in config.get('onewire', 'devices') ]
  rate = config.getfloat('onewire', 'rate')
  for dev in devices:
    path = '/sys/bus/w1/devices/' + dev + '/w1_slave'
    if not os.path.exists(path): continue
    root.add_resource(('1wire', dev), DS18B20(path, rate))
