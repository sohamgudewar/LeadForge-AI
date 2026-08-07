from pydantic import BaseModel, Field, field_validator


class LeadRequest(BaseModel):
    company: str = Field(min_length=2, max_length=120)

    @field_validator("company", mode="before")
    @classmethod
    def normalize_company(cls, value):
        if not isinstance(value, str):
            return value
        return " ".join(value.split())
