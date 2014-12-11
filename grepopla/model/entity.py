from pony.orm.core import PrimaryKey, Required, Optional, Set, sql_debug, commit

from datetime import datetime
from grepopla.model.database import db
from grepopla.settings import DEVELOPMENT


class GameObject(db.Entity):
    _table_ = "game_object"
    id = PrimaryKey(int, auto=True)
    game = Required("Game")
    player = Required("Player")
    action = Optional(unicode, column="json")


class Player(db.Entity):
    id = PrimaryKey(int, auto=True)
    nick = Required(unicode, lazy=False)
    color = Required(unicode, nullable=True)
    password = Optional(unicode, nullable=True)
    commands = Set("Command")
    games = Set("Game")
    game_objects = Set(GameObject)
    email = Required(unicode)


class Game(db.Entity):
    id = PrimaryKey(int, auto=True)
    commands = Set("Command")
    players = Set(Player)
    objects = Set(GameObject)
    active = Required(int)
    created = Required(datetime)


class Ship(db.GameObject):
    type = Required("ShipType")


class ShipType(db.Entity):
    _table_ = "ship_type"
    id = PrimaryKey(int, auto=True)
    ships = Set(Ship)
    size = Required(int)


class Planet(db.GameObject):
    pass


class Command(db.Entity):
    _table_ = "log"
    id = PrimaryKey(int, auto=True)
    received = Required(datetime)
    game = Required(Game)
    player = Optional(Player)


sql_debug(DEVELOPMENT)
db.generate_mapping(create_tables=True, check_tables=True)
db.check_tables()