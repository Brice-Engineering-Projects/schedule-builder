from fastapi import APIRouter

from schedule_builder.api.v1.routes_admin import router as admin_router
from schedule_builder.api.v1.routes_documents import router as documents_router
from schedule_builder.api.v1.routes_health import router as health_router
from schedule_builder.api.v1.routes_output import router as output_router
from schedule_builder.api.v1.routes_projects import router as projects_router
from schedule_builder.api.v1.routes_users import router as users_router
from schedule_builder.api.v1.routes_wbs import router as wbs_router
from schedule_builder.auth.routes import router as auth_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(health_router)
api_router.include_router(documents_router, prefix="/v1")
api_router.include_router(admin_router, prefix="/v1")
api_router.include_router(users_router, prefix="/v1")
api_router.include_router(wbs_router)
api_router.include_router(output_router)
api_router.include_router(projects_router)
