from datetime import datetime

from pydantic import BaseModel, UUID4, IPvAnyAddress


class ApplicationInstance(BaseModel):
    id: UUID4
    application_id: UUID4
    version: int
    environment: dict[str, str]
    secrets: dict[str, str]


class HostAttributes(BaseModel):
    os: str
    memory: int | None
    cpu_cores: int | None


class Host(BaseModel):
    id: UUID4
    label: str | None
    last_known_host: IPvAnyAddress
    last_seen: datetime
    attributes: HostAttributes
    applications: list[ApplicationInstance]
