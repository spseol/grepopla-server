from pony.orm.core import PrimaryKey, Required, Optional, Set, sql_debug

from datetime import datetime
from grepopla.model.database import db


class GameObject(db.Entity):
    _table_ = "game_object"
    id = PrimaryKey(int, auto=True)
    game = Required(lambda: Game)
    player = Required(lambda: Player)
    action = Optional(unicode, column="json", sql_type="json")


class Player(db.Entity):
    id = PrimaryKey(int, auto=True)
    nick = Required(unicode, lazy=False)
    color = Required(unicode, nullable=True)
    password = Optional(unicode, nullable=True)
    logs = Set(lambda: Log)
    games = Set(lambda: Game)
    game_objects = Set(GameObject)


class Game(db.Entity):
    id = PrimaryKey(int, auto=True)
    logs = Set(lambda: Log)
    players = Set(Player)
    objects = Set(GameObject)
    active = Required(bool)
    created = Required(datetime)


class Ship(db.GameObject):
    type = Required(lambda: ShipType)


class ShipType(db.Entity):
    _table_ = "ship_type"
    id = PrimaryKey(int, auto=True)
    ships = Set(Ship)
    size = Required(int)


class Planet(db.GameObject):
    pass


class Log(db.Entity):
    _table_ = "log"
    id = PrimaryKey(int, auto=True)
    received = Required(datetime)
    game = Required(Game)
    player = Optional(Player)


sql_debug(True)
db.generate_mapping(create_tables=True)