Smarmy
======

::

|-----------------------------------------------|
|         _______________                       |
|        < smarm-a-lade! >                      |
|         ---------------                       |
|                \                              |
|                 \     .---. __                |
|            ,     \   /     \   \    ||||      |
|           \\\\      |O___O |    | \\||||      |
|           \   //    | \_/  |    |  \   /      |
|            '--/----/|     /     |   |-'       |
|                   // //  /     -----'         |
|                  //  \\ /      /              |
|                 //  // /      /               |
|                //  \\ /      /                |
|               //  // /      /                 |
|              /|   ' /      /                  |
|              //\___/      /                   |
|             //   ||\     /                    |
|             \\_  || '---'                     |
|             /' /  \\_.-                       |
|            /  /    --| |                      |
|            '-'      |  |                      |
|                      '-'                      |
|_______________________________________________|

What?
~~~~~

Smarmy is a fork of the `Leafy Miracle <http://leafy-miracle.rhcloud.com>`_.

The original project graphed package dependencies in Fedora.

Smarmy gets its data from the `Python Package Index <http://pypi.python.org>`_.

Features
~~~~~~~~

* Written in `Python <http://python.org>`_ using the `Pyramid <http://pylonsproject.org>`_ web framework
* `SQLAlchemy <http://sqlalchemy.org>`_ database model of `Yum <http://yum.baseurl.org>`_ Categories, Groups, Packages, and Dependencies
* Interactive graph widget, using `ToscaWidgets2 <http://toscawidgets.org/documentation/tw2.core>`_ and the `JavaScript InfoVis Toolkit <http://thejit.org>`_
* Package mouse-over menus linking to downloads, acls, code
  bugs, builds and updates.
* Deep linking
* Search bar with auto-completion

Source
~~~~~~

* `Git repository <https://github.com/ralphbean/smarmy>`_ on github.

Running
~~~~~~~

::

   sudo yum -y install python-virtualenv
   git clone git://github.com/ralphbean/smarmy.git && cd smarmy
   virtualenv env && source env/bin/activate
   python setup.py develop
   python smarmy/populate.py
   paster serve development.ini

Authors
~~~~~~~

* Luke Macken <lmacken@redhat.com>
* Ralph Bean <ralph.bean@gmail.com>
