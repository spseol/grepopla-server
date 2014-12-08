from pony.orm.core import PrimaryKey, Required, Optional, Set, sql_debug

from grepopla.model.database import db


class GameObject(db):
    _table_ = "game_object"
    id = PrimaryKey(int, auto=True)
    game = Required("Game")
    player = Required("Player")
    action = Optional("Action")


class Player(db.Entity):
    id = PrimaryKey(int, auto=True)
    nick = Required(unicode, lazy=False)
    color = Required(unicode, nullable=True)
    games = Set("Game")
    objects = Set(GameObject)


class Game(db.Entity):
    id = PrimaryKey(int, auto=True)
    players = Set(Player)
    objects = Set(GameObject)
    active = Required(bool)


class Ship(db.GameObject):
    type = Required("ShipType")


class ShipType(db.Entity):
    _table_ = "ship_type"
    id = PrimaryKey(int, auto=True)
    ships = Set(Ship)
    size = Required(int)


class Planet(db.GameObject):
    pass


class Action(db.Entity):
    _table_ = "action"
    id = PrimaryKey(int, auto=True)
    game_object = Required(GameObject)
    action = Required(unicode, sql_type="json")


sql_debug(True)
db.generate_mapping(create_tables=True)