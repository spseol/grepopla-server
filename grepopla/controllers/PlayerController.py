from logging import warning
from random import randint
from logging import info

from pony.orm.core import commit
from tornado.escape import json_decode, to_basestring
from tornado.websocket import WebSocketHandler

from grepopla.model.entity import Player, Game
from datetime import datetime
from grepopla.settings import DEVELOPMENT


MODE_LOGIN = 'login'
MODE_SELECT = 'select'
MODE_GAME = 'game'
MODES = (MODE_LOGIN, MODE_SELECT, MODE_GAME)


class PlayerController(WebSocketHandler):
    def __init__(self, application, request, **kwargs):
        super(PlayerController, self).__init__(application, request, **kwargs)
        self.player = None
        self.game = None
        self.game_controller = None
        self.mode = MODE_LOGIN
        self.toggle_message_mode(MODE_LOGIN)

    def open(self):
        self.set_nodelay(True)
        if DEVELOPMENT:
            info('new WS')

    def on_close(self):
        if not self.mode == MODE_GAME:
            return
        warning(u'Player {} in game {} disconnected ({})'.format(to_basestring(self.player.nick), self.game.id,
                                                                 self.close_code))
        commit()

    def on_message(self, message):
        raise NotImplementedError

    def set_player(self, nick, ip_address):
        p = Player.get(nick=nick, ip_address=ip_address)
        if not p:
            p = Player(nick=nick, ip_address=ip_address, color="%06x" % randint(0, 0xFFFFFF))
        if p.games:
            self.write_message({'error': 1001})
            raise RuntimeWarning
        self.player = p
        assert isinstance(self.player, Player)
        info(u'Player {} connected!'.format(to_basestring(self.player.nick)))

    def set_game(self, game_id):
        assert isinstance(self.player, Player)
        g = Game.get(id=game_id)
        assert isinstance(g, Game)
        if g.launched_at is not None:
            self.write_message({'error': 1002})
            raise RuntimeWarning
        self.game = g
        assert isinstance(self.game, Game)
        self.game.players.add(self.player)
        commit()
        info(u'Player {} logged in game {}!'.format(to_basestring(self.player.nick), str(self.game.id)))

    def write_game_select(self):
        assert isinstance(self.player, Player)
        games = Game.select(lambda g: g.closed_at is None and g.launched_at is None).count()
        if not games:
            g = Game()
            g.created_at = datetime.now()
            info(u'Creating new game with id {}.'.format(g))
        commit()
        games = Game.select(lambda g: g.closed_at is None and g.launched_at is None)
        games_select = {
            'games': [
                {'id': game.id,
                 'players': [player.nick for player in game.players]}
                for game in games]}

        self.write_message(games_select)

    def toggle_message_mode(self, mode):
        if mode == MODE_GAME:
            self.on_message = self._on_game_message
        elif mode in (MODE_SELECT, MODE_LOGIN):
            self.on_message = self._on_command_message

    def _on_command_message(self, message):
        message = json_decode(message)

        command = message.get('command', None)
        command = command if command in MODES else None
        try:
            if command == MODE_LOGIN and self.mode == MODE_LOGIN:
                self.set_player(nick=message.get('nick', None), ip_address=self.request.remote_ip)
                self.mode = MODE_SELECT
                self.write_game_select()
            elif command == MODE_SELECT and self.mode == MODE_SELECT:
                self.set_game(game_id=int(message.get('game_id', 0)))
                self.mode = MODE_GAME
                self.toggle_message_mode(MODE_GAME)

                self.game_controller = GameController(self, self.player, self.game)
                GameController.clients.append(self)
            else:
                warning('Unknown command!')
        except RuntimeWarning as e:
            warning(e.message)

    def _on_game_message(self, message):
        message = json_decode(message)
        assert isinstance(self.player, Player)
        assert isinstance(self.game, Game)
        assert isinstance(self.game_controller, GameController)
        if DEVELOPMENT:
            info('Game message (player {} in game {}): {}'.format(to_basestring(self.player.nick), self.game.id,
                                                                  message))
        self.game_controller.process_game_message(message)

    def write_message(self, message, binary=False):
        if DEVELOPMENT:
            info('Sent WS message: {}'.format(message))
        return super(PlayerController, self).write_message(message, binary)


from grepopla.controllers.GameController import GameController
