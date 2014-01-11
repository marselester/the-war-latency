# coding: utf-8
from twisted.trial.unittest import TestCase
from twisted.internet.defer import Deferred, DeferredList

from the_war_latency.protocols import WarFactory
from the_war_latency.models import Game
from . import client


def _dummy_deferred():
    d = Deferred()
    d.addCallback(lambda res: None)
    return d


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

    def test_it_is_ok_if_opponent_left_the_game(self):
        """Tests that client can continue to play when opponent has gone.

        Scenario:

        - 1st connected
        - 2nd connected
        - both have been getting countdown messages (game is going to start)
        - 1st disconnected
        - 2nd sent message when game is in progress
        - 2nd got congrats

        """
        cf_first = client.connected_client(port=self.portnum)
        cf_second = client.connected_client(port=self.portnum)

        d_c1_discon = Deferred()
        d_c1_discon.addCallback(
            lambda _: cf_first.player.transport.loseConnection()
        )

        cf_first.recv_d_list = [
            _dummy_deferred(),  # welcomed
            d_c1_discon,  # opponent is found
        ]

        def send_totem(number):
            cf_second.player.sendLine(Game.TOTEM)

        d_c2_totem = Deferred()
        d_c2_totem.addCallback(send_totem)

        def player_was_congratulated(message):
            expected_message = 'You won!'
            self.assertEqual(message, expected_message)

        d_c2_won = Deferred()
        d_c2_won.addCallback(player_was_congratulated)

        cf_second.recv_d_list = [
            _dummy_deferred(),  # welcomed
            _dummy_deferred(),  # opponent is found
            _dummy_deferred(),  # countdown 1
            _dummy_deferred(),  # countdown 2
            d_c2_totem,  # countdown 3
            d_c2_won,
        ]

        def results_of_deferreds_are_true(result):
            self.assertTrue(all(r[0] for r in result))

        d = DeferredList([d_c1_discon, d_c2_won])
        d.addCallback(results_of_deferreds_are_true)

        return d
