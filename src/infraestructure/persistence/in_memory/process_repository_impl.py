from typing import Optional, List, Dict
from src.domain.entities.process import Process
from src.domain.repositories.ctq_repository import ICTQRepository
from src.domain.repositories.process_repository import IProcessRepository



class InMemoryProcessRepository(IProcessRepository):
    def __init__(self):
        self._processes: Dict[str, Process] = {}  # Inicializa el diccionario de procesos

    def add_sample_process(self):
        sample = Process(name="Proceso de Ejemplo", description="Proceso inicial para pruebas")
        self.save(sample)

    def save(self, process: Process) -> None:
        self._processes[process.id] = process
        print(f"DEBUG: Guardado Proceso {process.id} en memoria.")

    def find_by_id(self, process_id: str) -> Optional[Process]:
        return self._processes.get(process_id)

    def find_all(self) -> List[Process]:
        return list(self._processes.values())