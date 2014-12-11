from pony.orm.core import Database

from grepopla.settings_default import DATABASE


db = Database("postgres", **DATABASE)