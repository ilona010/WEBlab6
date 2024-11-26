from sqlalchemy import Column, Integer, String, Date, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

# Модель бази даних
class Subscriber(Base):
    __tablename__ = "subscribers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

class Newsletter(Base):
    __tablename__ = "newsletters"
    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String, nullable=False)
    content = Column(String, nullable=False)
    send_date = Column(Date, nullable=False)

# Підключення до SQLite
DATABASE_URL = "sqlite:///./newsletter.db"
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
