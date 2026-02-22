"""
Logger de auditoria - Registra ações do usuário
"""
import json
import hashlib
from datetime import datetime
from pathlib import Path
import getpass
import socket
from typing import Optional, List, Dict, Any

from audit.models import AuditEvent


class AuditLogger:
    """
    Sistema de registro de auditoria
    Localização: ~/DarkFeather/audit/audit_log.json
    """
    
    def __init__(self):
        self.audit_dir = Path.home() / "DarkFeather" / "audit"
        self.audit_file = self.audit_dir / "audit_log.json"
        self.ensure_audit_file()
    
    def ensure_audit_file(self):
        """Garante que o arquivo de auditoria existe"""
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        
        if not self.audit_file.exists():
            with open(self.audit_file, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2, ensure_ascii=False)
    
    def _get_system_info(self) -> Dict[str, str]:
        """Obtém informações do sistema"""
        return {
            "user": getpass.getuser(),
            "hostname": socket.gethostname(),
            "timestamp": datetime.now()
        }
    
    def _load_logs(self) -> List[Dict]:
        """Carrega logs existentes"""
        try:
            with open(self.audit_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _save_logs(self, logs: List[Dict]):
        """Salva logs no arquivo"""
        with open(self.audit_file, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=2, ensure_ascii=False, default=str)
    
    def log_event(self, event_type: str, details: Dict[str, Any], sha256: Optional[str] = None):
        """
        Registra um evento no log de auditoria
        
        Args:
            event_type: Tipo do evento (APP_STARTED, SCAN_FINISHED, etc)
            details: Detalhes específicos do evento
            sha256: Hash SHA256 opcional (para relatórios)
        """
        system_info = self._get_system_info()
        
        event = AuditEvent(
            event_type=event_type,
            user=system_info["user"],
            hostname=system_info["hostname"],
            timestamp=system_info["timestamp"],
            details=details,
            sha256=sha256
        )
        
        # Carregar logs existentes
        logs = self._load_logs()
        
        # Adicionar novo evento
        logs.append(event.to_dict())
        
        # Salvar
        self._save_logs(logs)
    
    def log_app_started(self):
        """Registra inicialização da aplicação"""
        self.log_event("APP_STARTED", {})
    
    def log_scan_finished(self, networks_count: int):
        """Registra conclusão de scan"""
        self.log_event("SCAN_FINISHED", {"networks_found": networks_count})
    
    def log_password_copied(self, ssid: str):
        """Registra cópia de senha"""
        self.log_event("PASSWORD_COPIED", {"ssid": ssid})
    
    def log_report_generated(self, report_path: Path, content: str):
        """Registra geração de relatório com hash"""
        sha256 = hashlib.sha256(content.encode()).hexdigest()
        self.log_event(
            "REPORT_GENERATED",
            {
                "report_path": str(report_path),
                "sha256": sha256,
                "file_size": len(content)
            },
            sha256=sha256
        )
    
    def log_export_performed(self, export_type: str, networks_count: int):
        """Registra exportação de dados"""
        self.log_event("EXPORT_PERFORMED", {
            "export_type": export_type,
            "networks_exported": networks_count
        })
    
    def get_audit_summary(self) -> Dict[str, Any]:
        """Retorna resumo dos eventos de auditoria"""
        logs = self._load_logs()
        
        if not logs:
            return {
                "total_events": 0,
                "first_event": None,
                "last_event": None,
                "events_by_type": {}
            }
        
        return {
            "total_events": len(logs),
            "first_event": logs[0]["timestamp"],
            "last_event": logs[-1]["timestamp"],
            "events_by_type": self._count_by_type(logs)
        }
    
    def _count_by_type(self, logs: List[Dict]) -> Dict[str, int]:
        """Conta eventos por tipo"""
        counts = {}
        for log in logs:
            event_type = log["event_type"]
            counts[event_type] = counts.get(event_type, 0) + 1
        return counts
    
    def get_events_by_type(self, event_type: str) -> List[Dict]:
        """Retorna todos os eventos de um determinado tipo"""
        logs = self._load_logs()
        return [log for log in logs if log["event_type"] == event_type]