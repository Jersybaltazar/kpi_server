from typing import Dict, List, Optional
from src.domain.entities.capacity_study import CapacityStudy
from src.domain.repositories.capacity_study_repository import ICapacityStudyRepository

class InMemoryCapacityStudyRepository(ICapacityStudyRepository):
    """
    Implementación en memoria del repositorio de estudios de capacidad.
    """
    
    def __init__(self):
        self._studies: Dict[str, CapacityStudy] = {}
        
    def save(self, study: CapacityStudy) -> CapacityStudy:
        """Guarda un estudio de capacidad en el repositorio."""
        self._studies[study.id] = study
        return study
        
    def find_by_id(self, study_id: str) -> Optional[CapacityStudy]:
        """Busca un estudio de capacidad por su ID."""
        return self._studies.get(study_id)
        
    def find_by_ctq_id(self, ctq_id: str) -> List[CapacityStudy]:
        """Busca todos los estudios para una CTQ específica."""
        return [study for study in self._studies.values() if study.ctq_id == ctq_id]
        
    def delete(self, study_id: str) -> bool:
        """Elimina un estudio de capacidad del repositorio."""
        if study_id in self._studies:
            del self._studies[study_id]
            return True
        return False
        
    def update(self, study: CapacityStudy) -> CapacityStudy:
        """Actualiza un estudio de capacidad existente."""
        if study.id not in self._studies:
            raise ValueError(f"Estudio con ID {study.id} no encontrado.")
        self._studies[study.id] = study
        return study
        
    def find_all(self) -> List[CapacityStudy]:
        """Devuelve todos los estudios de capacidad."""
        return list(self._studies.values())