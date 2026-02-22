"""
Modelos de dados para o sistema de auditoria
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Any, Dict


@dataclass
class AuditEvent:
    """Modelo para eventos de auditoria"""
    event_type: str
    user: str
    hostname: str
    timestamp: datetime
    details: Dict[str, Any]
    sha256: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte evento para dicionário"""
        return {
            "event_type": self.event_type,
            "user": self.user,
            "hostname": self.hostname,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details,
            "sha256": self.sha256
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AuditEvent':
        """Cria evento a partir de dicionário"""
        return cls(
            event_type=data["event_type"],
            user=data["user"],
            hostname=data["hostname"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            details=data["details"],
            sha256=data.get("sha256")
        )