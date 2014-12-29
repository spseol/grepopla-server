from logging import warning
from random import randint

from tornado.escape import json_decode
import tornado.ioloop
import tornado.web
from tornado.web import RequestHandler
from tornado.websocket import WebSocketHandler


class SocketHandler(WebSocketHandler):
    clients = []
    messages = []
    _id = 0

    def open(self):
        self.nick = None
        self.clients.append(self)
        warning('WS opened!')

    def on_close(self):
        warning('WS closed')
        self.clients.remove(self)

    def on_message(self, message):
        message = json_decode(message)
        nick = message.get('nick', None)
        if nick:
            self.nick = nick

        for client in self.clients:
            assert isinstance(client, SocketHandler)
            client.write_message(message)

    @classmethod
    def init_game(cls):
        messages = []
        for cl in cls.clients:
            assert isinstance(cl, cls)
            player = cl.get_init_player_msg()
            planet = cls._get_new_entity('Planet', player['id'])
            ship = cls._get_new_entity('Ship', player['id'])
            messages.extend((player, planet, ship))

        for cl in cls.clients:
            assert isinstance(cl, cls)
            for msg in messages:
                cl.write_message(msg)

        return messages

    @classmethod
    def _get_new_entity(cls, entity, owner_id):
        cls._id += 1
        return {
            'command': 'init',
            'entity': str(entity),
            'id': cls._id,
            'owner_id': owner_id,
            'values': {
                'x': randint(0, 800),
                'y': randint(0, 400),
                'size': 1
            }
        }

    def get_init_player_msg(self):
        self._id += 1
        return {
            'command': 'init',
            'entity': 'Player',
            'id': self._id,
            'nick': self.nick
        }


class IndexHandler(RequestHandler):
    def get(self, *args, **kwargs):
        self.write('started with {}'.format(SocketHandler.init_game()))


application = tornado.web.Application([
    (r"/", SocketHandler),
    (r"/start", IndexHandler),
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()