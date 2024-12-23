import datetime

from sqlalchemy import create_engine, Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()

class Chapters(Base):    
    __tablename__ = 'Chapters'
    chapter_id = Column(Integer, primary_key=True, unique=True)
    title_id = Column(Integer, ForeignKey('Titles.title_id'), nullable=False)
    chapter = Column(Integer, nullable=False)  # Дробные главы можно сделать Float
    role_id = Column(Integer, ForeignKey('Roles.role_id'), nullable=False)
    workers_id = Column(Integer, ForeignKey('Workers.workers_id'), nullable=False)
    
    title = relationship('Titles', back_populates='chapters', foreign_keys=[title_id])
    role = relationship('Roles', back_populates='chapters')
    worker = relationship('Workers', back_populates='chapters')

    def __init__(self, title_id, chapter, role_id, workers_id):
        self.title_id = title_id
        self.chapter = chapter
        self.role_id = role_id
        self.workers_id = workers_id
    
    def __repr__(self):
        return f'<Chapter {self.chapter}>'

class Titles(Base):
    __tablename__ = 'Titles'
    title_id = Column(Integer, primary_key=True, unique=True)
    ru_name = Column(String, nullable=False)
    en_name = Column(String)
    jp_name = Column(String)
    last_chapter = Column(Integer, ForeignKey('Chapters.chapter_id'), nullable=True, default=None)  # Может быть NULL
    
    chapters = relationship('Chapters', back_populates='title', foreign_keys=[Chapters.title_id])

    def __init__(self, ru_name, en_name=None, jp_name=None, last_chapter=None):
        self.ru_name = ru_name
        self.en_name = en_name
        self.jp_name = jp_name
        self.last_chapter = last_chapter
    
    def __repr__(self):
        return f'<Title {self.ru_name}>'

class Roles(Base):
    __tablename__ = 'Roles'
    role_id = Column(Integer, primary_key=True, unique=True)
    role_name = Column(String, nullable=False)
    role_description = Column(String, nullable=True)

    chapters = relationship('Chapters', back_populates='role')

    def __init__(self, role_name, role_description=None):
        self.role_name = role_name
        self.role_description = role_description
    
    def __repr__(self):
        return f'<Role {self.role_name}>'

class Workers(Base):
    __tablename__ = 'Workers'
    workers_id = Column(Integer, primary_key=True, unique=True)
    nickname = Column(String, nullable=False)
    access_token = Column(String, nullable=True)
    discord_access_token = Column(String, nullable=False)
    discord_refresh_token = Column(String, nullable=False)
    discord_id = Column(Integer, nullable=False, unique=True)

    last_upload = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    chapters = relationship('Chapters', back_populates='worker')

    def __init__(self, nickname, access_token, discord_access_token, discord_refresh_token, discord_id):
        self.nickname = nickname
        self.access_token = access_token
        self.discord_access_token = discord_access_token
        self.discord_refresh_token = discord_refresh_token
        self.discord_id = discord_id
    
    def __repr__(self):
        return f'<Worker {self.nickname}>'

# Создание базы данных
engine = create_engine('sqlite:///manga.db')

# Настройка сессии
Session = sessionmaker(bind=engine)
session = Session()
