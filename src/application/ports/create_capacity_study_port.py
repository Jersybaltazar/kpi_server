from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
from ...domain.entities.capacity_study import CapacityStudy # Referencia relativa válida

@dataclass
class CreateCapacityStudyCommand:
    """Comando para crear un estudio a partir de datos crudos."""
    ctq_id: str
    raw_measurements: List[float] # <- Cambio clave: Lista de mediciones
    study_date_override: Optional[str] = None # Opcional para permitir fechas específicas
    opportunities_per_unit: int = 1
    
class ICreateCapacityStudy(ABC):
    @abstractmethod
    def execute(self, command: CreateCapacityStudyCommand) -> CapacityStudy:
        """
        Ejecuta el comando para analizar datos crudos y crear un estudio.

        Args:
            command: El comando con el ID de la CTQ y las mediciones crudas.

        Returns:
            La entidad CapacityStudy creada con los resultados calculados.

        Raises:
            ValueError: Si los datos son inválidos, insuficientes o la CTQ no existe.
            StatisticsError: Si no se pueden calcular las estadísticas (ej. < 2 puntos).
        """
        pass
    @abstractmethod
    def get_studies_by_ctq(self, ctq_id: str) -> list:
        """
        Devuelve todos los estudios de capacidad asociados a una CTQ.
        """
        pass    