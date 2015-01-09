from collections import defaultdict
from math import cos, sin
from logging import warning, info
from math import pi
from random import randint

from pony.orm.core import commit, select
from tornado.escape import to_basestring, json_encode

from datetime import datetime
from grepopla.model.entity import Player, Game, Planet, GameObject, Ship
from grepopla.settings import GAME_RESOLUTION, PRODUCTION
from grepopla.settings import GAME_WIDTH, GAME_HEIGHT


class GameController(object):
    clients = defaultdict(list)

    def __init__(self, player_controller, player, game):
        assert isinstance(player, Player)
        self.player = player
        assert isinstance(game, Game)
        self.game = game
        assert isinstance(player_controller, PlayerController)
        self.player_controller = player_controller

    def process_game_message(self, message):
        self.write_to_clients(message)
        if message.get("command", None) == "request" and message.get("entity", None) == "Ship":
            self.init_new_ship()
        if message['command'] == 'game' and message['nick'] == 'start':
            self.pre_start()

    def init_new_ship(self):
        ship = Ship()
        ship.player = self.player
        ship.game = self.game
        ship.size = 1
        commit()
        msg = {
            'command': 'init',
            'entity': "Ship",
            'id': ship.id,
            'owner_id': self.player.id,
            'values': {
                'x': randint(0, 400),
                'y': randint(0, 400),
                'size': 1
            }
        }
        self.write_to_clients(msg)

    def pre_start(self):
        start_msg = {'command': 'start', 'time': '10'}
        self.write_to_clients(start_msg, to_self=True)
        warning('Game {} with {} players starting'.format(self.game.id, len(self.game.players)))
        self.game.launched_at = datetime.now()
        commit()

        center = GAME_RESOLUTION[0] / 2, GAME_RESOLUTION[1] / 2
        step = 2 * pi / len(self.game.players)
        angle = 0
        for player in self.game.players:
            x = int(center[0] + cos(angle) * 2.0 / 3 * (GAME_WIDTH * 0.5))
            y = int(center[0] + sin(angle) * 2.0 / 3 * (GAME_HEIGHT * 0.5))
            size = randint(1, 10)
            angle += step
            planet = Planet(x=x, y=y, player=player, game=self.game, size=size)
            commit()
            info('New planet ({}) on ({}, {}) for player {}'.format(planet.id, x, y, to_basestring(player.nick)))
            # TODO: move message generating to common method
            init_msg = {
                'command': 'init',
                'entity': 'Planet',
                'id': planet.id,
                'values': {
                    'x': x,
                    'y': y,
                    'owner_id': player.id,
                    'size': size
                }
            }
            self.write_to_clients(init_msg)

    def on_close(self):
        for planet in GameObject.select(lambda g_o: g_o.player == self.player and g_o.game == self.game and g_o.game_object_type == "Planet")[:]:
            assert isinstance(planet, Planet)
            planet.player = None
            planet.is_free = 0
            warning('Planet {} setting to free.'.format(planet.id))
        self.game.players.remove(self.player)
        if not self.game.players:
            self.game.closed_at = datetime.now()
            info('Closing game {}'.format(self.game.id))
        commit()
        self.clients[self.game.id].remove(self.player_controller)

    @property
    def other_clients(self):
        clients = self.clients[self.game.id][:]
        clients.remove(self.player_controller)
        return clients

    def write_to_clients(self, message, to_self=True):
        if not PRODUCTION:
            info('To clients: {}'.format(json_encode(message)))
        clients = self.clients[self.game.id] if not to_self else self.other_clients
        for cl in clients:
            cl.write_message(message)


from grepopla.controllers.PlayerController import PlayerController