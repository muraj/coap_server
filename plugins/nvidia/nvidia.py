import xml.etree.ElementTree as ET
import asyncio
import asyncio.subprocess

import aiocoap.resource as resource
import aiocoap

resources = []
smi_etree = None

@asyncio.coroutine
def updateNVSMI():
  global smi_etree
  proc = yield from asyncio.create_subprocess_exec('nvidia-smi', '-q', '-x',
    stdout=asyncio.subprocess.PIPE)
  yield from proc.wait()
  data = yield from proc.stdout.read()
  smi_etree = ET.fromstring(data)

def updateResources():
  global resources
  for r in resources:
    r.updated_state()

@asyncio.coroutine
def update(rate):
  while 1:
    yield from updateNVSMI()
    updateResources()
    yield from asyncio.sleep(rate)

class nvidiaResource(resource.ObservableResource):

  def __init__(self, elemPath):
    super(nvidiaResource, self).__init__()
    self.elemPath = elemPath

  @asyncio.coroutine
  def render_GET(self, request):
    global smi_etree
    txt = smi_etree.findtext(self.elemPath).strip().encode('ascii')
    return aiocoap.Message(code=aiocoap.CONTENT, payload=txt)

def init(config, root):
  global resources, smi_etree
  asyncio.get_event_loop().run_until_complete(updateNVSMI())
  for idx in range(len(smi_etree.findall('gpu'))):
    resources.append(nvidiaResource("gpu[%d]/temperature/gpu_temp" % (idx+1)))
    root.add_resource(('nvidia', str(idx), 'temp'), resources[-1])
  rate = config.getfloat('nvidia', 'rate')
  asyncio.async(update(rate))
