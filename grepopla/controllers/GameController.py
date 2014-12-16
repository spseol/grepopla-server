from logging import info

from grepopla.model.entity import Player, Game


class GameController(object):
    clients = []

    def __init__(self, player_controller, player, game):
        assert isinstance(player, Player)
        assert isinstance(game, Game)
        assert isinstance(self.player_controller, PlayerController)
        self.player = player
        self.game = game
        self.player_controller = player_controller

    def process_game_message(self, message):
        info(message)

    def on_close(self, client):
        # for ship in select(
        # game_object for game_object in client.player.game_objects if game_object.game_object_type == "Ship"):
        #     print(ship.id)
            # destroy all players ships
            # set to free all player's planets
        self.game.players.remove(client.player)
        self.clients.remove(self.player_controller)

    def get_other_clients(self):
        clients = self.clients[:]
        clients.remove(self.player_controller)
        return clients

    def write_to_other_clients(self, message):
        for cl in self.get_other_clients():
            cl.write_message(message)


from grepopla.controllers.PlayerController import PlayerController