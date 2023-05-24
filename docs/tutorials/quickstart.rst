Quickstart
----------

Add a :class:`~quart_mongo.Mongo` to your code:

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