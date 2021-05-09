# This file is distributed as a part of the polygon project (justaprudev.github.io/polygon)
# By justaprudev

import json
from urllib.parse import urlparse
from sqlalchemy import create_engine, Column, String, TypeDecorator
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import sessionmaker
from .util import dotdict
from .env import env

dburl = urlparse(env.DATABASE_URL)
if dburl.scheme == "postgres":
    dburl = dburl._replace(scheme="postgresql")  # SQLAlchemy v1.4+

engine = create_engine(dburl.geturl())
Base = declarative_base(bind=engine)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine, autoflush=False)
session = Session()


class Json(TypeDecorator):
    impl = String

    def process_bind_param(self, value, dialect):
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        return json.loads(value)


class Variable(Base):
    __tablename__ = "variables"
    name = Column(String, primary_key=True)
    value = Column(Json)


class Database:
    def __init__(self):
        Variable.__table__.create(checkfirst=True)
        self.debug = dotdict(session=session, engine=engine, variable_cls=Variable, base_cls=Base)

    def exists(self, name: str):
        return bool(self.query(name))

    def get(self, name: str, default=None):
        variable = self.query(name)
        return variable.value if variable else default

    def dump(self) -> dict:
        return {variable.name: variable.value for variable in self.query()}

    def add(self, name: str, value, overwrite=True) -> bool:
        variable = self.query(name)
        if variable:
            if not overwrite:
                return False
            self.remove(name)
        session.add(Variable(name=name, value=value))
        session.commit()
        return True

    def update(self, data: dict) -> bool:
        for key, value in data.items():
            self.add(key, value)
        return True

    def remove(self, name: str) -> bool:
        variable = self.query(name)
        if variable:
            session.delete(variable)
            session.commit()
            return True
        return False

    def clear(self, members: tuple = None) -> bool:
        data = self.query()
        members = members or [entry.name for entry in data]
        for entry in data:
            if entry.name in members:
                session.delete(variable)
        session.commit()
        return bool(data)

    def query(self, name: str = None):
        query = session.query(Variable)
        results = query.filter_by(name=name).first() if name else query.all()
        session.close()
        return results


db = Database()
