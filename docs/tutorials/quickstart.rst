Quickstart
==========

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

If you wish to use Odmantic models to insert, get, update, and delete
collections. Then the database will also be exposed as the
:attr:`~quart_mongo.Mongo.odm` attribute.

You can also use :attr:`~quart_mongo.Mongo.odm` directly in views:

.. code-block:: python
    from odmaintic import Model

    class User(Model):
        name: str
        online: bool
    
    @app.route("/")
    async def home_page():
        online_users_db = await mongo.odm.find(User, User.online == True)

        # online users will be a list of `User` classes. If you wish
        # to pass to the template. You need to convert the classes
        # to a list of dictionaries. 
        online_users = []

        for user in online_users_db:
            online_users.append(user.doc())

        return await render_template("index.html",
            online_users=online_users)

.. note::

    If there is no database name, the :attr:`~quart_mongo.Mongo.odm`
    attribute will be ``None`` just like `~quart_mongo.Mongo.db`.
