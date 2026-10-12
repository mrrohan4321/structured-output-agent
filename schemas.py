from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ContactProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")  # extra field ashle reject

    name: str = Field(min_length=1)
    age: Optional[int] = Field(default=None, ge=0, le=130)
    skills: list[str] = Field(default_factory=list)
    email: Optional[EmailStr] = None