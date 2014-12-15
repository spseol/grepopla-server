from logging import warning
import logging
from random import randint
from logging import info

from pony.orm.core import commit, select
from tornado.escape import json_decode, to_basestring
from tornado.websocket import WebSocketHandler

from grepopla.model.entity import Player, Game
from datetime import datetime


MODE_LOGIN = 'login'
MODE_SELECT = 'select'
MODE_GAME = 'game'
MODES = (MODE_LOGIN, MODE_SELECT, MODE_GAME)


class PlayerClient(WebSocketHandler):
    def __init__(self, application, request, **kwargs):
        super(PlayerClient, self).__init__(application, request, **kwargs)
        self.player = None
        self.game = None
        self.mode = MODE_LOGIN
        self.toggle_message_mode(MODE_LOGIN)

    def open(self):
        self.set_nodelay(True)
        info('new WS')

    def on_close(self):
        if not self.mode == MODE_GAME:
            return
        warning(u'Player {} in game {} disconnected ({})'.format(to_basestring(self.player.nick), self.game.id,
                                                                 self.close_code))
        commit()
        for ship in select(
                game_object for game_object in self.player.game_objects if game_object.game_object_type == "Ship"):
            print(ship.id)
            # destroy all players ships
            # set to free all player's planets
        self.game.players.remove(self.player)

    def on_message(self, message):
        raise NotImplementedError

    def set_player(self, nick):
        p = Player.get(nick=nick)
        if not p:
            p = Player(nick=nick, color="%06x" % randint(0, 0xFFFFFF))
        if p.games:
            raise RuntimeWarning(u'Player {} is already in game!'.format(to_basestring(p.nick)))
        self.player = p
        assert isinstance(self.player, Player)
        info(u'Player {} connected!'.format(to_basestring(self.player.nick)))

    def set_game(self, game_id):
        assert isinstance(self.player, Player)
        g = Game.get(id=game_id)
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
        else:
            warning('Unknown game mode!')

    def _on_command_message(self, message):
        try:
            message = json_decode(message)
        except ValueError:
            warning("Message can't be decoded.")
            return

        command = message.get('command', None)
        command = command if command in MODES else None

        if command == MODE_LOGIN and self.mode == MODE_LOGIN:
            try:
                self.set_player(nick=message.get('nick', None))
                self.mode = MODE_SELECT
                self.write_game_select()
            except RuntimeWarning as e:
                warning(e.message)
        elif command == MODE_SELECT and self.mode == MODE_SELECT:
            self.set_game(game_id=int(message.get('game_id', 0)))
            self.mode = MODE_GAME
            self.toggle_message_mode(MODE_GAME)
        else:
            warning('Unknown command!')

    def _on_game_message(self, message):
        assert isinstance(self.player, Player)
        assert isinstance(self.game, Game)
        info('GM (player {} in game {}): {}'.format(to_basestring(self.player.nick), self.game.id, message))

    def write_message(self, message, binary=False):
        logging.error(message)
        return super(PlayerClient, self).write_message(message, binary)

