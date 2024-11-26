from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Date, ForeignKey, create_engine
from sqlalchemy.orm import relationship, declarative_base, sessionmaker, Session
import datetime

app = FastAPI()

# База даних
DATABASE_URL = "sqlite:///./newsletter.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Моделі бази даних
class Subscriber(Base):
    __tablename__ = "subscribers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    account = Column(String, unique=True)
    password = Column(String)

class Newsletter(Base):
    __tablename__ = "newsletters"
    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String, index=True)
    content = Column(String)
    send_date = Column(Date)
    subscriber_id = Column(Integer, ForeignKey("subscribers.id"))
    subscriber = relationship("Subscriber")

# Ініціалізація бази даних
Base.metadata.create_all(bind=engine)

# Моделі запитів/відповідей
class SubscriberCreate(BaseModel):
    name: str
    email: str
    account: str
    password: str

class SubscriberUpdate(BaseModel):
    name: str = None
    email: str = None
    account: str = None
    password: str = None

class NewsletterCreate(BaseModel):
    topic: str
    content: str
    send_date: datetime.date
    subscriber_id: int

class NewsletterUpdate(BaseModel):
    topic: str = None
    content: str = None
    send_date: datetime.date = None

# CRUD функції
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Маршрути для передплатників
@app.post("/subscribers/")
def create_subscriber(subscriber: SubscriberCreate, db: Session = Depends(get_db)):
    try:
        db_subscriber = Subscriber(
            name=subscriber.name,
            email=subscriber.email,
            account=subscriber.account,
            password=subscriber.password
        )
        db.add(db_subscriber)
        db.commit()
        db.refresh(db_subscriber)
        return {"message": "Subscriber created successfully", "subscriber": db_subscriber}
    except Exception as e:
        db.rollback()  # Важливо, щоб скасувати зміни в разі помилки
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.get("/subscribers/")
def list_subscribers(db: Session = Depends(get_db)):
    return db.query(Subscriber).all()

@app.put("/subscribers/{subscriber_id}")
def update_subscriber(subscriber_id: int, subscriber: SubscriberUpdate, db: Session = Depends(get_db)):
    db_subscriber = db.query(Subscriber).filter(Subscriber.id == subscriber_id).first()
    if not db_subscriber:
        raise HTTPException(status_code=404, detail="Subscriber not found")
    for key, value in subscriber.dict(exclude_unset=True).items():
        setattr(db_subscriber, key, value)
    db.commit()
    db.refresh(db_subscriber)
    return db_subscriber

@app.delete("/subscribers/{subscriber_id}")
def delete_subscriber(subscriber_id: int, db: Session = Depends(get_db)):
    db_subscriber = db.query(Subscriber).filter(Subscriber.id == subscriber_id).first()
    if not db_subscriber:
        raise HTTPException(status_code=404, detail="Subscriber not found")
    db.delete(db_subscriber)
    db.commit()
    return {"message": "Subscriber deleted"}

# Маршрути для розсилок
@app.post("/newsletters/")
def create_newsletter(newsletter: NewsletterCreate, db: Session = Depends(get_db)):
    db_newsletter = Newsletter(**newsletter.dict())
    db.add(db_newsletter)
    db.commit()
    db.refresh(db_newsletter)
    return db_newsletter

@app.get("/newsletters/")
def list_newsletters(db: Session = Depends(get_db)):
    return db.query(Newsletter).all()

@app.put("/newsletters/{newsletter_id}")
def update_newsletter(newsletter_id: int, newsletter: NewsletterUpdate, db: Session = Depends(get_db)):
    db_newsletter = db.query(Newsletter).filter(Newsletter.id == newsletter_id).first()
    if not db_newsletter:
        raise HTTPException(status_code=404, detail="Newsletter not found")
    for key, value in newsletter.dict(exclude_unset=True).items():
        setattr(db_newsletter, key, value)
    db.commit()
    db.refresh(db_newsletter)
    return db_newsletter

@app.delete("/newsletters/{newsletter_id}")
def delete_newsletter(newsletter_id: int, db: Session = Depends(get_db)):
    newsletter = db.query(Newsletter).filter(Newsletter.id == newsletter_id).first()
    if not newsletter:
        raise HTTPException(status_code=404, detail="Newsletter not found")
    db.delete(newsletter)
    db.commit()
    return {"message": "Newsletter deleted"}
