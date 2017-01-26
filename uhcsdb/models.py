""" Database models for microstructure dataset """

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Float, ForeignKey, Integer, String

from flask import current_app

Base = declarative_base()

# dbpath = 'sqlite:///data/microstructures.sqlite'

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username =  Column(String(250))
    firstname = Column(String(250))
    lastname =  Column(String(250))
    email =     Column(String(250))
    micrographs = relationship('Micrograph')

    def info(self):
        """ construct a dictionary to feed data to render_template """
        return dict(username=self.username,
                    email=self.email)

class Collection(Base):
    __tablename__ = 'collection'
    id =   Column(Integer, primary_key=True)
    name = Column(String(250))
    
class Sample(Base):
    __tablename__ = 'sample'
    id = Column(Integer, primary_key=True)
    label = Column(String(250))
    anneal_time = Column(Float)
    anneal_time_unit = Column(String(16))
    anneal_temperature = Column(Float)
    anneal_temp_unit = Column(String(16))
    cool = Column(String(16))
    micrographs = relationship('Micrograph')
    
class Micrograph(Base):
    __tablename__ = 'micrograph'
    id = Column(Integer, primary_key=True)
    path =             Column(String())
    contributor =      Column(Integer, ForeignKey('user.id'))
    micron_bar =       Column(Float)
    micron_bar_units = Column(String(64))
    micron_bar_px =    Column(Integer)
    magnification =    Column(Integer)
    detector =         Column(String(16))
    sample_id =        Column(Integer, ForeignKey('sample.id'))
    sample =           relationship('Sample', back_populates='micrographs')
    # user_id =          Column(Integer, ForeignKey('user.id'))
    user =             relationship('User', back_populates='micrographs')
    mstructure_class = Column(String(250))

    def info(self):
        """ construct a dictionary to feed data to render_template """

        def format_path(m_id):
            """ routing path to micrograph image file """
            # basename, ext = os.path.splitext(self.path)
            # name = 'micrograph{}{}'.format(m_id, ext)
            # convert image set to png for web...
            # (Chrome and Firefox don't display TIF by default
            name = 'micrograph{}.png'.format(m_id) 
            # return os.path.join(os.sep, current_app.config['DATADIR'], 'data', 'micrographs', name)
            return os.path.join(os.sep, current_app.config['MICROGRAPH_PATH'], name)
        # date = self.upload_date.strftime('%d %B %Y at %I:%M %p')
        if self.sample is not None and self.sample.label is not None:
            annealing_condition = self.sample.label
        else:
            annealing_condition = 'Not available'
        return dict(micrograph_id=self.id,
                    author_id=self.contributor,
                    micrograph_path=format_path(self.id),
                    url='',
                    annealing_condition=annealing_condition,
                    upload_date='today',
                    microconstituent=self.mstructure_class
        )

    
if __name__ == '__main__':
    engine = create_engine(dbpath)

    Base.metadata.create_all(engine)
