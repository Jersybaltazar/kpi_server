from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from ...domain.entities.ctq import CTQ  # Ajustar si la ruta relativa cambia

@dataclass
class DefineCTQCommand:
    """Comando para definir una nueva Característica de Calidad Crítica."""
    process_id: str
    name: str
    unit: str
    usl: float
    lsl: float
    nominal: Optional[float] = None
    # Podríamos añadir description, dataType, etc. aquí si fueran necesarios

class IDefineCTQ(ABC):
    """Interfaz para el caso de uso de definición de CTQ."""
    @abstractmethod
    def execute(self, command: DefineCTQCommand) -> CTQ:
        """
        Ejecuta el comando para definir y guardar una nueva CTQ.

        Args:
            command: El comando con los datos de la CTQ a definir.

        Returns:
            La entidad CTQ creada.

        Raises:
            ValueError: Si los datos de entrada son inválidos o el proceso no existe.
        """
        pass