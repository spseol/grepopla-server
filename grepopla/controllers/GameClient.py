from logging import error
from random import randint

from pony.orm.core import db_session, commit
from tornado.escape import json_decode
from tornado.gen import coroutine
from tornado.websocket import WebSocketHandler

from grepopla.model.entity import Player, Game


MODE_LOGIN = 'login'
MODE_SELECT = 'select'
MODE_GAME = 'game'
MODES = (MODE_LOGIN, MODE_SELECT, MODE_GAME)


class GameClient(WebSocketHandler):
    def __init__(self, application, request, **kwargs):
        super(GameClient, self).__init__(application, request, **kwargs)
        self.player = None
        self.game = None
        self.mode = MODE_LOGIN

    def open(self):
        pass

    def on_message(self, message):
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
        elif command == MODE_SELECT and self.mode == MODE_SELECT:
            self.set_game(game_id=message.get('game_id', None))

    def process_game_message(self, message):
        assert isinstance(self.player, Player)
        assert isinstance(self.game, Game)

    @coroutine
    @db_session
    def set_player(self, nick):
        p = Player.get(nick=nick)
        if not p:
            p = Player(nick=nick, color="%06x" % randint(0, 0xFFFFFF))
        yield commit()
        assert isinstance(self.player, Player)
        self.player = p

    def set_game(self, game_id):
        assert isinstance(self.player, Player)

    def send_game_select(self):
        pass