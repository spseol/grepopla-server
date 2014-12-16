from logging import info

from pony.orm.core import select

from grepopla.model.entity import Player, Game


class GameController(object):
    clients = []

    def __init__(self, player, game):
        assert isinstance(player, Player)
        assert isinstance(game, Game)
        self.player = player
        self.game = game


    def process_game_message(self, message):
        info(message)


    def on_close(self, client):
        for ship in select(
                game_object for game_object in client.player.game_objects if game_object.game_object_type == "Ship"):
            print(ship.id)
            # destroy all players ships
            # set to free all player's planets
        self.game.players.remove(client.player)

    def other_clients(self):
        clients = self.clients[:]