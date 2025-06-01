from pydantic import BaseModel, Field
from typing import Optional

# Schema para el cuerpo de la solicitud de creación de CTQ
class CTQCreationRequest(BaseModel):
    process_id: str = Field(..., example="PROC-SAMPLE-001")
    name: str = Field(..., min_length=1, example="Longitud de Capa")
    unit: str = Field(..., min_length=1, example="mm")
    usl: float = Field(..., description="Límite Superior de Especificación (ES)")
    lsl: float = Field(..., description="Límite Inferior de Especificación (EI)")
    nominal: Optional[float] = Field(None, description="Valor Nominal (N), opcional")

# Schema para la respuesta de especificación (anidado)
class SpecificationResponse(BaseModel):
    usl: float
    lsl: float
    nominal: Optional[float]
    tolerance: float # Propiedad calculada, útil en la respuesta
    midpoint: float  # Propiedad calculada

    class Config:
        from_attributes = True # Para mapear desde el objeto Specification

# Schema para la respuesta al crear o solicitar una CTQ
class CTQResponse(BaseModel):
    id: str
    process_id: str
    process_name: Optional[str] = Field(None, title="Nombre del proceso asociado")
    name: str
    unit: str
    specification: SpecificationResponse # Usar el schema anidado

    class Config:
        from_attributes = True # Para mapear desde la entidad CTQ