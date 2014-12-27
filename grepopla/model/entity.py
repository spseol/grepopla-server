from datetime import datetime

from pony.orm.core import PrimaryKey, Required, Optional, Set, Discriminator, sql_debug

from grepopla.model.database import db
from grepopla.settings import PRODUCTION


class GameObject(db.Entity):
    _table_ = "game_object"
    game_object_type = Discriminator(str)
    id = PrimaryKey(int, auto=True)
    game = Required("Game")
    player = Optional("Player")
    action = Optional(unicode)
    size = Required(int)


class Player(db.Entity):
    id = PrimaryKey(int, auto=True)
    nick = Required(unicode, lazy=False)
    color = Required(unicode)
    commands = Set("Command")
    games = Set("Game")
    game_objects = Set(GameObject)
    ip_address = Required(unicode)


class Game(db.Entity):
    id = PrimaryKey(int, auto=True)
    commands = Set("Command")
    players = Set(Player)
    objects = Set(GameObject)
    created_at = Optional(datetime)
    launched_at = Optional(datetime)
    closed_at = Optional(datetime)


class Ship(GameObject):
    pass


class Planet(GameObject):
    x = Required(int)
    y = Required(int)
    is_free = Optional(int)


class Command(db.Entity):
    _table_ = "log"
    id = PrimaryKey(int, auto=True)
    received = Required(datetime)
    game = Required(Game)
    player = Optional(Player)


sql_debug(not PRODUCTION)
db.generate_mapping(create_tables=True, check_tables=True)
db.check_tables()