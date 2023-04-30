"""
quart_mongo.wrappers.engine
"""
from odmantic import AIOEngine as _AIOEngine
from quart import abort

from quart_mongo.typing import ODM_Model

class AIOEngine(_AIOEngine):
    """
    Subclass of the `Odmantic.AIOEngine` object, which is responsible for handling database
    operations with MongoDB in an asynchronous way using `Motor`.

    The purpose of this subclass is to add the function :func::`AIOEngine.find_one_or_404`.
    """
    async def find_one_or_404(self, model: ODM_Model, *args, **kwargs) -> ODM_Model:
        """
        Find a single document or raise a 404 with the browser.

        This function is like :meth:`AIOEngine.find_one`, but rather than returning
        ``None``. It will raise a 404 error (Not Found HTTP status) on the request.

        .. code-block:: python
            @app.route("/user/<username>")
            async def user_profile(username):
                user = await odmantic.db..find_one_or_404(model, {"_id": username})
                return await render_template("user.html",
                    user=user)

        Parameters:
            model (``Model``): The `Odmantic.Model` to use to find the model.
            args: Arguments to pass to `AIOEngine.find_one`.
            kwargs: Extra arguments to pass to `AIOEngine.find_one`.

        Returns:
            ``Model``

        Raises:
            ``HTTPException``: Uses `quart.abort` to raises this exception if
            there is not entry found in the database. This will raise a 404
            error code with the browser.
        """
        found = await self.find_one(model, *args, **kwargs)

        if found is None:
            abort(404)

        return found
