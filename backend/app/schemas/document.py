from datetime import datetime

from pydantic import BaseModel


class DocumentCreate(BaseModel):
    filename: str


class DocumentResponse(BaseModel):

    id: int
    filename: str
    upload_date: datetime

    model_config = {
        "from_attributes": True
    }