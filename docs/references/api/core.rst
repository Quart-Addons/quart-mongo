Core
====

.. autoclass:: quart_mongo.Mongo
    :members:
    :private-members:
    
    .. attribute:: cx

        The :class::`~quart_mongo.wrappers.AIOMotorClient` connected to
        the MongoDB server.
    
    .. attribute:: db

        The :class::`~quart_mongo.wrappers.AIOMotorDatabase` if the URI
        used named a database or ``None`` otherwise.
    
    .. attribute:: odm

        The :class::`~quart_mongo.wrappers.AIOEngine` if the URI used 
        named a database or ``None`` otherwise. This is the class to
        add, get, or update :class::`~odmantic.Models` to the database.

.. autodata:: quart_mongo.Ascending

.. autodata:: quart_mongo.Descending