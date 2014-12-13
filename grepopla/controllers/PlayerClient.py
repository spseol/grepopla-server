from logging import error
from random import randint
from logging import info

from pony.orm.core import commit
from tornado.escape import json_decode
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

    def open(self):
        info('new WS')

    def on_message(self, message):
        info(message)
        try:
            message = json_decode(message)
        except ValueError:
            error("Message can't be decoded.")
            return

        command = message.get('command', None)
        command = command if command in MODES else None
        if not command and self.mode == MODE_GAME:
            self.process_game_message(message)
        elif command == MODE_LOGIN and self.mode == MODE_LOGIN:
            self.set_player(nick=message.get('nick', None))
            self.mode = MODE_SELECT
            self.send_game_select()
        elif command == MODE_SELECT and self.mode == MODE_SELECT:
            self.set_game(game_id=int(message.get('game_id', 0)))
            self.mode = MODE_GAME

    def process_game_message(self, message):
        assert isinstance(self.player, Player)
        assert isinstance(self.game, Game)

    def set_player(self, nick):
        p = Player.get(nick=nick)
        if not p:
            p = Player(nick=nick, color="%06x" % randint(0, 0xFFFFFF))
        self.player = p
        assert isinstance(self.player, Player)
        info(u'Player {} connected!'.format(self.player.nick.encode('utf8')))

    def set_game(self, game_id):
        assert isinstance(self.player, Player)
        g = Game.get(id=game_id)
        self.game = g
        assert isinstance(self.game, Game)
        commit()
        self.game.players.add(self.player)
        info(u'Player {} logged in game {}!'.format(self.player.nick.encode('utf8'), str(self.game.id)))

    def send_game_select(self):
        assert isinstance(self.player, Player)
        games = Game.select(lambda game: game.closed_at is None and game.launched_at is None).count()
        if not games:
            g = Game()
            g.created_at = datetime.now()
            info(u'Creating new game with id {}.'.format(g))
        games = Game.select(lambda game: game.closed_at is None and game.launched_at is None)
        games_select = {
            'games': [
                {'id': game.id,
                 'players': [player.nick for player in game.players]}
                for game in games]}

        self.write_message(games_select)