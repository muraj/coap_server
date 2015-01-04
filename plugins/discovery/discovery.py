import txthings.resource as resource
import txthings.coap as coap

from twisted.internet import defer

class CoreResource(resource.CoAPResource):
  def __init__(self, root):
    resource.CoAPResource.__init__(self)
    self.root = root
  def render_GET(self, req):
    data = []
    self.root.generateResourceList(data, '')
    payload = ','.join(data)
    resp = coap.Message(code=coap.CONTENT, payload=payload)
    resp.opt.content_format = coap.media_types_rev['application/link-format']
    return defer.succeed(resp)

def init(config, root):
  well_known = resource.CoAPResource()
  core = CoreResource(root)
  well_known.putChild('core', core)
  root.putChild('.well-known', well_known)
