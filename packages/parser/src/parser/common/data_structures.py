from dataclasses import dataclass, field
from enum import Enum
from typing import Any, List

class ErrorCode(str, Enum):
    UNKNOWN = "unknown"
    STRUCTURE = "structure"
    DATA_TYPE = "data_type"

@dataclass
class ValidationError:
    code: ErrorCode
    message: str
    row: int | None = None
    column: str | None = None


@dataclass
class DiagnosticsReport:
    errors: List[ValidationError] = field(default_factory=list)
    cleaning_log: List[str] = field(default_factory=list)


@dataclass
class UserReport:
    about: dict
    economic_contribution: dict
    entities_and_projects: dict
    extractive_revenues: dict
    gov_revenues: dict
    errors: list = []
    cleaning_log: list = []