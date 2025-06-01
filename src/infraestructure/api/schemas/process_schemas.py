from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ProcessCreationRequest(BaseModel):
    """
    Esquema para la creación de un nuevo proceso.
    Define la estructura de datos esperada cuando un cliente quiere crear un proceso.
    """
    name: str = Field(
        ..., 
        title="Nombre del proceso",
        description="Nombre descriptivo del proceso",
        min_length=3, 
        max_length=100,
        example="Proceso de Torneado CNC"
    )
    
    description: Optional[str] = Field(
        None, 
        title="Descripción del proceso",
        description="Detalles adicionales sobre el proceso",
        max_length=500,
        example="Proceso de torneado de precisión para ejes de transmisión de 15mm"
    )

class ProcessUpdateRequest(BaseModel):
    """
    Esquema para la actualización de un proceso existente.
    Permite actualización parcial (solo los campos que se envían).
    """
    name: Optional[str] = Field(
        None, 
        title="Nombre del proceso",
        description="Nombre descriptivo del proceso",
        min_length=3, 
        max_length=100,
        example="Proceso de Torneado CNC Actualizado"
    )
    
    description: Optional[str] = Field(
        None, 
        title="Descripción del proceso",
        description="Detalles adicionales sobre el proceso",
        max_length=500,
        example="Proceso actualizado de torneado de precisión para ejes de transmisión"
    )

class ProcessResponse(BaseModel):
    """
    Esquema para la respuesta con información de un proceso.
    Define la estructura de datos que se devuelve al cliente.
    """
    id: str = Field(
        ..., 
        title="ID único del proceso",
        description="Identificador único del proceso en el sistema",
        example="PROC-123abc"
    )
    
    name: str = Field(
        ..., 
        title="Nombre del proceso",
        description="Nombre descriptivo del proceso",
        example="Proceso de Torneado CNC"
    )
    
    description: Optional[str] = Field(
        None, 
        title="Descripción del proceso",
        description="Detalles adicionales sobre el proceso",
        example="Proceso de torneado de precisión para ejes de transmisión de 15mm"
    )
    
    # Si tienes campos adicionales como fecha de creación, puedes incluirlos aquí
    # created_at: datetime = Field(
    #     ..., 
    #     title="Fecha de creación",
    #     description="Fecha y hora en que se creó el proceso",
    #     example="2023-04-24T10:30:00Z"
    # )
    
    class Config:
        """Configuración adicional para el modelo"""
        # Permitir la conversión de ORM (como SQLAlchemy) a Pydantic
        orm_mode = True