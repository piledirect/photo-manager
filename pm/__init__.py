# encoding=utf-8

import os
import logging

import flask

import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

from elasticsearch_dsl.connections import connections

import redis as redispy

logging.basicConfig(format="%(asctime)s %(levelname)s: %(message)s", filename='flask.log', level=logging.DEBUG, datefmt='%Y-%m-%d %H:%M:%S')
logging.getLogger().addHandler(logging.StreamHandler())

app = flask.Flask(__name__)

app.config.from_object('pm.defaults')

if 'PM_CONFIG' in os.environ:
    app.config.from_envvar('PM_CONFIG')
else:
    app.config.from_object('pm.devconfig')


db_engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"], echo=False)
db = scoped_session(sessionmaker(bind=db_engine))
Base = declarative_base()
Base.query = db.query_property()

from . import models
from . import views
from . import api

@app.before_request
def configure_proxy():
    if app.config["USE_X_ACCEL"] is None:
        if "X-FORWARDED-FOR" in flask.request.headers:
            # should be harmless, even if not behind a proxy?
            app.config["USE_X_ACCEL"] = True
        else:
            app.config["USE_X_ACCEL"] = False

connections.create_connection(hosts=app.config["ELASTICSEARCH_HOSTS"], timeout=20)
redis = redispy.from_url(app.config["REDIS_URI"])
