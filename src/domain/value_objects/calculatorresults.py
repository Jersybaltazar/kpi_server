from dataclasses import dataclass, field
from typing import Any, Optional, Dict, List

@dataclass()
class Interpretation:
    cp: Optional[str] = None
    cpk: Optional[str] = None
    k: Optional[str] = None
    cpm: Optional[str] = None
    dpmo: Optional[str] = None
    sigma: Optional[str] = None
    yield_value: Optional[str] = None
    general: List[str] = field(default_factory=list)

@dataclass()
class CalculatedIndices:
    # Índices siempre calculables (si std_dev > 0)
    cp: Optional[float] = None
    cr: Optional[float] = None
    cpi: Optional[float] = None
    cps: Optional[float] = None
    cpk: Optional[float] = None
    # Índices que dependen de Nominal (N)
    k: Optional[float] = None
    tau: Optional[float] = None
    cpm: Optional[float] = None
    dpmo: Optional[float] = None
    yield_value: Optional[float] = None
    sigma_level: Optional[float] = None

    
    interpretation: Dict[str, Any] = field(default_factory=dict)
    histogram: Dict[str, List[int]] = field(default_factory=dict) 
    errors: List[str] = field(default_factory=list)

    def __post_init__(self):
        if self.errors is None:
            self.errors = []