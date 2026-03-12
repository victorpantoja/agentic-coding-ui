from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ResponseBase(BaseModel):
    success: bool
    message: str | None = None


class DataResponse(ResponseBase, Generic[T]):
    success: bool = True
    data: T | None = None


class ListResponse(ResponseBase, Generic[T]):
    success: bool = True
    data: list[T] = []
    total: int = 0


class ErrorResponse(ResponseBase):
    success: bool = False
    error_code: str | None = None
    error_details: dict[str, Any] | None = None


class StatusResponse(ResponseBase):
    success: bool = True
    status: str | None = None
