from pydantic import BaseModel, EmailStr
from typing import Optional

class TeamRegister(BaseModel):
    name: str
    description: str | None = None
