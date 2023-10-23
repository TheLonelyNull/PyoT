from pydantic import BaseModel
from pydantic_core import Url


class DownloadableApplicationConfig(BaseModel):
    link: Url
    post_download_command: list[str]
    run_command: list[str]
    healthcheck_command: list[str]