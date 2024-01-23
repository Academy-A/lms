import logging
from typing import Any

from pydantic import BaseModel, ValidationError
from starlette.requests import Request
from starlette_admin._types import RowActionsDisplayType
from starlette_admin.contrib.sqla import ModelView
from starlette_admin.contrib.sqla.converters import BaseSQLAModelConverter
from starlette_admin.helpers import pydantic_error_to_form_validation_errors

log = logging.getLogger(__name__)


class BaseModelView(ModelView):
    pydantic_model: type[BaseModel] | None = None
    _pydantic_model: type[BaseModel]
    form_include_pk = True
    row_actions = ["view", "edit"]
    row_actions_display_type = RowActionsDisplayType.DROPDOWN

    def __init__(
        self,
        model: type[Any],
        pydantic_model: type[BaseModel] | None = None,
        icon: str | None = None,
        name: str | None = None,
        label: str | None = None,
        identity: str | None = None,
        converter: BaseSQLAModelConverter | None = None,
    ):
        pm = pydantic_model or self.pydantic_model
        if pm is None or not issubclass(pm, BaseModel):
            raise TypeError("You must set pydantic model")
        self._pydantic_model = pm
        super().__init__(model, icon, name, label, identity, converter)

    async def validate(self, request: Request, data: dict[str, Any]) -> None:
        try:
            self._pydantic_model(**data)
        except ValidationError as error:
            log.exception("Unprocessable entity")
            raise pydantic_error_to_form_validation_errors(error) from error
