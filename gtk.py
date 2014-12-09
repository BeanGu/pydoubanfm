#!/usr/bin/env python
from twisted.internet import gtk3reactor
gtk3reactor.install()
from twisted.internet.protocol import ClientFactory
from twisted.internet import reactor
from gtk import Protocol
from utils import setting, reload_sys


class Factory(ClientFactory):
    def buildProtocol(self, addr):
        return Protocol()

if __name__ == '__main__':
    reload_sys()
    reactor.connectTCP('127.0.0.1', setting.get('port'), Factory())
    reactor.run()
