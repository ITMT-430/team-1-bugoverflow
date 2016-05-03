from flask import Flask
from flask.ext.alchemydumps import AlchemyDumps, AlchemyDumpsCommand
from flask.ext.script import Manager
from flask.ext.sqlalchemy import SQLAlchemy

from mydb import app, db
import sys

manager = Manager(app)

# init Alchemy Dumps
alchemydumps = AlchemyDumps(app, db)
manager.add_command('dump', AlchemyDumpsCommand)
manager.run()
