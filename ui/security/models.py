"""
Modelos de dados para análise de segurança
"""
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum


class RiskLevel(Enum):
    LOW = "Baixo"
    MEDIUM = "Médio"
    HIGH = "Alto"
    CRITICAL = "Crítico"


class VulnerabilityType(Enum):
    WEP = "WEP"
    WPA_LEGACY = "WPA Legado"
    OPEN_NETWORK = "Rede Aberta"
    NO_ENCRYPTION = "Sem Criptografia"
    TKIP = "TKIP (Obsoleto)"
    WEAK_PASSWORD = "Senha Fraca"
    DEFAULT_CREDENTIALS = "Credenciais Padrão"
    OLD_FIRMWARE = "Firmware Desatualizado"
    OPEN_PORT = "Porta Aberta"
    WPS_ENABLED = "WPS Ativado"


@dataclass
class Vulnerability:
    """Modelo de vulnerabilidade"""
    type: VulnerabilityType
    description: str
    risk_level: RiskLevel
    recommendation: str
    cvss_score: Optional[float] = None
    
    def to_dict(self):
        return {
            "type": self.type.value,
            "description": self.description,
            "risk_level": self.risk_level.value,
            "recommendation": self.recommendation,
            "cvss_score": self.cvss_score
        }


@dataclass
class NetworkSecurityAnalysis:
    """Análise completa de uma rede"""
    ssid: str
    auth: str
    encryption: str
    risk_level: RiskLevel
    risk_score: int
    vulnerabilities: List[Vulnerability]
    flags: List[str]
    recommendations: List[str]
    last_connection: Optional[str] = None
    
    @property
    def has_vulnerabilities(self) -> bool:
        return len(self.vulnerabilities) > 0
    
    @property
    def critical_count(self) -> int:
        return sum(1 for v in self.vulnerabilities if v.risk_level == RiskLevel.CRITICAL)
    
    @property
    def high_count(self) -> int:
        return sum(1 for v in self.vulnerabilities if v.risk_level == RiskLevel.HIGH)
    
    def to_dict(self):
        return {
            "ssid": self.ssid,
            "auth": self.auth,
            "encryption": self.encryption,
            "risk_level": self.risk_level.value,
            "risk_score": self.risk_score,
            "vulnerabilities": [v.to_dict() for v in self.vulnerabilities],
            "flags": self.flags,
            "recommendations": self.recommendations,
            "last_connection": self.last_connection
        }


@dataclass
class EnvironmentSecurityReport:
    """Relatório completo do ambiente"""
    total_networks: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    open_networks: int
    wep_networks: int
    wpa3_networks: int
    weak_passwords: int
    health_score: int
    health_status: str
    networks_analysis: List[NetworkSecurityAnalysis]
    global_recommendations: List[str]
    
    @property
    def has_critical_issues(self) -> bool:
        return self.critical_count > 0
    
    @property
    def summary_text(self) -> str:
        return (f"Total: {self.total_networks} | "
                f"Crítico: {self.critical_count} | "
                f"Alto: {self.high_count} | "
                f"Saúde: {self.health_score}%")