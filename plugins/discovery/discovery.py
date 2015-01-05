import asyncio

import aiocoap.resource as resource
import aiocoap

class CoreResource(resource.Resource):

  def __init__(self, root):
    super(CoreResource, self).__init__()
    self.root = root

  @asyncio.coroutine
  def render_GET(self, req):
    data = []
    for uri, res in self.root._resources.items():
      opts = ['<' + '/'.join(uri) + '>']
      # Add more
      data.append(';'.join(opts))
    payload = ','.join(data).encode('utf-8')
    response = aiocoap.Message(code=aiocoap.CONTENT, payload=payload)
    response.opt.content_format = 40
    return response


def init(config, root):
  root.add_resource(('.well-known', 'core'), CoreResource(root))
