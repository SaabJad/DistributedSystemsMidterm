from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from datetime import datetime


class RawPage(BaseModel):
    url: str
    status: int
    html: str
    fetched_at: datetime = Field(default_factory=datetime.utcnow)


class ParsedPage(BaseModel):
    url: str
    fetched_at: datetime
    title: Optional[str] = None
    main_text: Optional[str] = None
    links: List[str] = []
    metadata: Dict[str, str] = {}


