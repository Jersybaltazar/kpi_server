from dataclasses import dataclass, field
import uuid
from typing import Optional

@dataclass
class Process:
    name: str
    id: str = field(default_factory=lambda: f"PROC-{uuid.uuid4()}")

    description: Optional[str] = None
    # created_at: datetime = field(default_factory=datetime.now) # Opcional