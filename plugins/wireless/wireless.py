import os

import txthings.resource as resource
import txthings.coap as coap
from twisted.internet.task import LoopingCall

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

def update():
  updateWifi()
  updateResources()

class wirelessResource(resource.CoAPResource):
  isLeaf = True

  def __init__(self, itfc, idx):
    resource.CoAPResource.__init__(self)
    self.visible = True
    self.observable = True
    self.itfc = itfc
    self.idx = idx

  def render_GET(self, req):
    global wireless_stats
    vals = wireless_stats.get(self.itfc, None)
    if vals != None and len(vals) > idx:
      resp = coap.Message(code=coap.CONTENT, payload=vals[idx])
      return defer.succeed(resp)
    return defer.fail()

def init(config, root):
  global WIRELESS_FILE, wireless_resources
  interfaces = [ x.strip() for x in config.get('wireless', 'interfaces').split(',') ]
  value_strings = ['status', 'link', 'level', 'noise']
  rate = config.getfloat('wireless', 'rate')
  w = resource.CoAPResource()
  for itfc in interfaces:
    wi = resource.CoAPResource()
    for i,k in enumerate(value_strings):
      wireless_resources.append(wirelessResource(itfc, i))
      wi.putChild(k, wireless_resources[-1])
    w.putChild(itfc, wi)
  updateWifi()
  root.putChild('wireless', w)
  LoopingCall(update).start(rate)
