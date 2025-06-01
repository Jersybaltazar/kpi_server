from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Schema para creación de estudios
class StudyCreationRequest(BaseModel):
    raw_measurements: List[float] = Field(..., min_items=2, description="Lista de mediciones numéricas crudas del proceso")
    study_date_override: Optional[str] = Field(None, description="Fecha opcional en formato ISO (YYYY-MM-DDTHH:MM:SS) para el estudio")
    opportunities_per_unit: Optional[int] = Field(1, description="Oportunidades de defecto por unidad (default=1)")

# Schema para respuestas anidadas (simplificados)
class InputDataSummaryResponse(BaseModel):
    mean: float
    std_dev: float
    sample_size: int

class CalculationResultsResponse(BaseModel):
    cp: Optional[float] = None
    cr: Optional[float] = None
    cpi: Optional[float] = None
    cps: Optional[float] = None
    cpk: Optional[float] = None
    k: Optional[float] = None
    cpm: Optional[float] = None
    interpretation: Dict[str, str] = Field(default_factory=dict)
    histogram: Dict[str, List[float]] = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)

class StudyResponse(BaseModel):
    id: str
    ctq_id: str
    study_date: datetime
    mean: Optional[float] = None
    std_dev: Optional[float] = None
    sample_size: Optional[int] = None
    # Índices tradicionales
    cp: Optional[float] = None
    cr: Optional[float] = None
    cpi: Optional[float] = None
    cps: Optional[float] = None
    cpk: Optional[float] = None
    k: Optional[float] = None
    cpm: Optional[float] = None
    # Índices Six Sigma
    dpmo: Optional[float] = None
    yield_value: Optional[float] = None
    sigma_level: Optional[float] = None
    # Datos adicionales
    interpretation: Dict[str, str] = Field(default_factory=dict)
    histogram: Dict[str, List[float]] = Field(default_factory=dict)
    # Campos anidados
    input_data: Optional[InputDataSummaryResponse] = None
    results: Optional[CalculationResultsResponse] = None

    class Config:
        orm_mode = True
    
    @classmethod
    def from_entity(cls, entity):
        """Crea un StudyResponse a partir de una entidad CapacityStudy"""
        # Asegurarse de que interpretation sea un diccionario de strings
        interpretation = {}
        if entity.interpretation:
            for key, value in entity.interpretation.items():
                interpretation[key] = str(value) if value is not None else ""
                
        # Asegurarse de que histogram tenga la estructura correcta
        histogram = entity.histogram or {"bins": [], "counts": []}
        
        # Crear el objeto InputDataSummaryResponse
        input_data = InputDataSummaryResponse(
            mean=entity.mean or 0.0,
            std_dev=entity.std_dev or 0.0,
            sample_size=entity.sample_size or 0
        )
        
        # Crear el objeto CalculationResultsResponse
        results = CalculationResultsResponse(
            cp=entity.cp,
            cr=entity.cr,
            cpi=entity.cpi,
            cps=entity.cps,
            cpk=entity.cpk,
            k=entity.k,
            cpm=entity.cpm,
            interpretation=interpretation,
            histogram=histogram,
            errors=[]
        )
        
        return cls(
            id=entity.id,
            ctq_id=entity.ctq_id,
            study_date=entity.study_date,
            mean=entity.mean,
            std_dev=entity.std_dev,
            sample_size=entity.sample_size,
            cp=entity.cp,
            cr=entity.cr,
            cpi=entity.cpi,
            cps=entity.cps,
            cpk=entity.cpk,
            k=entity.k,
            cpm=entity.cpm,
            dpmo=entity.dpmo,
            yield_value=entity.yield_value,
            sigma_level=entity.sigma_level,
            interpretation=interpretation,
            histogram=histogram,
            input_data=input_data,
            results=results
        )