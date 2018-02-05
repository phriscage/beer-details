# pylint: disable=broad-except,invalid-name,import-error,wrong-import-position
""" model helpers used for each child model """
from __future__ import absolute_import
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, MapperExtension, create_session
from sqlalchemy.ext.declarative import declarative_base as real_declarative_base
#from sqlalchemy.ext.declarative import declarative_base
import datetime
import simplejson as json

engine = create_engine(os.getenv('SQLALCHEMY_DATABASE_URI'),
                       convert_unicode=True,
                       pool_recycle=7200)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
#engine = None

#def init_engine(uri, **kwargs):
    #""" create the engine when needed """
    #global engine
    #engine = create_engine(uri, **kwargs)
    #return engine

#db_session = scoped_session(lambda: create_session(autocommit=False,
                                                   #autoflush=False,
                                                   #bind=engine))

# Let's make this a class decorator
declarative_base = lambda cls: real_declarative_base(cls=cls)

#Base = declarative_base()
@declarative_base
class Base(object):
    """
    Add some default properties and methods to the SQLAlchemy declarative base.
    """
    @property
    def columns(self):
        """ list of database column names """
        #for column in self._sa_class_manager.mapper.mapped_table.columns:
            #print column
        return [column.name for column in self.__table__.columns]

    @property
    def fields(self):
        """ list of model field names """
        return [key for key in self.__mapper__.c.keys()]

    @property
    def column_items(self):
        """ get each class attribute value for the column name """
        return dict((column, getattr(self, column, None)) for column in \
            self.columns)

    @property
    def field_items(self):
        """ get each class attribute value for the field name """
        return dict((field, getattr(self, field)) for field in self.fields)

    @property
    def to_json(self):
        """ return a dictionary for field items """
        return self.field_items

    @property
    def resource_id(self):
        """ define the resource id for an object """
        return self.id

    @property
    def uri(self):
        """ return the uri path using class name as resource """
        resource = Converter().camel_to_snake(self.__class__.__name__)
        return "/%s/%s" % (resource, self.resource_id)

Base.query = db_session.query_property()


class BaseExtension(MapperExtension):
    """Base entension class for all entity """

    def before_insert(self, mapper, connection, instance):
        """ set the created_at  """
        datetime_now = datetime.datetime.now()
        instance.created_at = datetime_now
        if not instance.updated_at:
            instance.updated_at = datetime_now

    def before_update(self, mapper, connection, instance):
        """ set the updated_at  """
        instance.updated_at = datetime.datetime.now()


def to_json(instance, model):
    """ Returns a JSON representation of an SQLAlchemy-backed object.
    """
    json = {}
    json['fields'] = {}
    json['pk'] = getattr(model, 'id')

    for col in model._sa_class_manager.mapper.mapped_table.columns:
        json['fields'][col.name] = getattr(model, col.name)

    return json.dumps([json])
