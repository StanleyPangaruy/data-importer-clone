from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class ErrorCode(str, Enum):
    GENERIC_ERROR = "GENERIC_ERROR"

class ValidationError(BaseModel):
    code: ErrorCode
    message: str
    row_index: Optional[int] = None
    column_index: Optional[int] = None
    cell_value: Optional[Any] = None

class DiagnosticsReport(BaseModel):
    errors: List[ValidationError] = Field(default_factory=list)

class UserReport(BaseModel):
    extracted_data: Dict[str, Any]
    diagnostics: DiagnosticsReport = Field(default_factory=DiagnosticsReport)
    cleaning_log: List[Any] = Field(default_factory=list)