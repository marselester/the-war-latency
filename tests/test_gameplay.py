# coding: utf-8
from twisted.trial.unittest import TestCase
from twisted.internet.defer import Deferred

from the_war_latency.protocols import WarFactory
from . import client


class WarServerTest(TestCase):

    def setUp(self):
        """Creates War server that listens on a random port."""
        from twisted.internet import reactor
        sf = WarFactory()
        self.listening_port = reactor.listenTCP(0, sf)
        self.portnum = self.listening_port.getHost().port

    def tearDown(self):
        port, self.listening_port = self.listening_port, None
        return port.stopListening()

    def test_get_welcome_message_after_connection_is_made(self):
        cf = client.connected_client(port=self.portnum)

        def player_was_welcomed(message):
            expected_message = 'Hi! I am trying to find an opponent for you.'
            self.assertEqual(message, expected_message)

        d = Deferred()
        d.addCallback(player_was_welcomed)
        d.addCallback(
            lambda _: cf.player.transport.loseConnection()
        )

        cf.recv_d_list.append(d)
        return d
