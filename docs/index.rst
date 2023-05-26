:orphan:

.. title:: Quart Mongo Documentation

.. image:: _static/logo.png
   :width: 300px
   :alt: Quart Mongo
   :align: right

Quart-Mongo
-----------

`MongoDB <http://www.mongodb.org/>`_ is an open source database that stores flexible JSON-like "documents," which can have any number,
name, or hierarchy of fields within, instead of rows of data as in a relational database. Python developers can think of MongoDB as a 
persistent, searchablepy repository of Python dictionaries (and, in fact, this is how `PyMongo <http://api.mongodb.org/python/current/>`_ 
represents MongoDB documents).

Quart-Mongo bridges `Quart <https://quart.palletsprojects.com/en/latest/>`_, `Motor <https://motor.readthedocs.io/en/stable/>`_, 
and `Odmantic <https://art049.github.io/odmantic/>`_ to create a powerful MongoDB extension to use in your applications. It also 
provides some convenience helpers as well as being able to work with `Quart-Schema <https://quart-schema.readthedocs.io/en/latest/>`_.

Quart-Mongo is developed on Github, `here <https://github.com/Quart-Addons/quart-mongo>`_

This extension is heavily influenced on the following:

* `Flask-Pymongo <https://github.com/dcrosta/flask-pymongo>`_
* `Quart-Motor <https://github.com/marirs/quart-motor/>`_ 

.. image:: _static/quart_mongo.png
   :alt: Quart plus Mongo
   :align: center 

Tutorials
---------

.. toctree::
   :maxdepth: 2

   tutorials/index.rst

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