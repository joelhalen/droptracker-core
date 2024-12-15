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
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")

def get_current_partition() -> int:
    """
    Returns the naming scheme for a partition of drops
    Based on the current month
    """
    now = datetime.now()
    return now.year * 100 + now.month

# Setup database connection and create tables
engine = create_engine(f'mysql+pymysql://{DB_USER}:{DB_PASS}@localhost:3306/data', 
                      pool_size=20, max_overflow=10)
Base.metadata.create_all(engine)
Session = scoped_session(sessionmaker(bind=engine))
session = Session()