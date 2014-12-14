from os import path

from pony.orm.core import db_session
from tornado.web import StaticFileHandler, url, Application

from grepopla.controllers.PlayerClient import PlayerClient
from grepopla.controllers.IndexController import IndexController
from grepopla.settings import DEVELOPMENT


app_params = [
    url(r'/', IndexController),
    url(r'/game', PlayerClient),
    url(r'/static/(.*)', StaticFileHandler,
        {"path": ''.join((path.dirname(path.abspath(__file__)), '/../templates/index.html'))})
]
app = Application(app_params, degug=DEVELOPMENT, compiled_template_cache=not DEVELOPMENT,
                  static_hash_cache=not DEVELOPMENT)


@db_session
def start():
    from tornado import ioloop, options, autoreload

    options.parse_command_line()
    app.listen(8888)
    ioloop = ioloop.IOLoop().instance()
    autoreload.start(ioloop)
    ioloop.start()


if __name__ == '__main__':
    start()
