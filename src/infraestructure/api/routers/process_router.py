from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from src.domain.entities.process import Process
from src.domain.repositories.process_repository import IProcessRepository

from ..schemas.process_schemas import ProcessResponse, ProcessCreationRequest
from ...config.dependency_injection import get_process_repository

router = APIRouter(
    prefix="/processes",
    tags=["Procesos"]
)

# Endpoint GET para listar todos los procesos
@router.get("/", response_model=List[ProcessResponse])
async def get_all_processes(
    process_repo: IProcessRepository = Depends(get_process_repository)
):
    """
    Obtiene todos los procesos registrados en el sistema.
    
    Returns:
        List[ProcessResponse]: Lista de todos los procesos.
    """
    processes = process_repo.find_all()
    
    # Convertir entidades de dominio a schemas de respuesta
    return [
        ProcessResponse(
            id=process.id,
            name=process.name,
            description=process.description
        ) for process in processes
    ]

# Endpoint GET para obtener un proceso por ID
@router.get("/{process_id}", response_model=ProcessResponse)
async def get_process_by_id(
    process_id: str,
    process_repo: IProcessRepository = Depends(get_process_repository)
):
    """
    Obtiene un proceso específico por su ID.
    
    Args:
        process_id (str): ID único del proceso a buscar.
        
    Returns:
        ProcessResponse: Datos del proceso encontrado.
        
    Raises:
        HTTPException: Si no se encuentra el proceso con el ID especificado.
    """
    process = process_repo.find_by_id(process_id)
    
    if not process:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proceso con ID '{process_id}' no encontrado."
        )
    
    return ProcessResponse(
        id=process.id,
        name=process.name,
        description=process.description
    )

# Endpoint POST para crear un nuevo proceso
@router.post("/", response_model=ProcessResponse, status_code=status.HTTP_201_CREATED)
async def create_process(
    request: ProcessCreationRequest,
    process_repo: IProcessRepository = Depends(get_process_repository)
):
    """
    Crea un nuevo proceso en el sistema.
    
    Args:
        request (ProcessCreationRequest): Datos del proceso a crear.
        
    Returns:
        ProcessResponse: Datos del proceso creado.
    """
    # Crear entidad desde los datos de la petición
    new_process = Process(
        name=request.name,
        description=request.description
        # El ID se generará automáticamente
    )
    
    # Guardar en el repositorio
    process_repo.save(new_process)
    
    # Devolver respuesta
    return ProcessResponse(
        id=new_process.id,
        name=new_process.name,
        description=new_process.description
    )

# Endpoint para crear datos de prueba rápidamente
@router.post("/setup-test-data", tags=["Testing"])
async def create_test_process(
    process_repo: IProcessRepository = Depends(get_process_repository)
):
    """
    Crea un proceso de prueba con ID fijo para facilitar el testing.
    """
    test_process = Process(
        id="PROC-123", 
        name="Proceso de Manufactura de Prueba", 
        description="Proceso creado para pruebas de la API"
    )
    
    try:
        process_repo.save(test_process)
        return {"message": "Datos de prueba creados correctamente", "process_id": test_process.id}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear datos de prueba: {str(e)}"
        )