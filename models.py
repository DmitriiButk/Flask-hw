import os
import datetime
import atexit
from sqlalchemy import create_engine, String, DateTime, func
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, sessionmaker

POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'postgres')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
POSTGRES_HOST = os.getenv('POSTGRES_HOST', '127.0.0.1')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5431')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'db_postgres')

PG_DSN = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'

engine = create_engine(PG_DSN)
Session = sessionmaker(bind=engine)

atexit.register(engine.dispose)


class Base(DeclarativeBase):
    pass


class Announcement(Base):
    __tablename__ = 'Announcement'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(String(250), nullable=False)
    date_of_creation: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())
    owner: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    @property
    def dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'date_of_creation': self.date_of_creation.isoformat(),
            'owner': self.owner,
        }


Base.metadata.create_all(engine)
