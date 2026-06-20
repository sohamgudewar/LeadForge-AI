from pydantic import BaseModel


class LeadRequest(BaseModel):
    company: str
