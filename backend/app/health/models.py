from enum import Enum

from pydantic import BaseModel


class HealthStatus(str, Enum):
    ok = "ok"
    degraded = "degraded"
    unavailable = "unavailable"


class HealthResponse(BaseModel):
    status: HealthStatus
