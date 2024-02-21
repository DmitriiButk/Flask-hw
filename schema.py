import pydantic
from typing import Optional


class CreateAnnouncement(pydantic.BaseModel):
    owner: str
    title: str
    description: str


class UpdateAnnouncement(pydantic.BaseModel):
    owner: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
