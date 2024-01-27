from fastapi import Depends, HTTPException, status
from pydantic import BaseModel

from ..service import Service, get_service
from . import router


class RegisterUserRequest(BaseModel):
    email: str
    password: str


class RegisterUserResponse(BaseModel):
    email: str


@router.post(
    "/users",
    status_code=status.HTTP_201_CREATED,
    response_model=RegisterUserResponse,
)
def register_user(
    request: RegisterUserRequest,
    svc: Service = Depends(get_service),
):
    if svc.repository.get_user_by_email(request.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already taken.",
        )

    svc.repository.create_user(request.dict())

    return RegisterUserResponse(email=request.email)