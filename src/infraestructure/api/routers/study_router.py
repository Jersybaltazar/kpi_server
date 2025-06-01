import statistics
from src.application.ports.create_capacity_study_port import CreateCapacityStudyCommand, ICreateCapacityStudy
from src.domain.entities.capacity_study import CapacityStudy
from src.domain.services.capability_calculator import CapabilityCalculator

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from ..schemas.study_schemas import StudyCreationRequest, StudyResponse
from ...config.dependency_injection import get_create_study_use_case

router = APIRouter(
    prefix="/ctqs/{ctq_id}/studies",
    tags=["Capacity Studies"]
)
@router.get(
    "/",
    response_model=List[StudyResponse],
    summary="Obtener todos los estudios de capacidad de una CTQ"
)
async def get_studies_by_ctq(
    ctq_id: str,
    create_study_uc: ICreateCapacityStudy = Depends(get_create_study_use_case)
):
    """
    Devuelve la lista de estudios de capacidad realizados para la CTQ especificada.
    """
    try:
        studies = create_study_uc.get_studies_by_ctq(ctq_id)
        return studies
    except Exception as e:
        print(f"ERROR Interno: {e}")
        raise HTTPException(status_code=500, detail="Error interno al obtener los estudios.")

@router.post(
    "/",
    response_model=StudyResponse, # <- Usa el schema de respuesta actualizado
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo estudio de capacidad para una CTQ a partir de datos crudos"
)
async def create_study_endpoint(
    ctq_id: str,
    request: StudyCreationRequest, # <- Usa el schema de request actualizado
    create_study_uc: ICreateCapacityStudy = Depends(get_create_study_use_case)
):
    """
    Realiza un nuevo análisis de capacidad para la CTQ especificada,
    calculando la media (μ) y desviación estándar (σ) a partir de la
    lista de **mediciones crudas** proporcionada.
    """
    command = CreateCapacityStudyCommand(
        ctq_id=ctq_id,
        raw_measurements=request.raw_measurements, # <- Pasa la lista de datos
        study_date_override=request.study_date_override,
        opportunities_per_unit=request.opportunities_per_unit
    )
    try:
        new_study: CapacityStudy = create_study_uc.execute(command)
        # Pydantic con orm_mode=True debería mapear la entidad al response schema
        return StudyResponse.from_entity(new_study)
    except ValueError as ve:
        # Errores de validación (pocos datos, CTQ no existe, error en especificación)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except statistics.StatisticsError as se:
        # Error específico al calcular media/sigma
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error estadístico: {se}")
    except Exception as e:
        # Loggear el error 'e' para depuración
        print(f"ERROR Interno: {e}") # Log simple
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno al procesar el estudio.")


