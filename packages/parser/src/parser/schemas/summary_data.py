from pydantic import BaseModel, Field, conlist, EmailStr
from typing import Any, List, Optional
from .base import TableSchema


class SubmitterInfo(BaseModel):
    name: Optional[str]
    organisation: Optional[str]
    email: Optional[str]


class Disaggregation(BaseModel):
    revenue_stream: Optional[str]
    government_agency: Optional[str]
    company: Optional[str]
    project: Optional[str]


class Sectors(BaseModel):
    oil: Optional[str]
    gas: Optional[str]
    mining: Optional[str]
    other: Optional[str]

# ------------------------------------
# Pydantic Models for each table row
# ------------------------------------

class SummaryAboutModel(BaseModel):
    """
    Pydantic model to hold the data from the '1_About' sheet.
    """
    country_or_area_name: Optional[str]
    iso_alpha_3: Optional[str]
    national_currency_name: Optional[str]
    national_currency_iso4217: Optional[str]

    start_date: Optional[str]   # For MVP1, keep as string (MVP2 can parse as date)
    end_date: Optional[str]

    sectors: Sectors
    number_reporting_government_entities: Optional[int]
    number_reporting_companies: Optional[int]

    exchange_rate_used: Optional[str]
    exchange_rate_source: Optional[str]

    disaggregation: Disaggregation
    submitter: SubmitterInfo


class ExplorationActivityRow(BaseModel):
    """
    Pydantic model for a single row in the 'Exploration activities' table.
    """
    commodity: str = Field(alias="Description")
    amount: float = Field(alias="Amount")
    source_units: str = Field(alias="Source / units")
    quality_grade: Optional[str] = Field(alias="Quality/Grade")
    comments: Optional[str] = Field(alias="Comments / Notes")

class ProductionByCommodityRow(BaseModel):
    """
    Pydantic model for a single row in the 'Production by commodity' table.
    """
    commodity: str = Field(alias="Description")
    amount: float = Field(alias="Amount")
    source_units: str = Field(alias="Source / units")
    quality_grade: Optional[str] = Field(alias="Quality/Grade")
    comments: Optional[str] = Field(alias="Comments / Notes")

class ExportsRow(BaseModel):
    """
    Pydantic model for a single row in the 'Exports' table.
    """
    commodity: str = Field(alias="Description")
    amount: float = Field(alias="Amount")
    source_units: str = Field(alias="Source / units")
    quality_grade: Optional[str] = Field(alias="Quality/Grade")
    comments: Optional[str] = Field(alias="Comments / Notes")

class EconomicContributionRow(BaseModel):
    """
    Pydantic model for a single row in the 'Economic contribution' table.
    """
    indicator: str = Field(alias="Description")
    amount: float = Field(alias="Amount")
    source_units: str = Field(alias="Source / units")
    quality_grade: Optional[str] = Field(alias="Quality/Grade")
    comments: Optional[str] = Field(alias="Comments / Notes")
    
class ReportingGovernmentEntityRow(BaseModel):
    """
    Pydantic model for a single row in the '(A) Reporting government entities list' table.
    """
    full_name_of_entity: str = Field(alias="Full name of entity")
    entity_type: str = Field(alias="Entity type")
    id_number: Optional[str] = Field(alias="ID number (if applicable)")
    total_reported: Optional[float] = Field(alias="Total reported")
    submitted_data_to_eiti: Optional[bool] = Field(alias="Submitted data to EITI?")
    subjected_to_audit_standards: Optional[bool] = Field(alias="Subjected to audit standards?")
    adhered_to_msg_quality: Optional[bool] = Field(alias="Adhered to MSG's quality assurance requirements?")

class ReportingCompanyIDRow(BaseModel):
    company_id_type: str = Field(alias="Company ID type")
    issuer: str = Field(alias="Issuer")
    link: Optional[str] = Field(alias="Link")

class ReportingCompanyRow(BaseModel):
    """
    Pydantic model for a single row in the '(B) Reporting companies' list' table.
    """
    company_name: Optional[str] = Field(alias="Company name")
    is_EITI_Supporting: Optional[bool] = Field(alias="Is the company an EITI Supporting company?")
    company_type: Optional[str] = Field(alias="Company type")
    company_id: Optional[str] = Field(alias="Company ID number")
    sector: Optional[str] = Field(alias="Sector")
    commodities: Optional[str] = Field(alias="Commodities (common-expected)")
    total_payments_to_government: Optional[float] = Field(alias="Total payments to Government")
    stock_exchange_listing: Optional[str] = Field(alias="Stock exchange listing or company website")
    submitted_data_to_eiti: Optional[bool] = Field(alias="Submitted data to EITI?")
    subjected_to_audit_standards: Optional[bool] = Field(alias="Subjected to audit standards for fiscal year covered?")
    adhered_to_msg_quality: Optional[bool] = Field(alias="Adhered to MSG's quality assurance requirement?")

class ReportingProjectRow(BaseModel):
    """
    Pydantic model for a single row in the 'Projects' table.
    """
    project_name: str = Field(alias="Full Project name")
    legal_agreement_ref_num: Optional[str] = Field(alias="Legal agreement reference number(s): contract, licence, lease, concession, …")
    start_date: Optional[str] = Field(alias="Start Date")
    expiry_date: Optional[str] = Field(alias="Expiry Date")
    affiliated_companies: Optional[str] = Field(alias="Affiliated companies, start with Operator")
    commodities: Optional[str] = Field(alias="Commodities (one commodity/row)")
    status: Optional[str] = Field(alias="Status")
    production_volume: Optional[float] = Field(alias="Production (volume)")
    unit: Optional[str] = Field(alias="Unit")
    production_value: Optional[float] = Field(alias="Production (value)")
    currency: Optional[str] = Field(alias="Currency")
    costs_capex: Optional[float] = Field(alias="Costs -Capex-")
    costs_opex: Optional[float] = Field(alias="Costs -Opex-")
    cost_currency: Optional[str] = Field(alias="Cost currency")
    ghg_emmisions: Optional[float] = Field(alias="GHG Emissions")
    emmisions_unit: Optional[str] = Field(alias="Emissions unit")

class ExtractiveRevenueRow(BaseModel):
    """
    Pydantic model for a single row in the 'Extractive revenue' table.
    """
    gfs_classification: str = Field(alias="GFS classification")
    sector: str = Field(alias="Sector")
    revenue_stream_name: str = Field(alias="Revenue stream name")
    legal_basis: Optional[str] = Field(alias="Legal basis")
    issuing_government_entity: Optional[str] = Field(alias="Issuing government entity")
    final_recipient: Optional[str] = Field(alias="Final recipient")
    revenue_value: Optional[float] = Field(alias="Revenue value")
    currency: Optional[str] = Field(alias="Currency")

class ExcludedRevenueRow(BaseModel):
    """
    Pydantic model for a single row in the 'Excluded revenue' table.
    """
    sector: str = Field(alias="Sector")
    revenue_stream_name: str = Field(alias="Revenue stream name")
    government_entity: Optional[str] = Field(alias="Government entity")
    revenue_value: Optional[float] = Field(alias="Revenue value")
    currency: Optional[str] = Field(alias="Currency")

class GovernmentRevenueRow(BaseModel):
    """
    Pydantic model for a single row in the 'Government revenue' table.
    """
    company: str = Field(alias="Company")
    issuing_government_entity: str = Field(alias="Issuing government entity")
    revenue_stream_name: str = Field(alias="Revenue stream name")
    levied_on_project: Optional[str] = Field(alias="Levied on project (Y/N)")
    reported_on_project: Optional[str] = Field(alias="Reported on project (Y/N)")
    project_name: Optional[str] = Field(alias="Project name (if applicable)")
    reporting_currency: Optional[str] = Field(alias="Reporting currency")
    revenue_value: Optional[float] = Field(alias="Revenue value")
    payment_made_in_kind: Optional[bool] = Field(alias="Payment made in kind (Y/N)")
    in_kind_volume: Optional[float] = Field(alias="In-kind volume (if applicable)")
    unit: Optional[str] = Field(alias="Unit (if applicable)")
    comments: Optional[str] = Field(alias="Comments")

# ------------------------------------
# Concrete TableSchema instances
# ------------------------------------


ABOUT_SCHEMA = TableSchema(
    sheet_name="1_About",
    table_name="about",
    model=SummaryAboutModel,
    header_map={
        "Country or area name": "country_or_area_name",
        "ISO Alpha-3 Code": "iso_alpha_3_code",
        "National currency name": "national_currency_name",
        "National currency ISO-4217": "national_currency_iso_4217",
        "Start Date": "start_date",
        "End Date": "end_date",
        "Disclosures cover the following sectors:": "sectors",
        "Number of reporting companies (incl SOEs if payer)": "reporting_companies_count",
        "Name": "name",
        "Organisation": "organisation",
        "Email address": "email_address",
    },
    header_row_index=None,
    header_column_index=None,
    data_start_row_index=None,
)

EXPLORATION_SCHEMA = TableSchema(
    sheet_name="2_Economic contribution",
    table_name="exploration_activities",
    model=ExplorationActivityRow,
    header_row_index=14,
    header_column_index=1,
    header_map={
        "Description": "commodity",
        "Amount": "amount",
        "Source / units": "source_units",
        "Quality/Grade": "quality_grade",
        "Comments / Notes": "comments",
    },
    data_start_row_index=20,
)

PRODUCTION_SCHEMA = TableSchema(
    sheet_name="2_Economic contribution",
    table_name="production_by_commodity",
    model=ProductionByCommodityRow,
    header_row_index=15,
    header_column_index=1,
    header_map={
        "Description": "commodity",
        "Amount": "amount",
        "Source / units": "source_units",
        "Quality/Grade": "quality_grade",
        "Comments / Notes": "comments",
    },
    data_start_row_index=32,
)

EXPORTS_SCHEMA = TableSchema(
    sheet_name="2_Economic contribution",
    table_name="exports",
    model=ExportsRow,
    header_row_index=2,
    header_column_index=1,
    header_map={
        "Description": "commodity",
        "Amount": "amount",
        "Source / units": "source_units",
        "Quality/Grade": "quality_grade",
        "Comments / Notes": "comments",
    },
    data_start_row_index=55,
)

ECONOMIC_CONTRIBUTION_SCHEMA = TableSchema(
    sheet_name="2_Economic contribution",
    table_name="economic_contribution",
    model=EconomicContributionRow,
    header_row_index=15,
    header_column_index=1,
    header_map={
        "Description": "indicator",
        "Amount": "amount",
        "Source / units": "source_units",
        "Quality/Grade": "quality_grade",
        "Comments / Notes": "comments",
    },
    data_start_row_index=75,
)

REPORTING_GOVERNMENT_ENTITIES_SCHEMA = TableSchema(
    sheet_name="3_Entities and projects List",
    table_name="reporting_government_entities",
    model=ReportingGovernmentEntityRow,
    header_row_index=14,
    header_column_index=1,
    header_map={
        "Full name of entity": "full_name_of_entity",
        "Entity type": "entity_type",
        "ID number (if applicable)": "id_number",
        "Total reported": "total_reported",
        "Submitted data to EITI?": "submitted_data_to_eiti",
        "Subjected to audit standards?": "subjected_to_audit_standards",
        "Adhered to MSG's quality assurance requirements?": "adhered_to_msg_quality",
    },
    data_start_row_index=15,
)

REPORTING_COMPANIES_ID_SCHEMA = TableSchema(
    sheet_name="3_Entities and projects List",
    table_name="reporting_companies_id",
    model=ReportingCompanyIDRow,
    header_row_index=24,
    header_column_index=1,
    header_map={
        "Company ID type": "company_id_type",
        "Issuer": "issuer",
        "Link": "link",
    },
    data_start_row_index=25,
)

REPORTING_COMPANIES_SCHEMA = TableSchema(
    sheet_name="3_Entities and projects List",
    table_name="reporting_companies",
    model=ReportingCompanyRow,
    header_row_index=28,
    header_column_index=1,
    header_map={
        "Company name": "company_name",
        "Is the company an EITI Supporting company?": "is_EITI_Supporting",
        "Company type": "company_type",
        "Company ID number": "company_id",
        "Sector": "sector",
        "Commodities (common-expected)": "commodities",
        "Total payments to Government": "total_payments_to_government",
        "Stock exchange listing or company website": "stock_exchange_listing",
        "Submitted data to EITI?": "submitted_data_to_eiti",
        "Subjected to audit standards for fiscal year covered?": "subjected_to_audit_standards",
        "Adhered to MSG's quality assurance requirement?": "adhered_to_msg_quality",
    },
    data_start_row_index=29,
)

REPORTING_PROJECTS_SCHEMA = TableSchema(
    sheet_name="3_Entities and projects List",
    table_name="reporting_projects",
    model=ReportingProjectRow,
    header_row_index=37,
    header_column_index=1,
    header_map={
        "Full Project name": "project_name",
        "Legal agreement reference number(s): contract, licence, lease, concession, …": "legal_agreement_ref_num",
        "Start Date": "start_date",
        "Expiry Date": "expiry_date",
        "Affiliated companies, start with Operator": "affiliated_companies",
        "Commodities (one commodity/row)": "commodities",
        "Status": "status",
        "Production (volume)": "production_volume",
        "Unit": "unit",
        "Production (value)": "production_value",
        "Currency": "currency",
        "Costs -Capex-": "costs_capex",
        "Costs -Opex-": "costs_opex",
        "Cost currency": "cost_currency",
        "GHG Emissions": "ghg_emmisions",
        "Emissions unit": "emmisions_unit",
    },
    data_start_row_index=38,
)

EXTRACTIVE_REVENUES_SCHEMA = TableSchema(
    sheet_name="4_Extractive revenues -full-",
    table_name="extractive_revenues",
    model=ExtractiveRevenueRow,
    header_row_index=25,
    header_column_index=5,
    header_map={
        "GFS classification": "gfs_classification",
        "Sector": "sector",
        "Revenue stream name": "revenue_stream_name",
        "Legal basis": "legal_basis",
        "Issuing government entity": "issuing_government_entity",
        "Final recipient": "final_recipient",
        "Revenue value": "revenue_value",
        "Currency": "currency",
    },
    data_start_row_index=26,
)

EXCLUDED_REVENUES_SCHEMA = TableSchema(
    sheet_name="4_Extractive revenues -full-",
    table_name="excluded_revenues",
    model=ExcludedRevenueRow,
    header_row_index=66,
    header_column_index=6,
    header_map={
        "Sector": "sector",
        "Revenue stream name": "revenue_stream_name",
        "Government entity": "government_entity",
        "Revenue value": "revenue_value",
        "Currency": "currency",
    },
    data_start_row_index=67,
)

GOVERNMENT_REVENUES_SCHEMA = TableSchema(
    sheet_name="5_Gov revenues (comp+proj)",
    table_name="government_revenues",
    model=GovernmentRevenueRow,
    header_row_index=13,
    header_column_index=2,
    header_map={
        "Company": "company",
        "Issuing government entity": "issuing_government_entity",
        "Revenue stream name": "revenue_stream_name",
        "Levied on project (Y/N)": "levied_on_project",
        "Reported on project (Y/N)": "reported_on_project",
        "Project name (if applicable)": "project_name",
        "Reporting currency": "reporting_currency",
        "Revenue value": "revenue_value",
        "Payment made in kind (Y/N)": "payment_made_in_kind",
        "In-kind volume (if applicable)": "in_kind_volume",
        "Unit (if applicable)": "unit",
        "Comments": "comments",
    },
    data_start_row_index=14,
)

# List of all schemas for a given file type.
# SUMMARY_DATA_V1_SCHEMAS = []
# SUMMARY_DATA_V2_SCHEMAS = []

SUMMARY_DATA_V2P1_SCHEMAS = [
    ABOUT_SCHEMA, 
    EXPLORATION_SCHEMA, 
    PRODUCTION_SCHEMA, 
    EXPORTS_SCHEMA, 
    ECONOMIC_CONTRIBUTION_SCHEMA,
    REPORTING_GOVERNMENT_ENTITIES_SCHEMA,
    REPORTING_COMPANIES_ID_SCHEMA,
    REPORTING_COMPANIES_SCHEMA,
    REPORTING_PROJECTS_SCHEMA,
    EXTRACTIVE_REVENUES_SCHEMA,
    EXCLUDED_REVENUES_SCHEMA,
    GOVERNMENT_REVENUES_SCHEMA
]