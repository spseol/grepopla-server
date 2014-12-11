from pony.orm.core import Database

from grepopla.settings import DATABASE


db = Database()
db.bind("postgres", **DATABASE)
