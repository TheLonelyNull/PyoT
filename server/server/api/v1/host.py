from fastapi import APIRouter
from pydantic import UUID4

hosts_router = APIRouter(prefix="/host")


@hosts_router.get("/{host_id}")
async def get_host(host_id: UUID4):
    return []


@hosts_router.get("")
async def get_hosts():
    return []


@hosts_router.post("")
async def create_host():
    return


@hosts_router.patch("")
async def update_host():
    return


@hosts_router.delete("/{host_id}")
async def delete_host(host_id: UUID4):
    return


@hosts_router.post("/{host_id}/application")
async def add_host_application_instance(host_id: UUID4):
    return


@hosts_router.patch("/{host_id}/application")
async def update_host_application_instance(host_id: UUID4):
    return


@hosts_router.delete("/{host_id}/application/{application_instance_id}")
async def delete_host_application_instance(host_id: UUID4, application_instance_id: UUID4):
    return
