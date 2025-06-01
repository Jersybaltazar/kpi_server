from dataclasses import dataclass, field
import uuid
from datetime import datetime
from typing import Optional, List,Dict, Any
from src.domain.value_objects.calculatorresults import CalculatedIndices


@dataclass
class InputDataSummary:
    mean: float
    std_dev: float
    sample_size: Optional[int] = None

@dataclass
class CapacityStudy:
    """
    Representa un estudio de capacidad de proceso para una CTQ.
    """
    def __init__(
        self,
        id: Optional[str] = None,
        ctq_id: str = None,
        study_date: datetime = None,
        input_data: InputDataSummary = None,
        results: Any = None
    ):
        self.id = id or str(uuid.uuid4())
        self.ctq_id = ctq_id
        self.study_date = study_date or datetime.now()
        
        # Datos de entrada
        if input_data:
            self.mean = input_data.mean
            self.std_dev = input_data.std_dev
            self.sample_size = input_data.sample_size
        else:
            self.mean = None
            self.std_dev = None
            self.sample_size = 0
            
        # Resultados calculados (tradicionales)
        self.cp = results.cp if results else None
        self.cr = results.cr if results else None
        self.cpi = results.cpi if results else None
        self.cps = results.cps if results else None
        self.cpk = results.cpk if results else None
        self.k = results.k if results else None
        self.cpm = results.cpm if results else None
        
        # Resultados calculados (nuevos índices Six Sigma)
        self.dpmo = results.dpmo if results else None
        self.yield_value = results.yield_value if results else None
        self.sigma_level = results.sigma_level if results else None
        
        # Interpretaciones y datos adicionales
        self.interpretation = results.interpretation if results else {}
        self.histogram = results.histogram if results else {"bins": [], "counts": []}

    def to_dict(self) -> Dict:
        """Convierte la entidad a un diccionario para serialización."""
        return {
            'id': self.id,
            'ctq_id': self.ctq_id,
            'study_date': self.study_date,
            'mean': self.mean,
            'std_dev': self.std_dev,
            'sample_size': self.sample_size,
            # Índices tradicionales
            'cp': self.cp,
            'cr': self.cr,
            'cpi': self.cpi,
            'cps': self.cps,
            'cpk': self.cpk,
            'k': self.k,
            'cpm': self.cpm,
            # Nuevos índices Six Sigma
            'dpmo': self.dpmo,
            'yield_value': self.yield_value,
            'sigma_level': self.sigma_level,
            # Datos adicionales
            'interpretation': self.interpretation,
            'histogram': self.histogram
        }