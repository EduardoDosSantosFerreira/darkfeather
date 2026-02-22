"""
Gerador de relatórios de auditoria
"""
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
import json

from core.scanner import WifiNetwork
from core.security import SecurityAnalyzer
from audit.logger import AuditLogger


class ReportGenerator:
    """
    Gera relatórios em diferentes formatos (TXT, JSON, HTML)
    """
    
    def __init__(self, networks: List[WifiNetwork], audit: AuditLogger):
        self.networks = networks
        self.audit = audit
        self.environment = SecurityAnalyzer.analyze_environment(networks)
        self.generated_at = datetime.now()
        
        # Diretório de relatórios
        self.reports_dir = Path.home() / "DarkFeather" / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_filename(self, extension: str = "txt") -> Path:
        """Gera nome de arquivo único para o relatório"""
        timestamp = self.generated_at.strftime("%Y%m%d_%H%M%S")
        return self.reports_dir / f"darkfeather_report_{timestamp}.{extension}"
    
    def generate_text_report(self) -> str:
        """Gera relatório em formato texto"""
        lines = []
        lines.append("=" * 80)
        lines.append(" 🦅 DARKFEATHER - RELATÓRIO DE AUDITORIA WiFi")
        lines.append("=" * 80)
        lines.append(f" Gerado em: {self.generated_at.strftime('%d/%m/%Y %H:%M:%S')}")
        lines.append(f" Usuário: {self.audit._get_system_info()['user']}")
        lines.append(f" Hostname: {self.audit._get_system_info()['hostname']}")
        lines.append("=" * 80)
        lines.append("")
        
        # RESUMO EXECUTIVO
        lines.append("📊 RESUMO EXECUTIVO")
        lines.append("-" * 40)
        lines.append(f" Total de redes analisadas: {self.environment.get('total_networks', 0)}")
        lines.append(f" Redes de Alto Risco: {self.environment.get('high_risk', 0)}")
        lines.append(f" Redes de Médio Risco: {self.environment.get('medium_risk', 0)}")
        lines.append(f" Redes de Baixo Risco: {self.environment.get('low_risk', 0)}")
        lines.append(f" Redes Abertas: {self.environment.get('open_networks', 0)}")
        lines.append(f" Redes WEP: {self.environment.get('wep_networks', 0)}")
        lines.append(f" Redes WPA3: {self.environment.get('wpa3_networks', 0)}")
        lines.append(f" Senhas Fracas: {self.environment.get('weak_passwords', 0)}")
        lines.append("")
        lines.append(f" ▶ SAÚDE DO AMBIENTE: {self.environment.get('health_score', 0)}/100 - {self.environment.get('health_status', 'N/A')}")
        lines.append("")
        
        # DETALHAMENTO POR REDE
        lines.append("🔍 DETALHAMENTO POR REDE")
        lines.append("-" * 80)
        
        if not self.networks:
            lines.append("\nNenhuma rede encontrada no sistema.")
        else:
            for i, net in enumerate(self.networks, 1):
                analysis = SecurityAnalyzer.analyze_network(net)
                
                # Cabeçalho da rede
                risk_icon = SecurityAnalyzer.get_risk_icon(analysis["risk_level"])
                lines.append(f"\n{i:2d}. {risk_icon} {net.ssid}")
                lines.append(f"     Autenticação: {net.auth}")
                lines.append(f"     Criptografia: {net.encryption}")
                lines.append(f"     Risco: {analysis['risk_level']} ({analysis['risk_score']}/100)")
                
                # Bandeiras de vulnerabilidade
                if analysis["flags"]:
                    lines.append("     Observações:")
                    for flag in analysis["flags"]:
                        lines.append(f"       • {flag}")
                
                # Recomendações
                if analysis["recommendations"]:
                    lines.append("     Recomendações:")
                    for rec in analysis["recommendations"]:
                        lines.append(f"       → {rec}")
        
        lines.append("")
        lines.append("=" * 80)
        lines.append(" 📋 LOG DE AUDITORIA (últimos 5 eventos)")
        lines.append("-" * 80)
        
        # Adicionar últimos eventos do log
        events = self.audit.get_events_by_type("REPORT_GENERATED")[-5:]
        for event in events:
            timestamp = event["timestamp"][:19].replace("T", " ")
            lines.append(f" • {timestamp} - {event['event_type']}")
            if event.get("sha256"):
                lines.append(f"   Hash: {event['sha256'][:16]}...")
        
        lines.append("")
        lines.append("=" * 80)
        lines.append(" FIM DO RELATÓRIO")
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def generate_json_report(self) -> Dict[str, Any]:
        """Gera relatório em formato JSON (estruturado)"""
        return {
            "metadata": {
                "generated_at": self.generated_at.isoformat(),
                "user": self.audit._get_system_info()["user"],
                "hostname": self.audit._get_system_info()["hostname"],
                "tool": "DarkFeather WiFi Analysis",
                "version": "2.0.0"
            },
            "environment_summary": self.environment,
            "networks": [
                {
                    "ssid": net.ssid,
                    "auth": net.auth,
                    "encryption": net.encryption,
                    "last_connection": net.last_connection,
                    "has_password": bool(net.password),
                    "security_analysis": SecurityAnalyzer.analyze_network(net)
                }
                for net in self.networks
            ]
        }
    
    def generate_html_report(self) -> str:
        """Gera relatório em formato HTML com estilo"""
        html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DarkFeather - Relatório de Auditoria</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f3f4f6;
            margin: 0;
            padding: 20px;
            color: #1e293b;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            border-radius: 16px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            padding: 30px;
        }}
        h1 {{
            color: #0f172a;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 10px;
            margin-top: 0;
        }}
        h2 {{
            color: #334155;
            margin-top: 30px;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .card {{
            background-color: #f8fafc;
            border-radius: 12px;
            padding: 15px;
            border: 1px solid #e2e8f0;
        }}
        .card h3 {{
            margin: 0 0 10px 0;
            color: #64748b;
            font-size: 14px;
        }}
        .card .value {{
            font-size: 28px;
            font-weight: 600;
            color: #0f172a;
        }}
        .health {{
            background: linear-gradient(135deg, #2563eb, #1d4ed8);
            color: white;
            padding: 20px;
            border-radius: 12px;
            margin: 20px 0;
        }}
        .health .score {{
            font-size: 48px;
            font-weight: 700;
        }}
        .network {{
            background-color: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 15px;
            margin: 10px 0;
        }}
        .network-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 10px;
        }}
        .network-name {{
            font-size: 18px;
            font-weight: 600;
        }}
        .risk-badge {{
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }}
        .risk-Alto {{ background-color: #ef444420; color: #ef4444; }}
        .risk-Médio {{ background-color: #f59e0b20; color: #f59e0b; }}
        .risk-Baixo {{ background-color: #10b98120; color: #10b981; }}
        .flags {{
            margin-top: 10px;
            padding-left: 20px;
        }}
        .flag {{
            color: #64748b;
            margin: 5px 0;
        }}
        .footer {{
            margin-top: 30px;
            text-align: center;
            color: #94a3b8;
            font-size: 12px;
            border-top: 1px solid #e2e8f0;
            padding-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🦅 DarkFeather - Relatório de Auditoria WiFi</h1>
        <p>Gerado em: {self.generated_at.strftime('%d/%m/%Y %H:%M:%S')} | Usuário: {self.audit._get_system_info()['user']}</p>
        
        <div class="health">
            <div style="font-size: 18px; opacity: 0.9;">Saúde do Ambiente</div>
            <div class="score">{self.environment.get('health_score', 0)}/100</div>
            <div>{self.environment.get('health_status', 'N/A')}</div>
        </div>
        
        <h2>📊 Resumo</h2>
        <div class="summary">
            <div class="card">
                <h3>Total de Redes</h3>
                <div class="value">{self.environment.get('total_networks', 0)}</div>
            </div>
            <div class="card">
                <h3>Alto Risco</h3>
                <div class="value" style="color: #ef4444;">{self.environment.get('high_risk', 0)}</div>
            </div>
            <div class="card">
                <h3>Médio Risco</h3>
                <div class="value" style="color: #f59e0b;">{self.environment.get('medium_risk', 0)}</div>
            </div>
            <div class="card">
                <h3>Baixo Risco</h3>
                <div class="value" style="color: #10b981;">{self.environment.get('low_risk', 0)}</div>
            </div>
            <div class="card">
                <h3>Redes Abertas</h3>
                <div class="value">{self.environment.get('open_networks', 0)}</div>
            </div>
            <div class="card">
                <h3>WPA3</h3>
                <div class="value">{self.environment.get('wpa3_networks', 0)}</div>
            </div>
        </div>
        
        <h2>🔍 Detalhamento por Rede</h2>
        """
        
        for net in self.networks:
            analysis = SecurityAnalyzer.analyze_network(net)
            risk_class = f"risk-{analysis['risk_level']}"
            
            html += f"""
        <div class="network">
            <div class="network-header">
                <span class="network-name">{net.ssid}</span>
                <span class="risk-badge {risk_class}">{analysis['risk_level']} ({analysis['risk_score']}/100)</span>
            </div>
            <div><strong>Autenticação:</strong> {net.auth}</div>
            <div><strong>Criptografia:</strong> {net.encryption}</div>
            <div><strong>Última Conexão:</strong> {net.last_connection or 'Não disponível'}</div>
            """
            
            if analysis["flags"]:
                html += '<div class="flags"><strong>Observações:</strong>'
                for flag in analysis["flags"]:
                    html += f'<div class="flag">{flag}</div>'
                html += '</div>'
            
            if analysis["recommendations"]:
                html += '<div class="flags"><strong>Recomendações:</strong>'
                for rec in analysis["recommendations"]:
                    html += f'<div class="flag">→ {rec}</div>'
                html += '</div>'
            
            html += '</div>'
        
        html += f"""
        <div class="footer">
            <p>Relatório gerado por DarkFeather WiFi Analysis v2.0.0</p>
            <p>Hash SHA256: {hashlib.sha256(str(self.environment).encode()).hexdigest()[:32]}...</p>
        </div>
    </div>
</body>
</html>"""
        
        return html
    
    def save_report(self, format: str = "txt") -> Path:
        """
        Salva relatório em arquivo e registra na auditoria
        
        Args:
            format: "txt", "json" ou "html"
        
        Returns:
            Path do arquivo salvo
        """
        import hashlib
        
        if format.lower() == "json":
            filename = self.generate_filename("json")
            content = json.dumps(self.generate_json_report(), indent=2, ensure_ascii=False)
        elif format.lower() == "html":
            filename = self.generate_filename("html")
            content = self.generate_html_report()
        else:
            filename = self.generate_filename("txt")
            content = self.generate_text_report()
        
        # Salvar arquivo
        filename.write_text(content, encoding="utf-8")
        
        # Registrar na auditoria
        self.audit.log_report_generated(filename, content)
        
        return filename
    
    def save_all_formats(self) -> List[Path]:
        """Salva relatório em todos os formatos disponíveis"""
        paths = []
        for fmt in ["txt", "json", "html"]:
            try:
                path = self.save_report(fmt)
                paths.append(path)
            except Exception as e:
                print(f"Erro ao salvar formato {fmt}: {e}")
        return paths