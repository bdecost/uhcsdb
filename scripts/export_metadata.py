#!/usr/bin/env python
""" load uhcsdb metadata from sqlite database into pandas dataframe """
import sys
import numpy as np
import pandas as pd
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, contains_eager

sys.path.append('.')
from uhcsdb.models import Base, User, Collection, Sample, Micrograph

@contextmanager
def uhcsdb_session(dbpath):
    """ start a sqlalchemy session for the uhcsdb metadata store """
    engine = create_engine('sqlite:///' + dbpath)
    Base.metadata.bind = engine
    dbSession = sessionmaker(bind=engine)
    db = dbSession()
    try:
        yield db
    finally:
        db.close()

if __name__ == '__main__':
    
    with uhcsdb_session('uhcsdb/microstructures.sqlite') as db:
        
        # get metadata for all images associated with a sample
        q = (
            db.query(Micrograph)
            .outerjoin(Micrograph.sample)
            .options(contains_eager(Micrograph.sample))
        )
        df = pd.read_sql_query(q.statement, con=db.connection())

    # drop the redundant id field that results from Micrograph.sample.id
    df = df.T.groupby(level=0).last().T

    print(df.head())
    df.to_csv('uhcs-metadata.csv')
