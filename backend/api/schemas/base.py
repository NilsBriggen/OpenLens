"""
Base response model for the OpenLens API.

Every response model inherits ApiModel: snake_case in Python, camelCase on
the wire. Request models deliberately do NOT inherit it - the frontend
already sends snake_case bodies, and that side of the contract stays as-is.

Gotcha: once a field carries an explicit validation_alias, populate_by_name
no longer accepts the bare field name - always list the field's own name
first in AliasChoices, e.g.:

    id: str = Field(validation_alias=AliasChoices('id', 'ioc_id'))
"""

from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class ApiModel(BaseModel):
    """Base for every response model."""
    model_config = ConfigDict(
        alias_generator=to_camel,   # sets both validation and serialization alias
        populate_by_name=True,      # field names still work for construction
        from_attributes=True,       # model_validate(<dataclass instance>)
        extra="ignore",             # a dataclass gaining a field never leaks it
    )


class Payload(ApiModel):
    """
    Analytical blob the frontend passes through to a chart or JSON view
    rather than reading field-by-field.
    """
    data: Any = None
    meta: Dict[str, Any] = Field(default_factory=dict)


class StatusOut(ApiModel):
    """Minimal acknowledgement body."""
    status: str
    detail: str = ''
