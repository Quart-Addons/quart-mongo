Motor
=====

Quart-Mongo uses `Motor <https://motor.readthedocs.io/en/stable/index.html>`_ 
for general MongoDB connections.

Connection
-----------

.. _motor connection:

The :attribute:`~quart_mongo.Mongo.cx` will be an instance of 
:class:`~quart_mongo.wrappers.AsyncIOMotorClient` if the URI was passed
to :class:`~quart_mongo.Mongo` or set via the app configuration variable. 
Refer to `Configuration`_ for additional information. 

Database
--------

.. _motor database:

The :attribute:`~quart_mongo.Mongo.db` will be an instance of 
:class:`~quart_mongo.wrappers.AIOMotorDatabase` if the database
name was passed with the URI. If it was not, you will need to set
the database manually like so: 

.. code-block:: python

    mongo = Mongo(app)
    mongo.db = mongo.cx['test-database']
    
    # or
    mongo.db = mongo.cx.engine('test-database')

Getting a Collection
--------------------

Once the database is setup. You can start finding documents in a collection.
You get a collection by calling the :attribute:`~quart_mongo.Mongo.db` in the
following manner:

.. code-block:: python

    mongo = Mongo(app)
    mongo.db = mongo.cx['test-database']

    # using dot notation
    collection = mongo.db.some_collection
    # or 
    collection = mongo.db['some_collection']

Now you can follow the Motor `documentation <https://motor.readthedocs.io/en/stable/tutorial-asyncio.html>`_ 
for inserting and finding documents. 

Find One or 404
----------------

The extension provides a helper function to find a document or it will
raise a 404 error.

.. automethod:: quart_mongo.wrappers.AIOMotorCollection.find_one_or_404

Send File Helpers
------------------

Two helper functions are provided for sending files from GridFS. They are:

.. automethod:: quart_mongo.Mongo.send_file_by_name

.. automethod:: quart_mongo.Mongo.send_file_by_id

Save File Helper
----------------

A helper function is provided for saving files to GridFS.

.. automethod:: quart_mongo.Mongo.save_file



