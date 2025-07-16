from contextlib import contextmanager
from sqlalchemy.orm import Session
from ..core.database import SessionLocal
import logging

logger = logging.getLogger(__name__)

@contextmanager
def get_db():
    """context manager for databse sessions"""
    db=SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        logger.error(f"Database error:{e}")
        db.rollback()
        raise
    finally:
        db.close()

def get_db_session()->Session:
    """Get a database session(for dependency injection)"""
    return SessionLocal()
