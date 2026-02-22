"""
Lógica de análise de segurança (versão UI)
Converte dados do core.security para modelos da UI
"""
from typing import List, Dict, Any
from core.security import SecurityAnalyzer as CoreSecurityAnalyzer
from core.scanner import WifiNetwork

from ui.security.models import (
    RiskLevel, Vulnerability, VulnerabilityType,
    NetworkSecurityAnalysis, EnvironmentSecurityReport
)


class SecurityAnalyzerUI:
    """
    Adaptador da análise de segurança para a UI
    Prepara dados para exibição na tela de segurança
    """
    
    @classmethod
    def analyze_network(cls, network: WifiNetwork) -> NetworkSecurityAnalysis:
        """Analisa uma rede e retorna modelo completo para UI"""
        core_analysis = CoreSecurityAnalyzer.analyze_network(network)
        
        # Converter flags para vulnerabilidades estruturadas
        vulnerabilities = cls._flags_to_vulnerabilities(core_analysis["flags"])
        
        # Determinar nível de risco
        risk_score = core_analysis["risk_score"]
        if risk_score >= 80:
            risk_level = RiskLevel.CRITICAL
        elif risk_score >= 60:
            risk_level = RiskLevel.HIGH
        elif risk_score >= 30:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW
        
        return NetworkSecurityAnalysis(
            ssid=network.ssid,
            auth=network.auth,
            encryption=network.encryption,
            risk_level=risk_level,
            risk_score=risk_score,
            vulnerabilities=vulnerabilities,
            flags=core_analysis["flags"],
            recommendations=core_analysis["recommendations"],
            last_connection=network.last_connection
        )
    
    @classmethod
    def analyze_environment(cls, networks: List[WifiNetwork]) -> EnvironmentSecurityReport:
        """Analisa todo o ambiente e retorna relatório completo"""
        core_env = CoreSecurityAnalyzer.analyze_environment(networks)
        
        # Analisar cada rede individualmente
        networks_analysis = [
            cls.analyze_network(net) for net in networks
        ]
        
        # Gerar recomendações globais
        global_recommendations = cls._generate_global_recommendations(core_env, networks_analysis)
        
        return EnvironmentSecurityReport(
            total_networks=core_env.get("total_networks", 0),
            critical_count=core_env.get("high_risk", 0),  # Ajustar depois
            high_count=core_env.get("medium_risk", 0),
            medium_count=core_env.get("low_risk", 0),
            low_count=0,
            open_networks=core_env.get("open_networks", 0),
            wep_networks=core_env.get("wep_networks", 0),
            wpa3_networks=core_env.get("wpa3_networks", 0),
            weak_passwords=core_env.get("weak_passwords", 0),
            health_score=core_env.get("health_score", 100),
            health_status=core_env.get("health_status", "Bom"),
            networks_analysis=networks_analysis,
            global_recommendations=global_recommendations
        )
    
    @classmethod
    def _flags_to_vulnerabilities(cls, flags: List[str]) -> List[Vulnerability]:
        """Converte flags simples em vulnerabilidades estruturadas"""
        vulnerabilities = []
        
        for flag in flags:
            if "WEP" in flag:
                vulnerabilities.append(Vulnerability(
                    type=VulnerabilityType.WEP,
                    description="Rede utiliza WEP - protocolo completamente inseguro",
                    risk_level=RiskLevel.CRITICAL,
                    recommendation="Substituir WEP por WPA2 ou WPA3 imediatamente",
                    cvss_score=9.0
                ))
            elif "aberta" in flag or "open" in flag.lower():
                vulnerabilities.append(Vulnerability(
                    type=VulnerabilityType.OPEN_NETWORK,
                    description="Rede sem autenticação - qualquer um pode conectar",
                    risk_level=RiskLevel.CRITICAL,
                    recommendation="Configurar WPA2 com senha forte",
                    cvss_score=8.5
                ))
            elif "WPA original" in flag:
                vulnerabilities.append(Vulnerability(
                    type=VulnerabilityType.WPA_LEGACY,
                    description="WPA original vulnerável a ataques",
                    risk_level=RiskLevel.HIGH,
                    recommendation="Atualizar roteador para suportar WPA2 ou WPA3",
                    cvss_score=7.5
                ))
            elif "TKIP" in flag:
                vulnerabilities.append(Vulnerability(
                    type=VulnerabilityType.TKIP,
                    description="TKIP é um protocolo de criptografia obsoleto",
                    risk_level=RiskLevel.MEDIUM,
                    recommendation="Configurar AES em vez de TKIP",
                    cvss_score=6.0
                ))
            elif "fraca" in flag:
                vulnerabilities.append(Vulnerability(
                    type=VulnerabilityType.WEAK_PASSWORD,
                    description="Senha fraca ou padrão",
                    risk_level=RiskLevel.HIGH,
                    recommendation="Usar senha com pelo menos 12 caracteres incluindo números e símbolos",
                    cvss_score=7.0
                ))
        
        return vulnerabilities
    
    @classmethod
    def _generate_global_recommendations(cls, core_env: Dict, networks_analysis: List) -> List[str]:
        """Gera recomendações globais baseadas na análise do ambiente"""
        recommendations = []
        
        if core_env.get("wep_networks", 0) > 0:
            recommendations.append("🔴 Remover todas as redes WEP - protocolo inseguro")
        
        if core_env.get("open_networks", 0) > 0:
            recommendations.append("🔴 Configurar autenticação nas redes abertas")
        
        if core_env.get("weak_passwords", 0) > 0:
            recommendations.append("🟡 Atualizar senhas fracas para senhas mais fortes")
        
        if core_env.get("health_score", 100) < 50:
            recommendations.append("⚠️ Ambiente crítico - revisar todas as redes urgentemente")
        elif core_env.get("health_score", 100) < 80:
            recommendations.append("📋 Revisar redes com segurança abaixo do ideal")
        
        if not recommendations:
            recommendations.append("✅ Ambiente com boa segurança - mantenha as práticas")
        
        return recommendations