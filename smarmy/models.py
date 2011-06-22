# Copyright (C) 2011 Luke Macken <lmacken@redhat.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from sqlalchemy import Integer, Column, Unicode, UnicodeText, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, scoped_session, sessionmaker, backref

from kitchen.text.converters import to_unicode
import hashlib

DBSession = scoped_session(sessionmaker())
Base = declarative_base()
Base.query = DBSession.query_property()


class Root(Base):
    __tablename__ = 'root'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255), unique=True)

    packages = relationship("Package", backref="root")

    def __init__(self, name):
        self.name = to_unicode(name)

    def __unicode__(self):
        return self.name

class Package(Base):
    __tablename__ = 'packages'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255), unique=True)
    releases = relationship("Release", backref="package")
    root_id = Column(Integer, ForeignKey('root.id'))

    def __unicode__(self):
        return unicode(self.name)


classifiers_mapping = Table(
    'releases_classifiers_mapping', Base.metadata,
    Column('classifier_id', Integer,
           ForeignKey('classifiers.id'), primary_key=True),
    Column('release_id', Integer,
           ForeignKey('releases.id'), primary_key=True))

keywords_mapping = Table(
    'releases_keywords_mapping', Base.metadata,
    Column('keyword_id', Integer,
           ForeignKey('keywords.id'), primary_key=True),
    Column('release_id', Integer,
           ForeignKey('releases.id'), primary_key=True))

class Release(Base):
    __tablename__ = 'releases'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255))
    summary = Column(Unicode(1024))
    long_description = Column(Unicode(4096))

    package_id = Column(Integer, ForeignKey('packages.id'))
    license_id = Column(Integer, ForeignKey('licenses.id'))
    author_id       = Column(Integer, ForeignKey('authors.id'))
    maintainer_id   = Column(Integer, ForeignKey('maintainers.id'))

    keywords = relationship(
        "Keyword", secondary=keywords_mapping,
        backref='releases')
    classifiers = relationship(
        "Classifier", secondary=classifiers_mapping,
        backref='releases')

    def __unicode__(self):
        return u"%s - %s" % (unicode(self.package), self.name)

    def __jit_data__(self):
        return {
            'hover_html': """hai""",
            "traversal_costs": {},
        }

class Keyword(Base):
    __tablename__ = 'keywords'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255), unique=True)
    def __unicode__(self):
        return self.name

class Classifier(Base):
    __tablename__ = 'classifiers'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255), unique=True)
    def __unicode__(self):
        return self.name


class GravatarMixin(object):
    def avatar_link(self, s=24, d='mm'):
        hash = 'd41d8cd98f00b204e9800998ecf8427e'
        if self.email:
            hash = hashlib.md5(self.email).hexdigest()
        return "http://www.gravatar.com/avatar/%s?s=%i&d=%s" % (hash, s, d)


class Author(Base, GravatarMixin):
    __tablename__ = 'authors'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255), unique=True)
    email = Column(Unicode(255))
    releases = relationship("Release", backref="author")
    def __unicode__(self):
        return "Author:  <img src='%s' /> %s" % (
            self.avatar_link(), (self.name or "'None'"))

class Maintainer(Base, GravatarMixin):
    __tablename__ = 'maintainers'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255), unique=True)
    email = Column(Unicode(255))
    releases = relationship("Release", backref="maintainer")
    def __unicode__(self):
        return "Maintainer:  <img src='%s' /> %s" % (
            self.avatar_link(), (self.name or "'None'"))

class License(Base):
    __tablename__ = 'licenses'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255), unique=True)
    releases = relationship("Release", backref="license")
    def __unicode__(self):
        return "License:  " + (self.name or "'None'")


def initialize_sql(engine):
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
