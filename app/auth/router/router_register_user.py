from fastapi import Depends, HTTPException, status
from pydantic import BaseModel
from ..service import Service, get_service
import httpx
from . import router


class RegisterUserRequest(BaseModel):
    email: str
    password: str
    iin: str
    phone_number: str

class RegisterUserResponse(BaseModel):
    email: str


@router.post(
    "/users/registration",
    status_code=status.HTTP_201_CREATED,
    response_model=RegisterUserResponse,
)
async def register_user(
    request: RegisterUserRequest,
    svc: Service = Depends(get_service),
):
    if svc.repository.get_user_by_email(request.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already taken.",
        )


    api_url = "https://fastapi-5lcu.onrender.com/damumed/check_user"

    data = {"iin": request.iin}

    async with httpx.AsyncClient() as client:
        response = await client.post(api_url, json=data)

    if response.is_error:
        raise HTTPException(status_code=response.status_code, detail="Error from external API")

    if response.status_code == 404:
            raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="IIN not found",
        )

    svc.repository.create_user(request.dict())

    return RegisterUserResponse(email=request.email)