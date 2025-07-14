"""
quart_mongo.odmantic.wrappers
"""
from typing import Any, Dict, Optional, Type, Union

from odmantic import AIOEngine as _AIOEngine
from odmantic.engine import ModelType, AIOSessionType
from odmantic.query import QueryExpression
from quart import abort


class AIOEngine(_AIOEngine):
    """
    A wrapper of `~odmantic.AIOEngine` to include
    a `find_one_or_404 function for `quart.Quart`.
    """
    async def find_one_or_404(
            self,
            model: Type[ModelType],
            *queries: Union[
                QueryExpression, Dict, bool
            ],
            sort: Optional[Any] = None,
            session: AIOSessionType = None
    ) -> ModelType:
        """
        Find a single document or raise a 404.

        This like :meth:`~odmantic.engine.find_one`, but rather than
        returning ``None``, cause a 404 Not Found HTTP status on the
        request.

        .. code-block:: python
            @app.route("/user/<username>")
            async def user_profile(username):
                user = await mongo.engine.find_one_or_404(
                    user_model, *query_expression
                )
                return render_template("user.html", user=user)
        """
        found = await self.find_one(
            model,
            *queries,
            sort=sort,
            session=session
        )

        if found is None:
            abort(404)
        else:
            return found
