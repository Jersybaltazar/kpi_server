from typing import Optional, List, Dict
from src.domain.entities.ctq import CTQ
from src.domain.repositories.ctq_repository import ICTQRepository



class InMemoryCTQRepository(ICTQRepository):
    def __init__(self):
        self._ctqs: Dict[str, CTQ] = {}

    def save(self, ctq: CTQ) -> None:
        self._ctqs[ctq.id] = ctq
        print(f"DEBUG: Guardada CTQ {ctq.id} en memoria.") # Logging simple

    def find_by_id(self, ctq_id: str) -> Optional[CTQ]:
        return self._ctqs.get(ctq_id)
    
    def find_all(self) -> List[CTQ]:
        """Devuelve todas las CTQs almacenadas."""
        return list(self._ctqs.values())
    
    def find_by_process_id(self, process_id: str) -> List[CTQ]:
        return [ctq for ctq in self._ctqs.values() if ctq.process_id == process_id]