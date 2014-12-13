from logging import warning

import tornado.ioloop
import tornado.web
from tornado.websocket import WebSocketHandler


class Sockethandler(WebSocketHandler):
    def open(self):
        warning('new ws')

    def on_close(self):
        warning('new ws')

    def on_message(self, message):
        warning('new msg {}'.format(message))
        self.write_message(message)


application = tornado.web.Application([
    (r"/", Sockethandler),
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()