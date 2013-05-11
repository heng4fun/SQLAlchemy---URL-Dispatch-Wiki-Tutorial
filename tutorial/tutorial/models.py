from pyramid.security import (
    Allow,
    Everyone,
    )

from sqlalchemy import (
    Column,
    Integer,
    Text,
    String,
    DateTime,
    ForeignKey,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

class Page(Base):
    """ The SQLAlchemy declarative model class for a Page object. """
    __tablename__ = 'pages'
    id = Column(Integer, primary_key=True)
    name = Column(String(length=50), unique=True)
    data = Column(Text)

    def __init__(self, name, data):
        self.name = name
        self.data = data
    
        
class User(Base):
    
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    user_name = Column(String(50), unique=True)
    password = Column(String(50))
    user_group = Column(String(50),ForeignKey('groups.group_name'))
    
    def __init__(self, user_name, password, user_group):
        self.user_name = user_name
        self.password = password
        self.user_group = user_group
    
        
class Group(Base):

    __tablename__ = 'groups'
    id = Column(Integer, primary_key=True)
    group_name = Column(String(50), unique=True)
    
    def __init__(self, group_name):
        self.group_name = group_name
        
 
class Posts(Base):
    
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    user_name = Column(String(50), ForeignKey('users.user_name'))
    page_name = Column(String(50), ForeignKey('pages.name'))      
    message = Column(Text)
    time = Column(DateTime)
    
    def __init__(self, user_name, page_name, message, time):
        self.user_name = user_name
        self.page_name = page_name
        self.message = message
        self.time = time
   

class RootFactory(object):
    __acl__ = [ (Allow, Everyone, 'view'),
                (Allow, 'group:editors', 'edit') ]
    def __init__(self, request):
        pass
        
