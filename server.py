#!/usr/bin/env python2
import os
import sys
import imp
import glob
import ConfigParser
import datetime

from twisted.internet import defer
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from twisted.python import log

import txthings.resource as resource
import txthings.coap as coap

# Resource tree creation
if __name__ == '__main__':
  log.startLogging(sys.stdout)
  root = resource.CoAPResource()

  config = ConfigParser.ConfigParser()
  defaultCfg = os.path.expanduser('~/.config/coap')
  if not os.path.exists(defaultCfg):
    os.mkdir(defaultCfg)
  config.read(['default.cfg', defaultCfg + '/config.cfg'])

  pluginsDir = os.path.dirname(os.path.realpath(__file__))
  for plugin in glob.glob(pluginsDir + '/plugins/*/'):
    key = os.path.basename(os.path.dirname(plugin))
    if not config.has_section(key): continue
    if not config.has_option(key, 'enable'): continue
    if not config.getboolean(key, 'enable'): continue
    log.msg("Loading plugin %s..." % key)
    try:
      f, p, desc = imp.find_module(key, [pluginsDir + '/plugins'])
      module = imp.load_module(key, f, p, desc)
      init = getattr(module, 'init', None)
      if callable(init): init(config, root)
    except:
      log.err()

  endpoint = resource.Endpoint(root)
  reactor.listenUDP(coap.COAP_PORT, coap.Coap(endpoint)) #, interface="::")
  reactor.run()
