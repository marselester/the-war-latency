# coding: utf-8
from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import LineReceiver
from twisted.internet.defer import Deferred
from twisted.python import log


class PlayerProtocol(LineReceiver):

    def connectionMade(self):
        log.msg('Connected to server')
        self.factory.player_in(player=self)

    def lineReceived(self, line):
        log.msg('Received data from server')
        self.factory.server_sent_data(line)

    def connectionLost(self, reason):
        log.msg('Disconnected from server')
        self.factory.player_out()


class PlayerFactory(ClientFactory):

    protocol = PlayerProtocol

    def __init__(self):
        self.conn_d = Deferred()
        self.disconn_d = Deferred()
        self.recv_d_list = []
        self.player = None

    def player_in(self, player):
        self.player = player

        if self.conn_d is not None:
            d, self.conn_d = self.conn_d, None
            log.msg('Fire "connected" callback')
            d.callback(None)

    def player_out(self):
        if self.disconn_d is not None:
            d, self.disconn_d = self.disconn_d, None
            log.msg('Fire "disconnected" callback')
            d.callback(None)

        self.player = None

    def server_sent_data(self, line):
        log.msg('Server sent "{}"'.format(line))

        if self.recv_d_list:
            d = self.recv_d_list.pop(0)
            d.callback(line)

    def clientConnectionFailed(self, connector, reason):
        log.msg('Connection failed')
        if self.conn_d is not None:
            d, self.conn_d = self.conn_d, None
            log.msg('Fire "connected" errback')
            d.errback(reason)


def game(host='localhost', port=6666):
    from twisted.internet import reactor
    factory = PlayerFactory()
    reactor.connectTCP(host, port, factory)
    return factory
