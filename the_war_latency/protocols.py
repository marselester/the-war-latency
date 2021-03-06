# coding: utf-8
from collections import deque

from twisted.internet.protocol import ServerFactory
from twisted.protocols.basic import LineReceiver
from twisted.python import log

from .models import Game


class WarProtocol(LineReceiver):

    def lineReceived(self, line):
        log.msg('{} sent data: "{}"'.format(self.addr, line))
        self.factory.player_sent_data(player=self, data=line)

    def connectionMade(self):
        log.msg('{} connected'.format(self.addr))
        self.factory.prepare_player(player=self)

    def connectionLost(self, reason):
        log.msg('{} disconnected'.format(self.addr))
        self.factory.destroy_player(player=self)

    @property
    def addr(self):
        peer = self.transport.getPeer()
        return '{host}:{port}'.format(
            host='lo' if peer.host == '127.0.0.1' else peer.host,
            port=peer.port,
        )


class WarFactory(ServerFactory):

    protocol = WarProtocol

    def __init__(self):
        self.user_wait_list = deque()
        self.game_list = deque()

    def player_sent_data(self, player, data):
        for game in self.game_list:
            if not game.is_over() and game.has_player(player):
                log.msg('User is a member of a game')
                d = game.next_step()
                d.callback((player, data))
                break
        else:
            log.msg('User is waiting for game to join')

    def prepare_player(self, player):
        player.sendLine('Hi! I am trying to find an opponent for you.')

        if self.user_wait_list:
            opponent = self.user_wait_list.popleft()
            game = Game(player, opponent)
            self.game_list.append(game)

            message = (
                'Opponent has been found. '
                'Wait until number "{number}" and send "{totem}" character.'
            ).format(number=game.NUMBER_TO_WAIT, totem=game.TOTEM)

            d = game.start()
            d.callback(message)
        else:
            self.user_wait_list.append(player)

    def destroy_player(self, player):
        try:
            # Removing is O(N), so maybe not to remove, and
            # only set to ``None``. But it requires storing player's
            # index of ``user_wait_list`` to get element by O(1).
            self.user_wait_list.remove(player)
        except ValueError:
            log.msg('User was not found in waiting list')
        else:
            log.msg('User was removed from waiting list')
        # Try to find player in games.
