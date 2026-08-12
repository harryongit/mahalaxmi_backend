from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.exceptions import register_exception_handlers

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS
origins = [o.strip() for o in settings.BACKEND_CORS_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME} API"}

@app.get("/health")
async def health():
    return {"status": "healthy", "version": settings.VERSION}

from app.api.v1 import auth, users, services, orders, payments, enquiries
from app.api.v1.admin import dashboard, users as admin_users

app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
app.include_router(services.router, prefix=f"{settings.API_V1_STR}/services", tags=["services"])
app.include_router(orders.router, prefix=f"{settings.API_V1_STR}/orders", tags=["orders"])
app.include_router(payments.router, prefix=f"{settings.API_V1_STR}/payments", tags=["payments"])
app.include_router(enquiries.router, prefix=f"{settings.API_V1_STR}/enquiries", tags=["enquiries"])

# Admin routes
from app.api.v1.admin import auth as admin_auth
app.include_router(admin_auth.router, prefix=f"{settings.API_V1_STR}/admin/auth", tags=["admin-auth"])
app.include_router(dashboard.router, prefix=f"{settings.API_V1_STR}/admin/dashboard", tags=["admin-dashboard"])
app.include_router(admin_users.router, prefix=f"{settings.API_V1_STR}/admin/users", tags=["admin-users"])





