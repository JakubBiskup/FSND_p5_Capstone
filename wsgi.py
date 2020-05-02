import os
from app import create_app

app = create_app(database_path = os.environ['DATABASE_URL'])