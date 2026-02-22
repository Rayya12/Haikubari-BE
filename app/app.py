from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.schema.authSchema import UserRead, UserCreate, UserUpdate
from app.users import auth_backend, current_active_user,fastapi_users
from app.router.otp import router as otp_router
from app.router.health import router as health_router
from app.router.haikuRouter import router as haiku_router
from app.router.reviewRouter import router as review_router
from app.router.likeRouter import router as like_router
from app.router.UserRouter import router as user_router
from app.router.imageRouter import router as image_router

origins = ["*"]

app = FastAPI()
app.include_router(fastapi_users.get_auth_router(auth_backend),prefix='/auth/jwt',tags=["auth"])
app.include_router(fastapi_users.get_register_router(UserRead,UserCreate),prefix="/auth",tags=["auth"])
app.include_router(fastapi_users.get_reset_password_router(),prefix="/auth",tags=["auth"])
app.include_router(fastapi_users.get_verify_router(UserRead),prefix="/auth",tags=["auth"])
app.include_router(otp_router)
app.include_router(health_router)
app.include_router(haiku_router)
app.include_router(review_router)
app.include_router(like_router)
app.include_router(user_router)
app.include_router(image_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"Hello": "World"}


