from ...domain.entities.ctq import CTQ
from ...domain.value_objects.specification import Specification
from ...domain.repositories.ctq_repository import ICTQRepository
from ...domain.repositories.process_repository import IProcessRepository # Necesario para validar processId
from ..ports.define_ctq_port import IDefineCTQ, DefineCTQCommand

class DefineCTQUseCase(IDefineCTQ):
    def __init__(self,
                 ctq_repo: ICTQRepository,
                 process_repo: IProcessRepository): # Inyectar repo de procesos
        self.ctq_repo = ctq_repo
        self.process_repo = process_repo

    def execute(self, command: DefineCTQCommand) -> CTQ:
        # 1. Validar existencia del Proceso
        process = self.process_repo.find_by_id(command.process_id)
        if not process:
            raise ValueError(f"Proceso con ID '{command.process_id}' no encontrado.")

        # 2. Validar y crear Value Object Specification
        try:
            spec = Specification(
                usl=command.usl,
                lsl=command.lsl,
                nominal=command.nominal
            )
        except ValueError as e:
            # Capturar errores de validación de Specification (e.g., USL <= LSL)
            raise ValueError(f"Error en especificación: {e}")

        # 3. Crear la entidad CTQ
        # El ID se genera automáticamente en la entidad
        new_ctq = CTQ(
            process_id=command.process_id,
            name=command.name,
            unit=command.unit,
            specification=spec
        )

        # 4. Persistir la nueva CTQ usando el repositorio
        self.ctq_repo.save(new_ctq)

        # 5. Retornar la CTQ creada
        return new_ctq