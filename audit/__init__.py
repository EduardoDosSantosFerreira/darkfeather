"""
Módulo de auditoria para DarkFeather WiFi Analysis
Registro de ações, hashes e logs de segurança
"""

from audit.logger import AuditLogger
from audit.models import AuditEvent

__all__ = ['AuditLogger', 'AuditEvent']