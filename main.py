from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import date
from pydantic import BaseModel
from database import SessionLocal, Subscriber, Newsletter

app = FastAPI()

# Схеми даних для валідації
class SubscriberCreate(BaseModel):
    name: str
    email: str
    username: str
    password: str

class NewsletterCreate(BaseModel):
    topic: str
    content: str
    send_date: date

# Залежність для бази даних
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Виведення всіх передплатників
@app.get("/subscribers")
def get_subscribers(db: Session = Depends(get_db)):
    return db.query(Subscriber).all()

# Додавання передплатника
@app.post("/subscribers")
def add_subscriber(subscriber: SubscriberCreate, db: Session = Depends(get_db)):
    db_subscriber = Subscriber(**subscriber.dict())
    db.add(db_subscriber)
    db.commit()
    db.refresh(db_subscriber)
    return db_subscriber

# Видалення передплатника
@app.delete("/subscribers/{subscriber_id}")
def delete_subscriber(subscriber_id: int, db: Session = Depends(get_db)):
    subscriber = db.query(Subscriber).filter(Subscriber.id == subscriber_id).first()
    if not subscriber:
        raise HTTPException(status_code=404, detail="Subscriber not found")
    db.delete(subscriber)
    db.commit()
    return {"message": "Subscriber deleted"}

# Виведення всіх розсилок
@app.get("/newsletters")
def get_newsletters(db: Session = Depends(get_db)):
    return db.query(Newsletter).all()

# Додавання розсилки
@app.post("/newsletters")
def add_newsletter(newsletter: NewsletterCreate, db: Session = Depends(get_db)):
    db_newsletter = Newsletter(**newsletter.dict())
    db.add(db_newsletter)
    db.commit()
    db.refresh(db_newsletter)
    return db_newsletter

class SubscriberUpdate(BaseModel):
    name: str = None
    email: str = None
    username: str = None
    password: str = None

class NewsletterUpdate(BaseModel):
    topic: str = None
    content: str = None
    send_date: date = None

# Редагування передплатника
@app.put("/subscribers/{subscriber_id}")
def update_subscriber(subscriber_id: int, updates: SubscriberUpdate, db: Session = Depends(get_db)):
    subscriber = db.query(Subscriber).filter(Subscriber.id == subscriber_id).first()
    if not subscriber:
        raise HTTPException(status_code=404, detail="Subscriber not found")

    # Оновлюємо лише передані поля
    for key, value in updates.dict(exclude_unset=True).items():
        setattr(subscriber, key, value)

    db.commit()
    db.refresh(subscriber)
    return subscriber


# Редагування розсилки
@app.put("/newsletters/{newsletter_id}")
def update_newsletter(newsletter_id: int, updates: NewsletterUpdate, db: Session = Depends(get_db)):
    newsletter = db.query(Newsletter).filter(Newsletter.id == newsletter_id).first()
    if not newsletter:
        raise HTTPException(status_code=404, detail="Newsletter not found")

    # Оновлюємо лише передані поля
    for key, value in updates.dict(exclude_unset=True).items():
        setattr(newsletter, key, value)

    db.commit()
    db.refresh(newsletter)
    return newsletter
