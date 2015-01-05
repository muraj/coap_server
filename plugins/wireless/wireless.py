import asyncio

import aiocoap.resource as resource
import aiocoap

WIRELESS_FILE = '/proc/net/wireless'
wireless_stats = {}
wireless_resources = []

def updateWifi():
  global wireless_stats, WIRELESS_FILE
  with open(WIRELESS_FILE, 'r') as f:
    f.readline()
    f.readline()
    for line in f:
      values = [ x.strip() for x in line.split() ]
      values[0] = values[0].partition(':')[0].strip()
      wireless_stats[values[0]] = values[1:]

def updateResources():
  global wireless_resources
  for r in wireless_resources:
    r.updatedState()

def update(rate):
  updateWifi()
  updateResources()
  asyncio.get_event_loop().call_later(rate, update, rate)

class wirelessResource(resource.ObservableResource):

  def __init__(self, itfc, idx):
    super(wirelessResource, self).__init__()
    self.itfc = itfc
    self.idx = idx

  def render_GET(self, req):
    global wireless_stats
    vals = wireless_stats[self.itfc]
    return aiocoap.Message(code=aiocoap.CONTENT, payload=vals[idx].encode('ascii'))

def init(config, root):
  global WIRELESS_FILE, wireless_resources
  interfaces = [ x.strip() for x in config.get('wireless', 'interfaces').split(',') ]
  value_strings = ['status', 'link', 'level', 'noise']
  rate = config.getfloat('wireless', 'rate')
  for itfc in interfaces:
    for i,k in enumerate(value_strings):
      wireless_resources.append(wirelessResource(itfc, i))
      root.add_resource(('wireless', itfc, k), wireless_resources[-1])
  update(rate)
