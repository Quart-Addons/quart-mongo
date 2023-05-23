from pathlib import Path
from uuid import UUID
from odmantic import Model

class OdmanticEncoded(Model):
    a: UUID
    b: Path

odm = OdmanticEncoded(a=UUID("23ef2e02-1c20-49de-b05e-e9fe2431c474"), b=Path("/"))

print(odm.id)