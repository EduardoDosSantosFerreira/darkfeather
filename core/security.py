"""
Módulo de análise de segurança para redes WiFi
Detecta vulnerabilidades e calcula scores de risco
"""
from datetime import datetime
from typing import List, Dict, Any, Tuple

from core.scanner import WifiNetwork


class SecurityAnalyzer:
    """
    Analisa redes WiFi e identifica riscos de segurança
    Baseado APENAS em dados locais (análise passiva)
    """
    
    # Pesos para diferentes vulnerabilidades
    WEIGHTS = {
        "OPEN_NETWORK": 40,
        "WEP": 35,
        "WPA_LEGACY": 20,
        "NO_ENCRYPTION": 30,
        "TKIP": 15,
        "OLD_CONNECTION": 5,
        "WPS_ENABLED": 10,
        "PMF_DISABLED": 8,
        "WEAK_PASSWORD": 25,
        "DEFAULT_CREDENTIALS": 30
    }
    
    @classmethod
    def analyze_network(cls, network: WifiNetwork) -> Dict[str, Any]:
        """
        Analisa uma rede específica
        
        Retorna:
            - risk_score: 0-100
            - risk_level: Baixo, Médio, Alto
            - flags: Lista de vulnerabilidades
            - recommendations: Sugestões de melhoria
        """
        risk_score = 0
        flags = []
        recommendations = []
        
        auth = network.auth.lower() if network.auth else ""
        encryption = network.encryption.lower() if network.encryption else ""
        
        # 1. Análise de autenticação
        if "open" in auth or "aberto" in auth:
            risk_score += cls.WEIGHTS["OPEN_NETWORK"]
            flags.append("🔓 Rede aberta (sem senha)")
            recommendations.append("Configure WPA2/WPA3 com senha forte")
        elif "wep" in auth:
            risk_score += cls.WEIGHTS["WEP"]
            flags.append("⚠️ WEP - Extremamente vulnerável")
            recommendations.append("Substitua WEP por WPA2 ou WPA3 imediatamente")
        elif "wpa" in auth:
            if "wpa2" not in auth and "wpa3" not in auth:
                risk_score += cls.WEIGHTS["WPA_LEGACY"]
                flags.append("⚠️ WPA original - Vulnerável a ataques")
                recommendations.append("Atualize para WPA2 ou WPA3")
            elif "wpa2" in auth:
                if "enterprise" in auth:
                    flags.append("🏢 WPA2-Enterprise - Requer 802.1X")
                else:
                    flags.append("✅ WPA2-Personal - Seguro (padrão atual)")
            elif "wpa3" in auth:
                flags.append("🛡️ WPA3 - Mais seguro disponível")
        
        # 2. Análise de criptografia
        if "none" in encryption or "nenhuma" in encryption:
            risk_score += cls.WEIGHTS["NO_ENCRYPTION"]
            flags.append("🔓 Sem criptografia")
        elif "tkip" in encryption:
            risk_score += cls.WEIGHTS["TKIP"]
            flags.append("⚠️ TKIP - Criptografia obsoleta")
            recommendations.append("Configure AES em vez de TKIP")
        elif "aes" in encryption:
            if "gcmp" in encryption:
                flags.append("✅ AES-GCMP - Criptografia forte (WPA3)")
            else:
                flags.append("✅ AES - Criptografia segura")
        
        # 3. Análise de WPS
        if network.wps and "configurado" in network.wps.lower():
            risk_score += cls.WEIGHTS["WPS_ENABLED"]
            flags.append("⚠️ WPS ativado - vulnerável a ataques de PIN")
            recommendations.append("Desative WPS no roteador")
        
        # 4. Análise de PMF
        if network.pmf and ("não" in network.pmf.lower() or "disabled" in network.pmf.lower()):
            risk_score += cls.WEIGHTS["PMF_DISABLED"]
            flags.append("ℹ️ PMF desativado - menos proteção contra ataques")
            recommendations.append("Ative PMF (Protected Management Frames) se disponível")
        
        # 5. Análise de última conexão
        if network.last_connection and network.last_connection != "N/A":
            try:
                for fmt in ["%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"]:
                    try:
                        last = datetime.strptime(network.last_connection, fmt)
                        days_ago = (datetime.now() - last).days
                        
                        if days_ago > 180:
                            risk_score += cls.WEIGHTS["OLD_CONNECTION"]
                            flags.append(f"📅 Não usada há {days_ago} dias")
                            recommendations.append("Revise se esta rede ainda é necessária")
                        elif days_ago > 90:
                            flags.append(f"📅 Último uso: {days_ago} dias atrás")
                        break
                    except ValueError:
                        continue
            except Exception:
                pass
        
        # 6. Análise de senha padrão (básica)
        if network.password:
            password_lower = network.password.lower()
            if password_lower in ["12345678", "password", "senha", "admin", "1234567890"]:
                risk_score += cls.WEIGHTS["WEAK_PASSWORD"]
                flags.append("⚠️ Senha muito fraca ou padrão")
                recommendations.append("Use uma senha forte com pelo menos 12 caracteres")
            elif len(network.password) < 8:
                risk_score += 15
                flags.append("⚠️ Senha muito curta (< 8 caracteres)")
                recommendations.append("Aumente o comprimento da senha para pelo menos 8 caracteres")
        
        # Calcular nível de risco
        risk_score = min(risk_score, 100)
        
        if risk_score >= 60:
            risk_level = "Alto"
        elif risk_score >= 30:
            risk_level = "Médio"
        else:
            risk_level = "Baixo"
        
        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "flags": flags,
            "recommendations": recommendations
        }
    
    @classmethod
    def analyze_environment(cls, networks: List[WifiNetwork]) -> Dict[str, Any]:
        """
        Analisa todo o ambiente de redes
        """
        if not networks:
            return {
                "total_networks": 0,
                "high_risk": 0,
                "medium_risk": 0,
                "low_risk": 0,
                "open_networks": 0,
                "wep_networks": 0,
                "wpa3_networks": 0,
                "wps_enabled": 0,
                "pmf_disabled": 0,
                "weak_passwords": 0,
                "health_score": 100,
                "health_status": "Sem redes"
            }
        
        total = len(networks)
        high_risk = 0
        medium_risk = 0
        low_risk = 0
        open_networks = 0
        wep_networks = 0
        wpa3_networks = 0
        wps_enabled = 0
        pmf_disabled = 0
        weak_passwords = 0
        
        for net in networks:
            analysis = cls.analyze_network(net)
            
            if analysis["risk_level"] == "Alto":
                high_risk += 1
            elif analysis["risk_level"] == "Médio":
                medium_risk += 1
            else:
                low_risk += 1
            
            flags_str = " ".join(analysis["flags"])
            if "aberta" in flags_str or "open" in flags_str:
                open_networks += 1
            if "WEP" in flags_str:
                wep_networks += 1
            if "WPA3" in flags_str:
                wpa3_networks += 1
            if "WPS" in flags_str:
                wps_enabled += 1
            if "PMF" in flags_str and "desativado" in flags_str:
                pmf_disabled += 1
            if "fraca" in flags_str or "curta" in flags_str:
                weak_passwords += 1
        
        penalties = (
            high_risk * 25 +
            medium_risk * 10 +
            open_networks * 15 +
            wep_networks * 20 +
            wps_enabled * 8 +
            pmf_disabled * 5 +
            weak_passwords * 10
        )
        health_score = max(0, 100 - (penalties / max(total, 1)))
        health_score = int(health_score)
        
        if health_score >= 80:
            health_status = "Bom"
        elif health_score >= 50:
            health_status = "Atenção"
        else:
            health_status = "Crítico"
        
        return {
            "total_networks": total,
            "high_risk": high_risk,
            "medium_risk": medium_risk,
            "low_risk": low_risk,
            "open_networks": open_networks,
            "wep_networks": wep_networks,
            "wpa3_networks": wpa3_networks,
            "wps_enabled": wps_enabled,
            "pmf_disabled": pmf_disabled,
            "weak_passwords": weak_passwords,
            "health_score": health_score,
            "health_status": health_status
        }
    
    @classmethod
    def get_risk_color(cls, risk_level: str) -> str:
        colors = {
            "Baixo": "#10b981",
            "Médio": "#f59e0b",
            "Alto": "#ef4444"
        }
        return colors.get(risk_level, "#94a3b8")
    
    @classmethod
    def get_risk_icon(cls, risk_level: str) -> str:
        icons = {
            "Baixo": "🟢",
            "Médio": "🟡",
            "Alto": "🔴"
        }
        return icons.get(risk_level, "⚪")