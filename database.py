#!/usr/bin/python
# -*- coding: utf-8 -*-

from sqlalchemy import create_engine, Column, Integer, String, Unicode, UnicodeText, ForeignKey, DateTime, UniqueConstraint, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref

import os

db_filename = 'liturgy.sqlite'
if 'LITURGY_DB' in os.environ:
    db_filename = os.environ['LITURGY_DB']
db = create_engine('sqlite:///%s' % (db_filename), echo=False)
Session = sessionmaker(db)

# From http://stackoverflow.com/a/17246726/807307
def get_subclasses(c):
    subclasses = c.__subclasses__()
    for d in list(subclasses):
        subclasses.extend(get_subclasses(d))
    return subclasses

def from_dict(data, session):
    subclasses = get_subclasses(Base)
    [cls] = [x for x in subclasses if x.__name__ == data['_type']]

    # Retrieve or create the object
    if '_id' in data:
        obj = session.query(cls).filter(cls.id == data['_id']).one()
    else:
        obj = cls()

    # Copy fields from data
    if '_copy_from' not in data or data['_copy_from'] is None:
        for tag in cls.__fields__:
            if tag in data:
                obj.__setattr__(tag, data[tag])
        for tag in cls.__dict_fields__:
            if tag in data:
                obj.__setattr__(tag, [])
                for piece in data[tag]:
                    obj.__getattribute__(tag).append(from_dict(piece, session))

    # Copy fields from another reference object
    else:
        src_obj = session.query(cls).filter(cls.id == data['_copy_from']).one()
        for tag in cls.__fields__:
            obj.__setattr__(tag, src_obj.__getattribute__(tag))
        for tag in cls.__dict_fields__:
            obj.__setattr__(tag, [])
            for piece in src_obj.__getattribute__(tag):
                obj.__getattribute__(tag).append(piece)

    return obj

class BaseTemplate(object):

    def as_dict(self):
        res = {}
        for tag in self.__fields__:
            if tag in self.__masked_fields__:
                res[tag + '_'] = self.__getattribute__(tag)
            else:
                res[tag] = self.__getattribute__(tag)
        for tag in self.__dict_fields__:
            res[tag] = map(lambda x: x.as_dict(), self.__getattribute__(tag))
        res['_id'] = self.id
        res['_type'] = self.__class__.__name__
        return res

Base = declarative_base(db, cls=BaseTemplate)

class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True)
    class_type = Column(String, nullable=False)
    type = Column(Integer, nullable=True)
    priority = Column(Integer, nullable=True)
    title = Column(Unicode, nullable=False)
    status = Column(Unicode, nullable=False)
    no_slide = Column(Boolean, nullable=False, default=False)
    no_masses = Column(Boolean, nullable=False, default=False)

    __mapper_args__ = {'polymorphic_on': class_type}

    __fields__ = ['title', 'status', 'no_slide', 'no_masses']
    __masked_fields__ = []
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
    event_id = Column(Integer, ForeignKey(Event.id, onupdate="CASCADE", ondelete="CASCADE"), nullable=True)
    order = Column(Integer, nullable=False)
    digit = Column(String, nullable=True)
    letter = Column(String, nullable=True)
    title = Column(Unicode, nullable=True)
    status = Column(Unicode, nullable=False)

    event = relationship(Event,
                         backref=backref('masses', order_by=order))

    __fields__ = ['order', 'digit', 'letter', 'title', 'status']
    __masked_fields__ = []
    __dict_fields__ = ['readings']

class Reading(Base):
    __tablename__ = 'readings'
    __table_args__ = (
        UniqueConstraint("mass_id", "order", "alt_num"),
        )

    id = Column(Integer, primary_key=True)
    mass_id = Column(Integer, ForeignKey(Mass.id, onupdate="CASCADE", ondelete="CASCADE"), nullable=True)
    order = Column(Integer, nullable=False)
    alt_num = Column(Integer, nullable=False)
    title = Column(Unicode, nullable=False)
    quote = Column(Unicode, nullable=True, index=True)
    text = Column(UnicodeText, nullable=True)
    quote_status = Column(Unicode, nullable=False)
    text_status = Column(Unicode, nullable=False)
    only_on_sunday = Column(Boolean, nullable=False)

    __fields__ = ['order', 'alt_num', 'title', 'quote', 'text',
                  'quote_status', 'text_status', 'only_on_sunday']
    __masked_fields__ = ['text']
    __dict_fields__ = []

    mass = relationship(Mass,
                        backref=backref('readings', order_by=(order, alt_num)))

    def as_dict(self):
        res = Base.as_dict(self)
        res['_copy_from'] = None
        return res

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
