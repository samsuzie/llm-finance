from sqlalchemy import create_engine
# declarative_base is used to define tables in python using a base class
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,Session
from .config import settings
import logging


logger = logging.getLogger(__name__)

# engine is nothing but it is connecting our database to our python application

engine = create_engine(
    settings.DATABASE_URL,
    # ping checks if our database connection is still active or is there and if it is not there , it creates one
    pool_pre_ping=True,
    # after 300 seconds the database connection is closed
    pool_recycle=300,
    # controls logging, if it was true it will be printing every sql query in the console but since it is false it will keep the console clean
    echo=False
)
# session local class
SessionLocal = sessionmaker(autocommit = False,autoflush=False,bind=engine)

# base class
# declarative base :- special class that tells SQLAlchemy: that  any class i build from this is going to be a table in the database
Base = declarative_base()

def get_db()->Session:
    db = SessionLocal()
    try:
        # closing of the connection
        yield db 
    except Exception as e:
        logger.error(f"Database session error:{e}")
        db.rollback()
        raise
    finally:db.close()

def create_tables():
    """Create all tables in the database"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created sucessfully")
    except Exception as e:
        logger.error(f"Error creating database tables:{e}")
        raise


def drop_tables():
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info(f"Database tables dropped sucessfully")
    except Exception as e:
        logger.error(f"Error droping database tables:{e}")
        raise

