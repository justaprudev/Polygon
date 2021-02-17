# This file is distributed as a part of the polygon project (justaprudev.github.io/polygon)
# By justaprudev

import json
from sqlalchemy import create_engine, Column, String, TypeDecorator
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from polygon.env import env

engine = create_engine(env.DATABASE_URL)
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
    name = Column(String(), primary_key=True)
    value = Column(Json())

    def __init__(self, name, value):
        self.name = name
        self.value = value


class Database:
    def __init__(self, session, engine, base):
        Variable.__table__.create(checkfirst=True)
        self.engine = engine
        self.session = session
        self.base = base

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
        self.session.add(Variable(name, value))
        self.session.commit()
        return True

    def update(self, data: dict) -> bool:
        for key, value in data.items():
            self.add(key, value)
        return True

    def remove(self, name: str) -> bool:
        variable = self.query(name)
        if variable:
            self.session.delete(variable)
            self.session.commit()
            return True
        return False

    def clear(self, members: list = None) -> bool:
        data = self.query()
        if data:
            for variable in data:
                if members and variable.name not in members:
                    continue
                self.session.delete(variable)
            self.session.commit()
            return True
        return False

    def query(self, name=None):
        query = self.session.query(Variable)
        results = query.filter_by(name=name).first() if name else query.all()
        self.session.close()
        return results


db = Database(session, engine, Base)
