from os import path

from tornado.web import RequestHandler

from grepopla.controllers.GameController import GameController
from grepopla.model.entity import Game


class IndexController(RequestHandler):
    def get(self):
        games = Game.select(lambda game: game.closed_at is None and game.launched_at is None)
        tmpl_path = ''.join((path.dirname(path.abspath(__file__)), '/../templates/index.html'))
        self.render(tmpl_path, games=games)

    def post(self, *args, **kwargs):
        games = Game.select(lambda game: game.closed_at is None and game.launched_at is None)
        game_id = int(self.request.arguments["game-id"][0])
        msg = GameController.clients[game_id][0].game_controller.pre_start()
        tmpl_path = ''.join((path.dirname(path.abspath(__file__)), '/../templates/index.html'))
        self.render(tmpl_path, msg=u"Hra {} byla spustena s {}!".format(game_id, msg), games=games)
