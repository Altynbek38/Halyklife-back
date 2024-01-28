from fastapi import Depends
from app.utils import AppModel
from ..service import Service, get_service
from starlette.responses import StreamingResponse
from . import router


class MessageRequest(AppModel):
    iin: str
    guid: str


@router.post("/check_certificate")
def check_certificate(
    message_request: MessageRequest,
    svc: Service = Depends(get_service),
):  
    iin = message_request.iin
    guid = message_request.guid

    return svc.repository.check_certificate(iin, guid)