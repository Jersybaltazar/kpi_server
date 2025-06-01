from abc import ABC, abstractmethod
from typing import Optional, List
from ..entities.process import Process  # Importación relativa desde el dominio

class IProcessRepository(ABC):
    """
    Interfaz para el repositorio de Procesos.
    Define las operaciones que debe implementar cualquier repositorio de procesos.
    """
    
    @abstractmethod
    def save(self, process: Process) -> None:
        """Guarda un proceso en el repositorio."""
        pass
        
    @abstractmethod
    def find_by_id(self, process_id: str) -> Optional[Process]:
        """Busca un proceso por su ID."""
        pass
        
    @abstractmethod
    def find_all(self) -> List[Process]:
        """Devuelve todos los procesos almacenados."""
        pass
        
    @abstractmethod
    def delete(self, process_id: str) -> bool:
        """Elimina un proceso por su ID."""
        pass