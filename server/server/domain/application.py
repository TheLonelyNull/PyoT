from enum import Enum, auto

from pydantic import BaseModel, UUID4

from domain.downloadable_application_config import DownloadableApplicationConfig


class ApplicationType(Enum):
    DOWNLOADABLE = auto()


class ApplicationVersion(BaseModel):
    version_number: int
    config: DownloadableApplicationConfig


class Application(BaseModel):
    id: UUID4
    name: str
    type: ApplicationType
    versions: list[ApplicationVersion]
