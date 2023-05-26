.. _Config:

Configuration
=============

You can configure Quart-Mongo either by passing a `MongoDB URI
<https://docs.mongodb.com/manual/reference/connection-string/>`_ to the
:class:`~quart_mongo.Mongo` constructor, or assigning it to the
``MONGO_URI`` `Quart configuration variable
<https://quart.palletsprojects.com/en/latest/how_to_guides/configuration.html>`_

The :class:`~quart_mongo.Mongo` instance also accepts these additional
customization options:

* ``json_options``, a :class:`~bson.json_util.JSONOptions` instance which
  controls the JSON serialization of MongoDB objects when used with
  :func:`~quart.json.jsonify`. Also, ``json_options`` can be assigned using
  the configuration variable ``MONGO_JSON_OPTIONS``.

You may also pass additional keyword arguments to the ``Mongo``
constructor. These are passed directly through to the underlying
:class:`~motor.motor_asyncio.AsyncIOMotorClient` object.

.. note::

    By default, Quart-Mongo sets the ``connect`` keyword argument to
    ``False``, to prevent Motor from connecting immediately. Motor
    itself `is not fork-safe
    <http://api.mongodb.com/python/current/faq.html#is-pymongo-fork-safe>`_,
    and delaying connection until the app is actually used is necessary to
    avoid issues. If you wish to change this default behavior, pass
    ``connect=True`` as a keyword argument to ``Mongo``.

You can create multiple ``Mongo`` instances, to connect to multiple
databases or database servers:

.. code-block:: python

    app = Quart(__name__)

    # connect to MongoDB with the defaults
    mongo1 = Mongo(app, uri="mongodb://localhost:27017/databaseOne")

    # connect to another MongoDB database on the same host
    mongo2 = Mongo(app, uri="mongodb://localhost:27017/databaseTwo")

    # connect to another MongoDB server altogether
    mongo3 = Mongo(app, uri="mongodb://another.host:27017/databaseThree")

Each instance is independent of the others and shares no state.