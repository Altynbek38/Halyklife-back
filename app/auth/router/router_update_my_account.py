from fastapi import Depends, HTTPException
from app.auth.router.dependencies import parse_jwt_user_data
from . import router
from ..service import Service, get_service
from app.utils import AppModel
from ..adapters.jwt_service import JWTData


class UpdateUserRequest(AppModel):
    phone: str
    name: str
    city: str


@router.patch("/users/me")
def update_user_data(
    data: UpdateUserRequest,
    svc: Service = Depends(get_service),
    user: JWTData = Depends(parse_jwt_user_data),
):
    try:
        svc.repository.update_user(user.user_id, data.dict())
        return {"message": "User data updated successfully"}
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to update user data")

