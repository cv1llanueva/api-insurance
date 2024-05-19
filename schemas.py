from pydantic import BaseModel, constr
from datetime import date, datetime 
from typing import Optional

class DocumentType(BaseModel):
    id: int
    description: str

class DocumentTypeInput(BaseModel):
    id: int

class ClaimCreate(BaseModel):
    policyId: int
    claimDate: date
    description: str

class ClaimOutput(BaseModel):
    claimId: int
    policyId: int
    claimDate: date
    description: str
    status: str