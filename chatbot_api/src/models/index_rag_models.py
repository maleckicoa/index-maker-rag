from pydantic import BaseModel
from typing import List, Optional, Any

class IndexQueryInput(BaseModel):
    text: str
    #tickers: Optional[List] = None 

class IndexQueryOutput(BaseModel):
    input: str
    output: Optional[Any] = None
    intermediate_steps: Optional[Any] = None
    result: Optional[Any] = None
    tickers: Optional[Any] = None
    memory: Optional[Any] = None
