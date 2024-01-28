from fastapi import Depends
from app.utils import AppModel
from ..service import Service, get_service
from . import router

class Request(AppModel):
    iin: str

@router.post("/check_user")
def check_user(request_data: Request, svc: Service = Depends(get_service)):
    iin = request_data.iin


    result = svc.repository.check_by_iin(user_iin = iin)

    return result