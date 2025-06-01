from abc import ABC, abstractmethod
from typing import Optional, List
from ..entities.ctq import CTQ  # Importación relativa desde el dominio

class ICTQRepository(ABC):
    """
    Interfaz para el repositorio de CTQ (Critical to Quality).
    Define las operaciones que debe implementar cualquier repositorio de CTQ.
    """
    
    @abstractmethod
    def save(self, ctq: CTQ) -> None:
        """Guarda una CTQ en el repositorio."""
        pass
        
    @abstractmethod
    def find_by_id(self, ctq_id: str) -> Optional[CTQ]:
        """Busca una CTQ por su ID."""
        pass
        
    @abstractmethod
    def find_by_process_id(self, process_id: str) -> List[CTQ]:
        """Busca todas las CTQs para un proceso específico."""
        pass
        
    @abstractmethod
    def find_all(self) -> List[CTQ]:
        """Devuelve todas las CTQs almacenadas."""
        pass