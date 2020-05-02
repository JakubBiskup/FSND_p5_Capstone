import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from app import create_app
from models import db

migrate = Migrate(create_app(test_config = None, database_path = os.environ['DATABASE_URL']), db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()