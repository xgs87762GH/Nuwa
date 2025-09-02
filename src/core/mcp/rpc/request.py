from typing import Dict, Any

from pydantic import BaseModel

class JSONRPCRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: str | int | None = None
    method: str = "camera.take_photo"
    params: Dict[str, Any]
