# coding=utf-8

from sqlalchemy_wrapper import SQLAlchemy

from config import DATABASE_URL

db = SQLAlchemy(DATABASE_URL)
