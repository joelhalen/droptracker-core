# models/base.py
from datetime import datetime
import pymysql
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os

pymysql.install_as_MySQLdb()
load_dotenv()

Base = declarative_base()
if os.getenv("mode") == "dev":
    DB_USER = os.getenv("DEV_DB_USER")
    DB_PASS = os.getenv("DEV_DB_PASSWORD")
    DB_HOST = os.getenv("DEV_DB_HOST")
    DB_PORT = os.getenv("DEV_DB_PORT")
else:
    DB_USER = os.getenv("DB_USER")
    DB_PASS = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")



# Setup database connection and create tables
engine = create_engine(f'mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/data', 
                      pool_size=20, max_overflow=10)
Base.metadata.create_all(engine)
Session = scoped_session(sessionmaker(bind=engine))
session = Session()