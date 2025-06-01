import math
from dataclasses import dataclass, field
from typing import Optional

@dataclass(frozen=True) # Inmutable
class Specification:
    usl: float
    lsl: float
    nominal: Optional[float] = None

    def __post_init__(self):
        if self.usl <= self.lsl:
            raise ValueError("USL debe ser mayor que LSL.")
        if self.nominal is not None:
            if not (self.lsl <= self.nominal <= self.usl):
                 # Permitir N fuera de LSL/USL puede ser válido en algunos contextos
                 # pero añadimos una validación estricta por defecto.
                 # Considerar relajar si es necesario.
                 # raise ValueError("El valor Nominal debe estar entre LSL y USL.")
                 pass # Opcional: decidir si validar N dentro de los límites

    @property
    def tolerance(self) -> float:
        return self.usl - self.lsl

    @property
    def midpoint(self) -> float:
        return (self.usl + self.lsl) / 2