#!/usr/bin/python
# -*- coding: utf-8 -*-

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref

db = create_engine('sqlite:///liturgy.sqlite', echo=False)
Session = sessionmaker(db)
Base = declarative_base(db)

class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True)
    class_type = Column(String, nullable=False)
    type = Column(Integer, nullable=True)
    priority = Column(Integer, nullable=True)
    title = Column(String, nullable=False)

    __mapper_args__ = {'polymorphic_on': class_type}

class FixedEvent(Event):
    __tablename__ = 'fixed_events'
    __mapper_args__ = {'polymorphic_identity': 'fixed'}

    id = Column(Integer, ForeignKey(Event.id), primary_key=True)
    day = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    season = Column(Integer, nullable=True)

class TimedEvent(Event):
    __tablename__ = 'timed_events'
    __mapper_args__ = {'polymorphic_identity': 'timed'}

    id = Column(Integer, ForeignKey(Event.id), primary_key=True)
    weekday = Column(Integer, nullable=False)
    week = Column(Integer, nullable=False)
    season = Column(Integer, nullable=False)

class MovableEvent(Event):
    __tablename__ = 'movable_events'
    __mapper_args__ = {'polymorphic_identity': 'movable'}

    id = Column(Integer, ForeignKey(Event.id), primary_key=True)
    calc_func = Column(String, nullable=False)

class Mass(Base):
    __tablename__ = 'masses'

    id = Column(Integer, primary_key=True)
    order = Column(Integer, nullable=False)
    event_id = Column(Integer, ForeignKey(Event.id), nullable=False)
    digit = Column(String, nullable=True)
    letter = Column(Integer, nullable=True)
    title = Column(String, nullable=True)

    event = relationship(Event,
                         backref=backref('masses', order_by=order))

class Reading(Base):
    __tablename__ = 'readings'

    id = Column(Integer, primary_key=True)
    order = Column(Integer, nullable=False)
    alt_num = Column(Integer, nullable=False)
    mass_id = Column(Integer, ForeignKey(Mass.id), nullable=False)
    title = Column(String, nullable=False)
    quote = Column(String, nullable=True)
    text = Column(String, nullable=True)
    quote_status = Column(String, nullable=False)
    text_status = Column(String, nullable=False)

    mass = relationship(Mass,
                        backref=backref('readings', order_by=order))

if __name__ == '__main__':
    Base.metadata.create_all()
