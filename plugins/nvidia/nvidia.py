import txthings.resource as resource
import txthings.coap as coap
import xml.etree.ElementTree as ET
from twisted.internet.task import LoopingCall
import subprocess

resources = []
smi_etree = None

def updateNVSMI():
  global smi_etree
  proc = subprocess.Popen(['nvidia-smi', '-q', '-x'], stdout=subprocess.PIPE)
  proc.wait()
  stdout, _ = proc.communicate()
  smi_etree = ET.fromstring(stdout)

def updateResources():
  global resources
  for r in resources:
    r.updatedState()

def update():
  updateNVSMI()
  updateResources()

class nvidiaResource(resource.CoAPResource):

  isLeaf = True

  def __init__(self, elemPath):
    resource.CoAPResource.__init__(self)
    self.visible = True
    self.observable = True
    self.elemPath = elemPath

  def render_GET(self, request):
    global smi_etree
    txt = smi_etree.find_text(self.elemPath)
    response = coap.Message(code=coap.CONTENT, payload=txt)
    return defer.succeed(response)

def init(config, root):
  global resources, smi_etree
  updateNVSMI()
  #idxs = [ x.strip() for x in config.get('nvidia', 'devices').split(',') ]
  nv = resource.CoAPResource()
  for idx in xrange(len(smi_etree.findall('gpu'))):
    idxr = resource.CoAPResource()
    resources.append(nvidiaResource("gpu[%d]/temperature/gpu_temp" % idx))
    idxr.putChild('temp', resources[-1])
    nv.putChild(str(idx), idxr)
  root.putChild('nvidia', nv)
  LoopingCall(update).start(config.getfloat('nvidia', 'rate'))
