from os import path

from pony.orm.core import db_session
from tornado.web import StaticFileHandler, url, Application

from grepopla.controllers.PlayerController import PlayerController
from grepopla.controllers.IndexController import IndexController
from grepopla.settings import PRODUCTION


app_params = [
    url(r'/', IndexController),
    url(r'/game', PlayerController),
    url(r'/static/(.*)', StaticFileHandler,
        {"path": ''.join((path.dirname(path.abspath(__file__)), '/grepopla/static/'))})
]
app = Application(app_params, debug=not PRODUCTION, compiled_template_cache=PRODUCTION,
                  static_hash_cache=PRODUCTION)


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
