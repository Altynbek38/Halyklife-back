from app.config import database
from .repository.repository import History
from .adapters.openai_service import OpenAI


class Service:
    def __init__(self):
        self.repository = History(database)
        self.openai = OpenAI()


def get_service():
    svc = Service()
    return svc
