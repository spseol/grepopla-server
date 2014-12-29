from logging import warning, info
from random import randint

import tornado.ioloop
import tornado.web
from tornado.websocket import WebSocketHandler


class SocketHandler(WebSocketHandler):
    clients = []
    _id = 0

    def open(self):
        self.clients.append(self)
        warning('WS opened!')
        if not self.messages:
            self.init_init_messages()
        for msg in self.messages:
            self.write_message(msg)

    def on_close(self):
        warning('WS closed')
        self.clients.remove(self)

    def on_message(self, message):
        info('MSG: {}'.format(message))
        for client in self.clients:
            assert isinstance(client, SocketHandler)
            client.write_message(message)

    def init_init_messages(self):
        player1 = self._get_new_player(2)
        player2 = self._get_new_player(1)
        planet1 = self._get_new_entity('Planet', player1['id'])
        planet2 = self._get_new_entity('Planet', player2['id'])
        ship1 = self._get_new_entity('Ship', player1['id'])
        ship2 = self._get_new_entity('Ship', player2['id'])
        self.messages = (player1, player2, planet1, planet2, ship1, ship2)

    def _get_new_entity(self, entity, owner_id):
        self._id += 1
        return {
            'command': 'init',
            'entity': str(entity),
            'id': self._id,
            'owner_id': owner_id,
            'values': {
                'x': randint(0, 800),
                'y': randint(0, 400),
                'size': 1
            }
        }

    def _get_new_player(self, enemy_id):
        self._id += 1
        return {
            'command': 'init',
            'entity': 'Player',
            'id': self._id,
            'enemy_id': enemy_id
        }

    def write_message(self, message, binary=False):
        warning(str(message))
        return super(SocketHandler, self).write_message(message, binary)


application = tornado.web.Application([
    (r"/", SocketHandler),
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()