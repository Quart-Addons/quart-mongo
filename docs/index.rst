:orphan:

.. title:: Quart Mongo Documentation

.. image:: _static/logo.png
   :width: 300px
   :alt: Quart Mongo
   :align: right

Introduction
------------

`MongoDB <http://www.mongodb.org/>`_ is an open source database that stores flexible JSON-like "documents," which can have any number,
name, or hierarchy of fields within, instead of rows of data as in a relational database. Python developers can think of MongoDB as a 
persistent, searchablepy repository of Python dictionaries (and, in fact, this is how `PyMongo <http://api.mongodb.org/python/current/>`_ 
represents MongoDB documents).

Quart-Mongo bridges `Quart <https://quart.palletsprojects.com/en/latest/>`_, `Motor <https://motor.readthedocs.io/en/stable/>`_, 
and `Odmantic <https://art049.github.io/odmantic/>`_ to create a powerful MongoDB extension to use in your applications. It also 
provides some convenience helpers as well as being quarable to work `Quart-Schema <https://quart-schema.readthedocs.io/en/latest/>`_.

Quart-Mongo is developed on Github, `here <https://github.com/Quart-Addons/quart-mongo>`_

This extension is heavily influenced on the following:

* `Flask-Pymongo <https://github.com/dcrosta/flask-pymongo>`_
* `Quart-Motor <https://github.com/marirs/quart-motor/>`_ 

Quickstart
----------

First, install Quart-Mongo:

.. code-block:: bash

    $ pip install quart_mongo

Next, add a :class:`~quart_mongo.Mongo` to your code:

.. code-block:: python

    from quart import Quart
    from quart_mongo import Mongo

    app = Quart(__name__)
    app.config["MONGO_URI"] = "mongodb://localhost:27017/myDatabase"
    mongo = Mongo(app)

:class:`~quart_mongo.Mongo` connects to the MongoDB server running on
port 27017 on localhost, to the database named ``myDatabase``. This database
is exposed as the :attr:`~quart_mongo.Mongo.db` attribute.

You can use :attr:`~quart_mongo.Mongo.db` directly in views:

.. code-block:: python

    @app.route("/")
    async def home_page():
        online_users = await mongo.db.users.find({"online": True})
        return await render_template("index.html",
            online_users=online_users)

.. note::

    If there is no database name, the :attr:`~quart_mongo.Mongo.db`
    attribute will be ``None``.

How to guides
-------------

.. toctree::
   :maxdepth: 2

   how_to_guides/index.rst

Reference
---------

.. toctree::
   :maxdepth: 2

   references/index.rst