Odmantic
========

Quart-Mongo uses `Odmantic <https://art049.github.io/odmantic/>`_ for ODM 
(Object Document Mapper) with MongoDB.

Connection
-----------

This is the same as for Motor. Refer to the information
:ref:`here <_motor connection>`. 

Odmantic Engine Instance
------------------------

If the database name was passed with the URI. Then 
:attribute:`~quart_mongo.Mongo.odm` will be an instance 
of :class:`quart_mongo.wrappers.AIOEngine`. If it was not,
you will need to set the database manually like so. 

.. code-block:: python

    mongo = Mongo(app)
    mongo.odm = self.cx.odm['test-database']

Now you can follow the Odmantic `documentation <https://art049.github.io/odmantic/engine/>`_ 
for inserting and finding documents. 

Find One or 404
----------------

The extension provides a helper function to find a document or it will
raise a 404 error.

.. automethod:: quart_mongo.wrappers.AIOEngine.find_one_or_404

Quart-Schema
------------

Quart-Schema can be used to send, recieve, and validate Odmantic models 
in routes, since :class:`~odmantic.Models` is based on Pydantic for model 
definition and validation. More information Quart-Schema can be found
`here <https://github.com/pgjones/quart-schema>`_.

.. note::

    If you are using Quart-Schema in your application. Please register 
    Quart-Schema with application first and then Quart-Mongo. Quart-Mongo
    JSON provider should be used in lieu of Quart-Schema JSON provider. 
    This will make sure that your application will use the JSON provider
    from Quart-Mongo. The JSON provider in Quart-Mongo has the same
    capability as the one from Quart-Schema except it can handle MongoDB
    collections as well. 




