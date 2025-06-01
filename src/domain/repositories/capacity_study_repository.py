from abc import ABC, abstractmethod
from typing import Optional, List
from ..entities.capacity_study import CapacityStudy

class ICapacityStudyRepository(ABC):
    """
    Interfaz para el repositorio de estudios de capacidad.
    Define las operaciones que debe implementar cualquier repositorio de estudios.
    """
    
    @abstractmethod
    def save(self, study: CapacityStudy) -> CapacityStudy:
        """Guarda un estudio de capacidad."""
        pass
        
    @abstractmethod
    def find_by_id(self, study_id: str) -> Optional[CapacityStudy]:
        """Busca un estudio por su ID."""
        pass
        
    @abstractmethod
    def find_by_ctq_id(self, ctq_id: str) -> List[CapacityStudy]:
        """Busca estudios para una CTQ específica."""
        pass
        
    @abstractmethod
    def delete(self, study_id: str) -> bool:
        """Elimina un estudio por su ID."""
        pass
        
    @abstractmethod
    def find_all(self) -> List[CapacityStudy]:
        """Devuelve todos los estudios."""
        pass