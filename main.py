from os import path

from tornado import web, ioloop, options, autoreload

from tornado.web import StaticFileHandler, url

from grepopla.controllers.GameClient import GameClient

from grepopla.controllers.IndexController import IndexController
from grepopla.settings import DEVELOPMENT


app_params = [
    url(r'/', IndexController),
    url(r'/game', GameClient),
    url(r'/static/(.*)', StaticFileHandler,
        {"path": ''.join((path.dirname(path.abspath(__file__)), '/../templates/index.html'))})
]
app = web.Application(app_params, degug=DEVELOPMENT)

if __name__ == '__main__':
    options.parse_command_line()
    app.listen(8888)
    ioloop = ioloop.IOLoop().instance()
    autoreload.start(ioloop)
    ioloop.start()
