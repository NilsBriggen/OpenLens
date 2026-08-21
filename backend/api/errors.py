"""
Error contract for the OpenLens API.

One body shape for every error:

    {"error": "feature_unavailable", "message": "...", "feature": "...",
     "requires": ["networkx"], "detail": null}

Rule: an endpoint must never return [] or {} for "cannot compute" - 200 []
means *computed, empty*. Anything that could not run returns 503 with a
machine-readable reason.
"""

from typing import Any, List, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from backend.api.schemas.base import ApiModel


class ApiError(ApiModel):
    """Uniform error body."""
    error: str
    message: str
    feature: Optional[str] = None
    requires: List[str] = []
    detail: Optional[Any] = None


class FeatureUnavailable(Exception):
    """Raised when an endpoint's backing capability is missing (-> 503)."""

    def __init__(self, feature: str, requires: List[str] = None,
                 message: str = None):
        self.feature = feature
        self.requires = requires or []
        self.message = message or (
            f"{feature} is unavailable"
            + (f"; requires: {', '.join(self.requires)}" if self.requires else ''))
        super().__init__(self.message)

    def to_body(self) -> ApiError:
        return ApiError(error='feature_unavailable', message=self.message,
                        feature=self.feature, requires=self.requires)


def _error_response(status_code: int, body: ApiError,
                    headers: dict = None) -> JSONResponse:
    return JSONResponse(status_code=status_code,
                        content=body.model_dump(by_alias=True),
                        headers=headers)


def install_error_handlers(app: FastAPI) -> None:
    """Make every error body ApiError-shaped, app-wide."""

    @app.exception_handler(FeatureUnavailable)
    async def _feature_unavailable(request: Request, exc: FeatureUnavailable):
        return _error_response(503, exc.to_body())

    @app.exception_handler(HTTPException)
    async def _http_exception(request: Request, exc: HTTPException):
        code_by_status = {
            400: 'invalid_argument',
            401: 'unauthorized',
            403: 'forbidden',
            404: 'not_found',
            409: 'conflict',
            501: 'not_implemented',
            503: 'feature_unavailable',
        }
        detail = exc.detail
        message = detail if isinstance(detail, str) else 'Request failed'
        body = ApiError(
            error=code_by_status.get(exc.status_code, 'error'),
            message=message,
            detail=None if isinstance(detail, str) else detail,
        )
        # Preserve auth challenge headers (WWW-Authenticate on 401s).
        return _error_response(exc.status_code, body, headers=exc.headers)

    @app.exception_handler(RequestValidationError)
    async def _validation_error(request: Request, exc: RequestValidationError):
        return _error_response(422, ApiError(
            error='validation_error',
            message='Request validation failed',
            detail=exc.errors(),
        ))
