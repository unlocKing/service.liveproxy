#!/usr/bin/env python
# -*- coding: utf-8 -*-
import errno
import logging
import sys

from liveproxy.shared import (
    check_root,
    check_streamlink_version,
    log_current_versions,
    setup_logging,
)
from liveproxy.server import (
    HTTPRequest,
    ThreadedHTTPServer,
)

import xbmc
import xbmcaddon

__addon__ = xbmcaddon.Addon(id='service.liveproxy')
__template = 'service.liveproxy: {0}'

log = logging.getLogger('streamlink.liveproxy-service')


def main():
    try:
        import Cryptodome
        sys.modules['Crypto'] = Cryptodome
    except ImportError:
        pass

    setup_logging()

    check_root()
    log_current_versions()
    check_streamlink_version()

    HOST = '0.0.0.0'
    PORT = int(__addon__.getSetting('listen_port'))

    log.info('Starting server: {0} on port {1}'.format(HOST, PORT))

    sys.stderr = sys.stdout
    server_class = ThreadedHTTPServer
    server_class.allow_reuse_address = True
    try:
        httpd = server_class((HOST, PORT), HTTPRequest)
    except OSError as err:
        if err.errno == errno.EADDRINUSE:
            log.error('Could not listen on port {0}! Exiting...'.format(PORT))
            sys.exit(errno.EADDRINUSE)
        log.error('Error {0}! Exiting...'.format(err.errno))
        sys.exit(err.errno)

    monitor = xbmc.Monitor()
    while not monitor.abortRequested():
        httpd.handle_request()
        if monitor.waitForAbort(1):
            break

    log.info('Closing server {0} on port {1} ...'.format(HOST, PORT))
    httpd.shutdown()
    httpd.server_close()
