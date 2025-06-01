import statistics
from datetime import datetime

from ...domain.entities.capacity_study import CapacityStudy, InputDataSummary,CalculatedIndices 
from ...domain.repositories.ctq_repository import ICTQRepository
from ...domain.repositories.capacity_study_repository import ICapacityStudyRepository
from ...domain.services.capability_calculator import CapabilityCalculator
from ..ports.create_capacity_study_port import ICreateCapacityStudy, CreateCapacityStudyCommand

class CreateCapacityStudyUseCase(ICreateCapacityStudy):
    def __init__(self,
                 ctq_repo: ICTQRepository,
                 study_repo: ICapacityStudyRepository):
        self.ctq_repo = ctq_repo
        self.study_repo = study_repo
        self.calculator = CapabilityCalculator()

    def execute(self, command: CreateCapacityStudyCommand) -> CapacityStudy:
        # 1. Validar entrada de datos crudos
        if not command.raw_measurements or len(command.raw_measurements) < 2:
            # Se necesitan al menos 2 puntos para calcular la desviación estándar
            raise ValueError("Se requieren al menos 2 mediciones para realizar el estudio.")

        # 2. Obtener la CTQ y sus especificaciones
        ctq = self.ctq_repo.find_by_id(command.ctq_id)
        if not ctq:
            raise ValueError(f"CTQ con id {command.ctq_id} no encontrada.")

        # 3. Calcular Media (μ) y Desviación Estándar (σ) de los datos crudos
        try:
            mean_calculated: float = statistics.mean(command.raw_measurements)
            # Usar desviación estándar muestral (n-1 en el denominador)
            std_dev_calculated: float = statistics.stdev(command.raw_measurements)
        except statistics.StatisticsError as e:
            raise statistics.StatisticsError(f"Error al calcular estadísticas básicas: {e}")
        except Exception as e:
             raise RuntimeError(f"Error inesperado calculando estadísticas: {e}")

        # Asegurar que std_dev no sea cero (aunque stdev() lo maneja, es buena práctica)
        if std_dev_calculated <= 0:
             # Esto podría pasar si todos los datos son idénticos.
             # El CapabilityCalculator ya maneja std_dev=0, pero podemos ser explícitos.
             pass # O lanzar un error específico si se desea

        # 4. Calcular índices de capacidad usando el servicio de dominio
        #    Pasamos las estadísticas recién calculadas
        calculated_indices: CalculatedIndices = self.calculator.calculate_indices(
            spec=ctq.specification,
            mean=mean_calculated,
            std_dev=std_dev_calculated,
            raw_measurements=command.raw_measurements 
        )

        # Si hubo errores graves en el cálculo de índices, podríamos lanzar una excepción
        if calculated_indices.errors and not any(v is not None for v in [calculated_indices.cp, calculated_indices.cpk]):
             raise ValueError(f"Errores en el cálculo de índices: {', '.join(calculated_indices.errors)}")

        # 5. Crear la entidad CapacityStudy
        study_input = InputDataSummary(
            mean=mean_calculated, # <- Guardar la media calculada
            std_dev=std_dev_calculated, # <- Guardar la sigma calculada
            sample_size=len(command.raw_measurements) # Guardar tamaño de muestra
        )

        # Determinar fecha del estudio
        study_time = datetime.now()
        if command.study_date_override:
            try:
                study_time = datetime.fromisoformat(command.study_date_override)
            except ValueError:
                print(f"Warning: study_date_override '{command.study_date_override}' no es un formato ISO válido, usando fecha actual.")


        new_study = CapacityStudy(
            ctq_id=command.ctq_id,
            study_date=study_time,
            input_data=study_input, # Contiene las estadísticas calculadas
            results=calculated_indices
            # El ID se genera por defecto
            # Nota: Decidimos *no* guardar la lista completa de raw_measurements
            # en la entidad/DB por defecto para mantener el modelo ligero,
            # pero se podría añadir un campo si fuera necesario para auditoría.
        )

        # 6. Persistir el estudio
        self.study_repo.save(new_study)

        # 7. Retornar el estudio creado
        return new_study
    def get_studies_by_ctq(self, ctq_id: str) -> list:
        """
        Devuelve todos los estudios de capacidad asociados a una CTQ.
        """
        return self.study_repo.find_by_ctq_id(ctq_id)