from fastapi import APIRouter
from app.schemas.user import UserSignup, UserLogin, UserOut, TokenResponse
from app.services import auth_service
from app.core.dependencies import get_current_user
from fastapi import Depends
from app.middleware.rate_limiter import rate_limit

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=UserOut, dependencies=[Depends(rate_limit(10, 60))])
def signup(signup_data: UserSignup):
    return auth_service.signup(signup_data)

@router.post("/login", response_model=TokenResponse, dependencies=[Depends(rate_limit(10, 60))])
def login(login_data: UserLogin):
    return auth_service.login(login_data)

@router.get("/me", response_model=UserOut)
def get_me(current_user: dict = Depends(get_current_user)):
    return current_user
