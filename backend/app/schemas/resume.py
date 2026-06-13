from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ResumeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    file_name: str
    storage_path: str
    file_url: str | None
    extracted_text: str | None
    created_at: datetime
    updated_at: datetime
