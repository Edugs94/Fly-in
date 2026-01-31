from pydantic import BaseModel, ConfigDict


class AppBaseModel(BaseModel):
    """Base class"""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
