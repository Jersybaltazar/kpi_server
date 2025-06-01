from dataclasses import dataclass, field
import uuid
from typing import Optional
from ..value_objects.specification import Specification

@dataclass
class CTQ:
    # Non-default arguments first
    process_id: str
    name: str
    unit: str
    specification: Specification
    # Default arguments last
    id: str = field(default_factory=lambda: f"CTQ-{uuid.uuid4()}")
    process_name: Optional[str] = None
    # Añadir más campos si es necesario (dataType, description, etc.)