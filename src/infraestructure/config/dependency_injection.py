from src.application.ports.define_ctq_port import IDefineCTQ
from src.domain.repositories.process_repository import IProcessRepository
from src.application.use_cases.create_capacity_study import CreateCapacityStudyUseCase
from src.application.use_cases.define_ctq import DefineCTQUseCase
from src.domain.repositories.capacity_study_repository import ICapacityStudyRepository
from src.domain.repositories.ctq_repository import ICTQRepository
from ..persistence.in_memory.process_repository_impl import InMemoryProcessRepository

from ..persistence.in_memory.ctq_repository_impl import InMemoryCTQRepository
from ..persistence.in_memory.capacity_study_repository_impl import InMemoryCapacityStudyRepository
from ..persistence.mysql.process_repository_impl import MySQLProcessRepository
from ..persistence.mysql.capacity_study_repository_impl import MySQLCapacityStudyRepository
# Instancias Singleton (o podrían ser creadas por request)
def get_process_repository() -> IProcessRepository:
    """Devuelve el repositorio de procesos."""
    if hasattr(get_process_repository, "instance"):
        return get_process_repository.instance
    
    get_process_repository.instance = MySQLProcessRepository()
    return get_process_repository.instance

def get_ctq_repository() -> ICTQRepository:
    """Devuelve el repositorio de CTQs."""
    if hasattr(get_ctq_repository, "instance"):
        return get_ctq_repository.instance
    
    # Usa el repositorio MySQL si está implementado, o en memoria si no
    from ..persistence.mysql.ctq_repository_impl import MySQLCTQRepository
    get_ctq_repository.instance = MySQLCTQRepository()
    return get_ctq_repository.instance

def get_capacity_study_repository() -> ICapacityStudyRepository:
    """Devuelve el repositorio de estudios de capacidad."""
    if hasattr(get_capacity_study_repository, "instance"):
        return get_capacity_study_repository.instance
    
    get_capacity_study_repository.instance = MySQLCapacityStudyRepository()
    return get_capacity_study_repository.instance

# Casos de uso
def get_define_ctq_use_case() -> IDefineCTQ:
    """Devuelve una instancia del caso de uso para definir CTQs."""
    return DefineCTQUseCase(
        ctq_repo=get_ctq_repository(),
        process_repo=get_process_repository()
    )

def get_create_study_use_case():
    """Devuelve una instancia del caso de uso para crear estudios de capacidad."""
    return CreateCapacityStudyUseCase(
        study_repo=get_capacity_study_repository(),
        ctq_repo=get_ctq_repository()
    )