from collections import defaultdict
from math import cos, sin
from logging import warning, info
from math import pi
from random import randint

from pony.orm.core import commit, select
from tornado.escape import to_basestring, json_encode

from datetime import datetime
from grepopla.model.entity import Player, Game, Planet, GameObject
from grepopla.settings import GAME_RESOLUTION, PRODUCTION
from grepopla.settings import GAME_WIDTH, GAME_HEIGHT


class GameController(object):
    clients = defaultdict(list)

    def __init__(self, player_controller, player, game):
        assert isinstance(player, Player)
        assert isinstance(game, Game)
        assert isinstance(player_controller, PlayerController)
        self.player = player
        self.game = game
        self.player_controller = player_controller

    def process_game_message(self, message):
        self.write_to_clients(message)
        if message['command'] == 'game' and message['nick'] == 'start':
            self.pre_start()

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

    def on_close(self, client):
        assert isinstance(client, PlayerController)
        for planet in select(g_o for g_o in client.player.game_objects if g_o.game_object_type == "Planet"):
            assert isinstance(planet, Planet)
            planet.player = None
            planet.is_free = True
            warning('Planet {} setting to free.'.format(planet.id))
        self.game.players.remove(client.player)
        if not self.game.players:
            self.game.closed_at = datetime.now()
            info('Closing game {}'.format(self.game.id))
        commit()
        self.clients[self.game.id].remove(self.player_controller)

    def get_other_clients(self):
        clients = self.clients[self.game.id][:]
        clients.remove(self.player_controller)
        return clients

    def write_to_clients(self, message, to_self=False):
        if not PRODUCTION:
            info('To clients: {}'.format(json_encode(message)))
        clients = self.clients[self.game.id] if not to_self else self.get_other_clients()
        for cl in clients:
            cl.write_message(message)


from grepopla.controllers.PlayerController import PlayerController