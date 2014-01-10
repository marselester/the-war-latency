# coding: utf-8
import random

from twisted.internet.defer import Deferred


class Game(object):
    """Represents the game between particular players.

    Available states:

    - **wait** - game is waiting for randomly slow countdown messages;
    - **play** - game is ready for accept players' actions;
    - **over** - game is over.

    """

    NUMBER_TO_WAIT = 10
    TOTEM = 'a'

    WAIT_STATE = 'wait'
    PLAY_STATE = 'play'
    END_STATE = 'over'

    def __init__(self, *args):
        self.player_list = set(args)
        self.state = self.WAIT_STATE

    def is_over(self):
        return self.state == self.END_STATE

    def has_player(self, player):
        return player in self.player_list

    def start(self):
        d = Deferred()
        d.addCallback(self._notify_players)
        self._add_broadcast_messaging_to_deferred(
            deferred=d,
            message_list=(str(n) for n in xrange(1, self.NUMBER_TO_WAIT + 1)),
        )
        d.addCallback(self._ch_state_to_play)
        return d

    def next_step(self):
        """Returns deferred that concerns about game rules."""
        d = Deferred()
        d.addCallback(self._judge)
        d.addCallback(self._notify_winner_and_losers_about_end)
        d.addBoth(self._clean_up)
        return d

    def _add_broadcast_messaging_to_deferred(self, deferred, message_list):
        for message in message_list:
            deferred.addCallback(self._slow_broadcast_message, message)

    def _slow_broadcast_message(self, _, message):
        d = Deferred()
        d.addCallback(self._notify_players)
        delay = random.randint(2, 4)

        from twisted.internet import reactor
        reactor.callLater(delay, d.callback, message)

        return d

    def _ch_state_to_play(self, _):
        self.state = self.PLAY_STATE

    def _notify_players(self, message):
        for player in self.player_list:
            player.sendLine(message)

    def _judge(self, player_and_data):
        """Judges the game and returns the winner.

        It considers incoming data only if game is in progress.

        """
        if self.state != self.PLAY_STATE:
            return
        player, data = player_and_data
        if data == self.TOTEM:
            self.state = self.END_STATE
            return player

    def _notify_winner_and_losers_about_end(self, winner):
        if not winner:
            return
        winner.sendLine('You won!')

        for player in self.player_list:
            if player != winner:
                player.sendLine('You lost!')

    def _clean_up(self, _):
        if self.is_over():
            for player in self.player_list:
                player.transport.loseConnection()
            self.player_list = set()
