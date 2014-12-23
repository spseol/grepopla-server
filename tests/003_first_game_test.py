from logging import warning
from random import randint

import tornado.ioloop
import tornado.web
from tornado.websocket import WebSocketHandler


class Sockethandler(WebSocketHandler):
    clients = []
    _id = 0

    def open(self):
        self.clients.append(self)
        warning('WS opened!')
        self.init_test_game()

    def on_close(self):
        warning('WS closed')
        self.clients.remove(self)

    def on_message(self, message):
        warning('new msg {}'.format(message))

    def init_test_game(self):
        player1 = self._get_new_player(2)
        player2 = self._get_new_player(1)
        planet1 = self._get_new_entity('Planet', player1['id'])
        planet2 = self._get_new_entity('Planet', player2['id'])
        ship1 = self._get_new_entity('Ship', player1['id'])
        ship2 = self._get_new_entity('Ship', player2['id'])
        messages = (player1, player2, planet1, planet2, ship1, ship2)
        for msg in messages:
            self.write_message(msg)

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
        return super(Sockethandler, self).write_message(message, binary)


application = tornado.web.Application([
    (r"/", Sockethandler),
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()