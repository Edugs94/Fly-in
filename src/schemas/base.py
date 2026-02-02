from pydantic import BaseModel, field_validator


class MapEntity(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if " " in v or "-" in v:
            raise ValueError(
                f"Invalid name '{v}': cannot " "contain dashes or spaces"
            )
        return v
