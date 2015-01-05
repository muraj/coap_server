#!/usr/bin/env python3
import os
import sys
import imp
import glob
import logging
import configparser

import asyncio

import aiocoap.resource as resource
import aiocoap

if __name__ == '__main__':

  logging.basicConfig(level=logging.INFO)
  logging.getLogger('coap-server').setLevel(logging.DEBUG)

  root = resource.Site()

  config = configparser.ConfigParser()
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
    logging.getLogger('coap-server').info("Loading plugin %s...", key)
    try:
      f, p, desc = imp.find_module(key, [pluginsDir + '/plugins'])
      module = imp.load_module(key, f, p, desc)
      init = getattr(module, 'init', None)
      if callable(init): init(config, root)
    except Exception as e:
      logging.getLogger('coap-server').error("Error loading plugin %s: %s", key, e)

  asyncio.async(aiocoap.Context.create_server_context(root))
  asyncio.get_event_loop().run_forever()
