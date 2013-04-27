#!/usr/bin/python
# -*- coding: utf-8 -*-

from sqlalchemy import create_engine, Column, Integer, String, Unicode, UnicodeText, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref

db = create_engine('sqlite:///liturgy.sqlite', echo=False)
Session = sessionmaker(db)

class BaseTemplate(object):

    def as_dict(self):
        res = {}
        for tag in self.__fields__:
            res[tag] = self.__getattribute__(tag)
        for tag in self.__dict_fields__:
            res[tag] = map(lambda x: x.as_dict(), self.__getattribute__(tag))
        res['_id'] = self.id
        return res

Base = declarative_base(db, cls=BaseTemplate)

class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True)
    class_type = Column(String, nullable=False)
    type = Column(Integer, nullable=True)
    priority = Column(Integer, nullable=True)
    title = Column(Unicode, nullable=False)

    __mapper_args__ = {'polymorphic_on': class_type}

    __fields__ = ['title']
    __dict_fields__ = ['masses']

class FixedEvent(Event):
    __tablename__ = 'fixed_events'
    __mapper_args__ = {'polymorphic_identity': 'fixed'}

    id = Column(Integer, ForeignKey(Event.id, onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    day = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    season = Column(Integer, nullable=True)

class TimedEvent(Event):
    __tablename__ = 'timed_events'
    __mapper_args__ = {'polymorphic_identity': 'timed'}

    id = Column(Integer, ForeignKey(Event.id, onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    weekday = Column(Integer, nullable=False)
    week = Column(Integer, nullable=False)
    season = Column(Integer, nullable=False)

class MovableEvent(Event):
    __tablename__ = 'movable_events'
    __mapper_args__ = {'polymorphic_identity': 'movable'}

    id = Column(Integer, ForeignKey(Event.id, onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    calc_func = Column(Unicode, nullable=False)

class Mass(Base):
    __tablename__ = 'masses'
    __table_args__ = (
        UniqueConstraint("event_id", "order", "digit", "letter"),
        )

    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey(Event.id, onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    order = Column(Integer, nullable=False)
    digit = Column(String, nullable=True)
    letter = Column(Integer, nullable=True)
    title = Column(Unicode, nullable=True)
    status = Column(Unicode, nullable=False)

    event = relationship(Event,
                         backref=backref('masses', order_by=order))

    __fields__ = ['order', 'digit', 'letter', 'title', 'status']
    __dict_fields__ = ['readings']

class Reading(Base):
    __tablename__ = 'readings'
    __table_args__ = (
        UniqueConstraint("mass_id", "order", "alt_num"),
        )

    id = Column(Integer, primary_key=True)
    mass_id = Column(Integer, ForeignKey(Mass.id, onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    order = Column(Integer, nullable=False)
    alt_num = Column(Integer, nullable=False)
    title = Column(Unicode, nullable=False)
    quote = Column(Unicode, nullable=True, index=True)
    text = Column(UnicodeText, nullable=True)
    quote_status = Column(Unicode, nullable=False)
    text_status = Column(Unicode, nullable=False)

    __fields__ = ['order', 'alt_num', 'title', 'quote', 'text',
                  'quote_status', 'text_status']
    __dict_fields__ = []

    mass = relationship(Mass,
                        backref=backref('readings', order_by=(order, alt_num)))

    def my_yaml_export(self, spaces=0):
        res = ''
        def write_line(line):
            res += ' ' * spaces + line + '\n'

        write_line('title:       "%s"' % (self.title))
        write_line('order:        %d' % (self.order))
        write_line('alt_num:      %s' % (self.alt_num))
        write_line('quote_status: "%s"' % (self.quote_status))
        write_line('text_status:  "%s"' % (self.text_status))
        if self.quote is not None:
            write_line('quote:    "%s"' % (self.quote))
        else:
            write_line('quote:    null')
        if self.text is not None:
            write_line('text: >')
        return res

if __name__ == '__main__':
    Base.metadata.create_all()
