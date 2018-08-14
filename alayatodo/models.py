from alayatodo import orm as db
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base(db.engine)
db_session = db.session

def obj2dict(dbobj):
    d = {}
    for column in dbobj.__table__.columns:
        d[column.name] = str(getattr(dbobj, column.name))
    return d

class User(Base,db.Model):
    __tablename__ = 'users'
    __table_args__ = {'autoload': True }

class Todo(Base,db.Model):
    __tablename__ = 'todos' 
    __table_args__ = {'autoload': True }
