"""
Módulo de segurança - Interface de análise de vulnerabilidades
"""

# Não exportar SecurityWindow daqui para evitar circular import
from ui.security.models import (
    RiskLevel, 
    VulnerabilityType, 
    Vulnerability, 
    NetworkSecurityAnalysis, 
    EnvironmentSecurityReport
)
from ui.security.widgets import SecurityCard, SecuritySummaryWidget, VulnerabilityBadge
from ui.security.security_analyzer import SecurityAnalyzerUI

__all__ = [
    'RiskLevel',
    'VulnerabilityType',
    'Vulnerability',
    'NetworkSecurityAnalysis',
    'EnvironmentSecurityReport',
    'SecurityCard',
    'SecuritySummaryWidget',
    'VulnerabilityBadge',
    'SecurityAnalyzerUI'
]