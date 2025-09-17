from dataclasses import dataclass, field
from typing import Any, List, Optional, Type
from pydantic import BaseModel

@dataclass
class TableSchema:
    """
    Defines the schema and location of a single table within a spreadsheet.
    
    Attributes:
        sheet_name (str): The name of the Excel sheet where the table is located.
        table_name (str): A unique name for the table (e.g., "companies_table").
        model (Type[BaseModel]): The Pydantic model for a single row in the table.
        header_row_index (int): The 0-indexed row number of the table's header.
        header_column_index (int): The 0-indexed column number of the table's first header cell.
        header_map (dict[str, str]): A mapping from the header text in the spreadsheet to the
                                     field names in the Pydantic model.
        data_start_row_index (Optional[int]): The 0-indexed row number where the data begins.
                                              If None, data starts on the row after the header.
    """
    sheet_name: str
    table_name: str
    model: Type[BaseModel]
    header_row_index: int
    header_column_index: int
    header_map: dict[str, str] = field(default_factory=dict)
    data_start_row_index: Optional[int] = None