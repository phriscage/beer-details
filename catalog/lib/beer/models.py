# pylint: disable=broad-except,invalid-name,import-error,wrong-import-position
"""
    the beer.models file contains the all the specific models for Beer
"""
from __future__ import absolute_import
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)) + '/../lib')
from lib.database import Base, BaseExtension
from sqlalchemy import Column, String, DateTime, Float
from sqlalchemy.dialects.mysql import INTEGER as Integer
from sqlalchemy.orm import validates

class Beer(Base):
    """
        Attributes for the Beer model. Custom MapperExtension declarative for
        before insert and update methods. The migrate.versioning api does not
        handle sqlalchemy.dialects.mysql for custom column attributes. I.E.
        INTEGER(unsigned=True), so they need to be modified manually.

        CREATE TABLE IF NOT EXISTS `data`.`beers` (
	    `id` INTEGER(10) UNSIGNED AUTO_INCREMENT PRIMARY KEY,
	    `brewery` VARCHAR(255),
	    `style`    VARCHAR(255),
	    `price`    DECIMAL(13, 2),
	    `name` VARCHAR(255),
	    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
	);

     """
    __tablename__ = 'beers'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }
    ## mapper extension declarative for before insert and before update
    __mapper_args__ = {'extension': BaseExtension()}

    id = Column('id', Integer(unsigned=True), primary_key=True)
    brewery = Column(String(255), index=True)
    name = Column(String(255), index=True, nullable=False)
    style = Column(String(255), index=True)
    price = Column(Float(13, 2), nullable=False)
    created_at = Column(DateTime(), nullable=False)
    updated_at = Column(DateTime(), nullable=False)

    def __init__(self, name):
        """ initialize """
        self.name = name

    @validates('name')
    def validate_name(self, key, name):
        """ validate the name attribute """
        if not name:
            raise ValueError("'name' is null")
        #assert '@' in name
        return name

    #def __repr__(self):
        #return '<User %r>' % (self.name)
