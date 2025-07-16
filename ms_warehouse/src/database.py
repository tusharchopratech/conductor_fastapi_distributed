from sqlalchemy import create_engine, Column, String
from sqlalchemy.orm import sessionmaker, declarative_base

# Database Configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///./ms_warehouse.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#Base class for declarative models
Base = declarative_base()

# Database Model
class Product(Base):
    __tablename__ = "items"

    id = Column(String, primary_key=True)
    name = Column(String)
    status = Column(String)
    order_id = Column(String)

# Dependency to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create DB tables
Base.metadata.create_all(bind=engine)
