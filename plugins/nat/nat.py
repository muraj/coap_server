import asyncio

import aiocoap.resource as resource
import aiocoap

import logging

class NatRegResource(resource.ObservableResource):

  def __init__(self, rate):
    super(NatRegResource, self).__init__()
    self.notify(rate)

  def notify(self, rate):
    self.updated_state()
    asyncio.get_event_loop().call_later(rate, self.notify, rate)

  @asyncio.coroutine
  def render_GET(self, request):
    return aiocoap.Message(code=aiocoap.CONTENT, payload=b'')

  #@asyncio.coroutine
  #def add_observation(self, request, serverobservation):
  #  self._observations.add(serverobservation)
  #  logging.debug('accept observations=%d', len(self._observations))
  #  def cancelcb():
  #    logging.debug('cancel observations=%d', len(self._observations))
  #    self._observations.remove(serverobservation)
  #  serverobservation.accept(cancelcb)

def init(config, root):
  #if config.has_section('nat.client'):
  #  natClientReg(config.get('nat.client', 'uri'))
  if config.has_section('nat.server'):
    rate = config.getfloat('nat.server', 'rate')
    root.add_resource(('nat', 'reg'), NatRegResource(rate))
