﻿import sqlalchemy

from .db_session import SqlAlchemyBase


class Components(SqlAlchemyBase):
    __tablename__ = 'components'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    type = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    about = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    datasheet = sqlalchemy.Column(sqlalchemy.String, nullable=True)
