from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from src.application.ports.define_ctq_port import DefineCTQCommand, IDefineCTQ
from src.domain.entities.ctq import CTQ
from src.domain.repositories.ctq_repository import ICTQRepository
from ..schemas.ctq_schemas import CTQCreationRequest, CTQResponse
# Importar funciones de DI
from ...config.dependency_injection import get_define_ctq_use_case, get_ctq_repository

router = APIRouter(
    prefix="/ctqs",
    tags=["Critical to Quality (CTQ)"]
)

# --- Endpoint para Crear CTQ ---
@router.post(
    "/",
    response_model=CTQResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Definir una nueva Característica de Calidad Crítica (CTQ)"
)
async def define_ctq_endpoint(
    request: CTQCreationRequest,
    define_ctq_uc: IDefineCTQ = Depends(get_define_ctq_use_case) # Inyectar caso de uso
):
    """
    Crea una nueva CTQ asociada a un proceso existente, con sus especificaciones.
    """
    command = DefineCTQCommand(
        process_id=request.process_id,
        name=request.name,
        unit=request.unit,
        usl=request.usl,
        lsl=request.lsl,
        nominal=request.nominal
    )
    try:
        new_ctq: CTQ = define_ctq_uc.execute(command)
        # Mapear entidad a respuesta (Pydantic con orm_mode=True ayuda)
        # Necesitamos mapear la especificación anidada explícitamente o asegurar compatibilidad
        spec_resp = {
            "usl": new_ctq.specification.usl,
            "lsl": new_ctq.specification.lsl,
            "nominal": new_ctq.specification.nominal,
            "tolerance": new_ctq.specification.tolerance, # Añadir propiedades útiles
            "midpoint": new_ctq.specification.midpoint,
        }
        response_data = new_ctq.__dict__ # Obtener datos de la entidad
        response_data["specification"] = spec_resp # Reemplazar con el dict formateado

        return CTQResponse(**response_data)
    except ValueError as ve:
        # Errores de validación (proceso no existe, USL<=LSL, etc.)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        # Loggear el error 'e' para depuración
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno al definir la CTQ.")

# --- Endpoint para Obtener CTQ por ID ---
@router.get(
    "/{ctq_id}",
    response_model=CTQResponse,
    summary="Obtener detalles de una CTQ específica por su ID"
)
async def get_ctq_by_id_endpoint(
    ctq_id: str,
    ctq_repo: ICTQRepository = Depends(get_ctq_repository) # Inyectar repositorio
):
    """
    Recupera la información detallada de una CTQ, incluyendo sus especificaciones.
    """
    ctq = ctq_repo.find_by_id(ctq_id)
    if not ctq:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"CTQ con ID '{ctq_id}' no encontrada.")

    # Mapear entidad a respuesta (igual que en POST)
    spec_resp = {
        "usl": ctq.specification.usl,
        "lsl": ctq.specification.lsl,
        "nominal": ctq.specification.nominal,
        "tolerance": ctq.specification.tolerance,
        "midpoint": ctq.specification.midpoint,
    }
    response_data = ctq.__dict__
    response_data["specification"] = spec_resp
    response_data["process_name"] = ctq.process_name 
    return CTQResponse(**response_data)

# --- Endpoint para Listar todas las CTQs (Opcional) ---
@router.get(
    "/",
    response_model=List[CTQResponse],
    summary="Listar todas las CTQs definidas"
)
async def list_all_ctqs_endpoint(
    ctq_repo: ICTQRepository = Depends(get_ctq_repository)
):
    """
    Devuelve una lista de todas las Características de Calidad Críticas registradas.
    """
    # Nota: Para un sistema real, este endpoint debería tener paginación
    all_ctqs = ctq_repo.find_all() # Necesitaríamos añadir `find_all` al repo
    response_list = []
    for ctq in all_ctqs:
         spec_resp = {
            "usl": ctq.specification.usl, "lsl": ctq.specification.lsl,
            "nominal": ctq.specification.nominal, "tolerance": ctq.specification.tolerance,
            "midpoint": ctq.specification.midpoint,
         }
         response_data = ctq.__dict__
         response_data["specification"] = spec_resp
         response_list.append(CTQResponse(**response_data))
    return response_list

# Añadir método find_all a ICTQRepository y InMemoryCTQRepository si se usa este endpoint
# src/core/domain/repositories/ctq_repository.py
# ...
#    @abstractmethod
#    def find_all(self) -> List[CTQ]:
#        pass

# src/infrastructure/persistence/in_memory/ctq_repository_impl.py
# ...
#    def find_all(self) -> List[CTQ]:
#        return list(self._ctqs.values())