# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from model import User
from config import SQLALCHEMY_DATABASE_URI

Base = declarative_base()

class Database:
    """
    Класс для обработки сессии SQLAlchemy.
    Так же включает в себя минимальный набор методов, вызываемых в управляющем классе.
    Названия методов говорящие.
    """
    def __init__(self):
        engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=False)

        Session = sessionmaker(bind=engine)
        self.session = Session()

    def add_user(self, user_data):
        user = User(user_data)
        self.session.add(user)
        self.session.commit()

    def get_user(self, user_id):
        return self.session.query(User).filter_by(id=user_id).first()
