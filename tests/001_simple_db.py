from random import randint

from pony.orm.core import db_session

from grepopla.model.entity import *
from datetime import datetime


@db_session
def db_test():
    p = Player(nick='{}'.format(randint(1000, 9999)), color='red', email='foobar@gmail.com')
    g = Game.get(id=1)
    if not g:
        g = Game(active=1, created=datetime.now())
    g.players.add(p)

    print 'players for game 0'
    for p in g.players:
        print '{} - nick {}'.format(p.id, p.nick)


db_test()


