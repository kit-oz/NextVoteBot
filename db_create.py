# -*- coding: utf-8 -*-

from model import engine, Base

Base.metadata.create_all(engine)
