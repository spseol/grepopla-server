from hashlib import md5
from logging import warning
from random import randint
from logging import info
from datetime import datetime

from tornado.escape import json_decode, to_basestring, json_encode
from tornado.websocket import WebSocketHandler

from pony.orm.core import commit, exists
from grepopla.model.entity import Player, Game
from grepopla.settings import PRODUCTION, SKIP_AUTHENTICATION, SKIP_GAME_SELECT


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
        self.on_message = self.on_message

    def open(self):
        self.set_nodelay(True)
        if not PRODUCTION:
            info('new WS from {}'.format(self.request.remote_ip))
        if SKIP_AUTHENTICATION:
            ip = self.request.remote_ip
            nick = md5(ip).hexdigest()[:10]

            self.set_player(nick, ip)
            game_select = self.get_game_select()
            game_id = game_select['games'][0]['id']
            self.set_game(game_id=game_id)
            self.toggle_message_mode(MODE_GAME)
            self.set_game_controller()

    def on_close(self):
        if not self.mode == MODE_GAME:
            return
        assert isinstance(self.game_controller, GameController)
        self.game_controller.on_close()
        warning(u'Player {} in game {} disconnected ({})'.format(to_basestring(self.player.nick), self.game.id,
                                                                 self.close_code))
        commit()

    def on_message(self, message):
        raise NotImplementedError

    def set_player(self, nick, ip_address):
        p = Player.get(nick=nick, ip_address=ip_address)
        if not p:
            p = Player(nick=nick, ip_address=ip_address, color="%06x" % randint(0, 0xFFFFFF))
        if Game.exists(lambda g: p in g.players and g.closed_at is None):
            self.write_message({'error': 1001})
            raise RuntimeWarning('Player is already in game.')
        self.player = p
        assert isinstance(self.player, Player)
        info(u'Player {} connected!'.format(to_basestring(self.player.nick)))

    def force_set_game(self):
        game_select = self.get_game_select()
        game_id = game_select["games"][0]["id"]
        self.set_game(game_id)
        self.toggle_message_mode(MODE_GAME)
        self.set_game_controller()

    def set_game(self, game_id):
        assert isinstance(self.player, Player)
        g = Game.get(id=game_id)
        assert isinstance(g, Game)
        if g.launched_at is not None:
            self.write_message({'error': 1002})
            raise RuntimeWarning('This game is already launched.')
        self.game = g
        assert isinstance(self.game, Game)
        self.game.players.add(self.player)
        commit()
        info(u'Player {} logged in game {}!'.format(to_basestring(self.player.nick), str(self.game.id)))

    def set_game_controller(self):
        assert isinstance(self.player, Player)
        assert isinstance(self.game, Game)
        self.game_controller = GameController(self, self.player, self.game)
        GameController.clients[self.game.id].append(self)

    def get_game_select(self):
        assert isinstance(self.player, Player)
        games = Game.select(lambda game: game.closed_at is None and game.launched_at is None)
        if not games.count():
            g = Game()
            g.created_at = datetime.now()
            info(u'Creating new game with id {}.'.format(g))
            commit()
        games_select = {
            'games': [
                {'id': game.id,
                 'players': [player.nick for player in game.players]}
                for game in games]}

        return games_select

    def toggle_message_mode(self, mode):
        self.mode = mode
        if mode == MODE_GAME:
            self.on_message = self._on_game_message
        elif mode in (MODE_SELECT, MODE_LOGIN):
            self.on_message = self._on_command_message

    def _on_command_message(self, message):
        message = json_decode(message)
        command = message.get('command', None)
        if message.get("nick", None):
            command = MODE_LOGIN
        command = command if command in MODES else None
        try:
            if command == MODE_LOGIN and self.mode == MODE_LOGIN:
                self.set_player(nick=message.get('nick', None), ip_address=self.request.remote_ip)
                self.mode = MODE_SELECT
                if SKIP_GAME_SELECT:
                    self.force_set_game()
                else:
                    self.write_message(self.get_game_select())
            elif command == MODE_SELECT and self.mode == MODE_SELECT:
                self.set_game(game_id=int(message.get('game_id', 0)))
                self.toggle_message_mode(MODE_GAME)
                self.set_game_controller()
            else:
                warning('Unknown command!')
        except RuntimeWarning as e:
            warning(e.message)

    def _on_game_message(self, message):
        message = json_decode(message)
        assert isinstance(self.player, Player)
        assert isinstance(self.game, Game)
        assert isinstance(self.game_controller, GameController)
        if not PRODUCTION:
            info('Game message (player {} in game {}): {}'.format(to_basestring(self.player.nick), self.game.id,
                                                                  to_basestring(json_encode(message))))
        self.game_controller.process_game_message(message)

    def write_message(self, message, binary=False):
        return super(PlayerController, self).write_message(message, binary)


from grepopla.controllers.GameController import GameController
