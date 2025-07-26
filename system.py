import subprocess
import os
import xml.etree.ElementTree as ET
import glob
import time
import wmi
import ctypes
import sys
import re
from datetime import datetime

class WiFiProfileSystem:
    def __init__(self):
        self._wmi_conn = None
        self._last_update = None
        self.check_admin()

    def check_admin(self):
        if not self.is_admin():
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
            sys.exit()

    def is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    @property
    def wmi_connection(self):
        if self._wmi_conn is None:
            try:
                self._wmi_conn = wmi.WMI()
            except Exception as e:
                print(f"Erro WMI: {e}")
                return None
        return self._wmi_conn

    def get_adapter_names(self):
        adapter_map = {}
        try:
            c = self.wmi_connection
            if c:
                for adapter in c.Win32_NetworkAdapter():
                    if adapter.GUID and adapter.Name:
                        clean_guid = adapter.GUID.upper().replace("{", "").replace("}", "")
                        adapter_map[clean_guid] = adapter.Name
        except Exception as e:
            print(f"Erro adaptadores: {e}")
        return adapter_map

    def get_ascii_key(self, profile_name):
        try:
            result = subprocess.run(
                ["netsh", "wlan", "show", "profile", profile_name, "key=clear"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
                creationflags=subprocess.CREATE_NO_WINDOW,
                timeout=10
            )
            
            if result.returncode != 0:
                return ""
                
            key_patterns = [
                r"Conteúdo da Chave\s*:\s*(.+)",
                r"Key Content\s*:\s*(.+)",
                r"Contenido de la Clave\s*:\s*(.+)"
            ]
            
            for pattern in key_patterns:
                match = re.search(pattern, result.stdout)
                if match:
                    return match.group(1).strip()
                    
        except Exception as e:
            print(f"Erro netsh: {e}")
        return ""

    def parse_xml_profile(self, path, adapter_names):
        try:
            tree = ET.parse(path)
            root = tree.getroot()
            ns = {"ms": "http://www.microsoft.com/networking/WLAN/profile/v1"}

            ssid = root.find(".//ms:name", ns).text
            key_material = root.find(".//ms:keyMaterial", ns)
            key_hex = key_material.text.encode("utf-8").hex() if key_material else ""
            
            raw_guid = path.split("\\")[-2]
            adapter_guid = raw_guid.upper().replace("{", "").replace("}", "")
            adapter_name = adapter_names.get(adapter_guid, "Desconhecido")

            auth = root.find(".//ms:authentication", ns)
            encrypt = root.find(".//ms:encryption", ns)
            conn_type = root.find(".//ms:connectionType", ns)

            mod_time = os.path.getmtime(path)
            formatted_time = datetime.fromtimestamp(mod_time).strftime("%d/%m/%Y %H:%M:%S")

            return {
                "SSID": ssid,
                "Senha (ASCII)": self.get_ascii_key(ssid),
                "Senha (HEX)": key_hex,
                "Adaptador": adapter_name,
                "GUID Adaptador": raw_guid,
                "Autenticação": auth.text if auth else "N/A",
                "Criptografia": encrypt.text if encrypt else "N/A",
                "Tipo de Conexão": conn_type.text if conn_type else "N/A",
                "Modificado em": formatted_time,
                "Caminho do Perfil": path,
                "_timestamp": mod_time
            }
            
        except Exception as e:
            print(f"Erro XML {path}: {e}")
            return None

    def extract_profiles(self):
        self._last_update = time.time()
        results = []
        adapter_names = self.get_adapter_names()
        
        try:
            xml_paths = glob.glob(
                r"C:\ProgramData\Microsoft\Wlansvc\Profiles\Interfaces\*\*.xml"
            )
            
            if not xml_paths:
                print("Nenhum perfil encontrado")
                return results

            for path in xml_paths:
                profile_data = self.parse_xml_profile(path, adapter_names)
                if profile_data:
                    results.append(profile_data)

            results.sort(key=lambda x: (x["SSID"].lower(), -x["_timestamp"]))
            
        except Exception as e:
            print(f"Erro geral: {e}")
            
        return results

    def get_current_time(self):
        return datetime.now().strftime("%d/%m/%Y %H:%M:%S")