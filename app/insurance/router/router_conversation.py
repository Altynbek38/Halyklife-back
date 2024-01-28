from fastapi import Depends
from app.utils import AppModel
from ..service import Service, get_service
from . import router

class Request(AppModel):
    user_query: str

@router.post("/conversation")
def conversation(request_data: Request, svc: Service = Depends(get_service)):
    user_query = request_data.user_query

    result = svc.openai.get_bot_response(user_query=user_query)

    return result