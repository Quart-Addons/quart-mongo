# Quart Mongo

![Quart Mongo Logo](logos/logo.png)

Quart-Mongo bridges [Quart][], [Motor][], and [Odmantic][] to create a powerful MongoDB extension to use in your Quart applications. It also provides some convenience helpers as well as being able to work with [Quart-Schema][].

![Quart Plug Mongo](logos/quart_mongo.png)

# Installation 

Install the extension with the following command:

    $ pip3 install quart-mongo

# Usage

To use the extension simply import the class wrapper and pass the Quart app 
object back to here. Do so like this:

    from quart import Quart
    from quart_mongo import Mongo

    app = Quart(__name__)
    babel = Mongo(app)


# Documentation

The documentation for Quart-Mongo and is available [here][docs].

[Quart]: https://quart.palletsprojects.com/en/latest/>
[Motor]: https://motor.readthedocs.io/en/stable/>
[Odmantic]: https://art049.github.io/odmantic/
[Quart-Schema]: https://github.com/pgjones/quart-schema
[docs]: https://quart-babel.readthedocs.io
