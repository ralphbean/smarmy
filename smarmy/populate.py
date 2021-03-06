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

import xmlrpclib

def ingest_package(package, tries=0):
    print "Processing package", package
    result = {
        'name': package,
        'releases':[]
    }

    # Bail if we keep failing.
    if tries > 3:
        print " ** Some error collecting package", package
        return result

    try:
        client = xmlrpclib.ServerProxy('http://pypi.python.org/pypi')


        for release in client.package_releases(package):#show_hidden=True):
            data = client.release_data(package, release)
            result['releases'].append({
                'name': release,
                'data': data
            })
    except Exception as e:
        return ingest_package(package, tries+1)
    return result


import multiprocessing as mp
pool = mp.Pool(100)

from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from kitchen.text.converters import to_unicode

from models import Root
from models import Package
from models import Release
from models import License
from models import Author
from models import Maintainer
from models import Classifier
from models import Keyword
from models import DBSession
from models import initialize_sql

def populate():
    session = DBSession()
    root = Root(name=u'PyPI')
    session.add(root)

    client = xmlrpclib.ServerProxy('http://pypi.python.org/pypi')
    packages = client.list_packages()

    # Do it in parallel to go faster
    results = pool.map(ingest_package, packages)

    for i, result in enumerate(results):
        package = result['name']
        print "Populating DB with:", i, package

        # Query for it first...
        if Package.query.filter_by(name=package).count() > 0:
            print "Package '%s' is already in the DB.  Skipping." % package
            continue

        p = Package(name=package, root=root)
        session.add(p)

        for release_data in result['releases']:
            release = release_data['name']
            data = release_data['data']

            r = Release(
                name=release,
                package=p,
                summary=data.get('summary', '')
            )

            for classifier in data['classifiers']:
                query = Classifier.query.filter_by(name=classifier)
                if query.count() == 0:
                    k = Classifier(name=classifier)
                    session.add(k)

                k = Classifier.query.filter_by(name=classifier).one()
                r.classifiers.append(k)

            for keyword in (data['keywords'] or '').split():
                query = Keyword.query.filter_by(name=keyword)
                if query.count() == 0:
                    k = Keyword(name=keyword)
                    session.add(k)

                k = Keyword.query.filter_by(name=keyword).one()
                r.keywords.append(k)

            if 'maintainer' in data:
                query = Maintainer.query.filter_by(name=data['maintainer'])
                if query.count() == 0:
                    a = Maintainer(name=data['maintainer'],
                                   email=data.get('maintainer_email'))
                    session.add(a)

                a = Maintainer.query.filter_by(name=data['maintainer']).one()
                r.maintainer = a

            if 'author' in data:
                query = Author.query.filter_by(name=data['author'])
                if query.count() == 0:
                    a = Author(name=data['author'],
                               email=data.get('author_email'))
                    session.add(a)

                a = Author.query.filter_by(name=data['author']).one()
                r.author = a

            if 'license' in data:
                query = License.query.filter_by(name=data['license'])
                if query.count() == 0:
                    l = License(name=data['license'])
                    session.add(l)

                l = License.query.filter_by(name=data['license']).one()
                r.license = l

            session.add(r)

    session.commit()


if __name__ == '__main__':
    print "Initializing Smarmy..."
    engine = create_engine('sqlite:///smarmy.db')
    initialize_sql(engine)
    try:
        populate()
        print "Complete!"
    except IntegrityError, e:
        print "Got an Integrity Error:", str(e)
        DBSession.rollback()
