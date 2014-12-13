import tornado.ioloop
import tornado.web
from tornado.websocket import WebSocketHandler


class Sockethandler(WebSocketHandler):
    def open(self):
        pass

    def on_close(self):
        pass

    def on_message(self, message):
        self.write_message(message)


application = tornado.web.Application([
    (r"/", Sockethandler),
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()