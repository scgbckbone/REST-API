from app_alchemy import app
from object_SQLAlchemy import db

db.init_app(app)

@app.before_first_request
def create_tables():
    db.create_all()
