from fastapi import APIRouter
from pydantic import UUID4

applications_router = APIRouter(prefix="/application")


@applications_router.get("/{application_id}")
async def get_application(application_id: UUID4):
    return []


@applications_router.get("")
async def get_applications():
    return []


@applications_router.post("")
async def create_application():
    return


@applications_router.patch("")
async def update_application():
    return


@applications_router.delete("/{application_id}")
async def delete_application(application_id: UUID4):
    return
