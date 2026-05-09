from typing import Optional, Dict, List
from datetime import datetime
from pydantic import BaseModel, Field


class GraphCreateRequest(BaseModel):
    walk_threshold_m: Optional[int] = Field(200, ge=10, le=5000)
    save: Optional[bool] = True
    name: Optional[str] = None


class GraphMetadata(BaseModel):
    id: str
    filename: str
    created_at: datetime
    params: Dict
    nodes_count: int
    edges_count: int


class GraphListResponse(BaseModel):
    total: int
    page: int
    per_page: int
    items: List[GraphMetadata]
