from fastapi import APIRouter

from api.v1.application import applications_router
from api.v1.host import hosts_router

v1_router = APIRouter(prefix="/v1", tags=["V1"])
v1_router.include_router(applications_router)
v1_router.include_router(hosts_router)
