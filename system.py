import subprocess
import os
import ctypes
import xml.etree.ElementTree as ET
import glob
import time
import wmi

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def get_adapter_names():
    adapter_map = {}
    try:
        c = wmi.WMI()
        for adapter in c.Win32_NetworkAdapter():
            guid = adapter.GUID
            name = adapter.Name
            if guid and name:
                clean_guid = guid.upper().replace("{", "").replace("}", "")
                adapter_map[clean_guid] = name
    except Exception as e:
        print("Erro com WMI:", e)
    return adapter_map

def get_ascii_key(profile):
    try:
        output = subprocess.check_output(["netsh", "wlan", "show", "profile", profile, "key=clear"], 
                                       text=True, encoding="utf-8", errors="ignore")
        for line in output.splitlines():
            if "Conteúdo da Chave" in line or "Key Content" in line:
                return line.split(":")[1].strip()
    except:
        return ""
    return ""

def extract_profiles():
    results = []
    xml_paths = glob.glob(r"C:\ProgramData\Microsoft\Wlansvc\Profiles\Interfaces\*\*.xml")
    adapter_names = get_adapter_names()

    for path in xml_paths:
        try:
            tree = ET.parse(path)
            root = tree.getroot()
            ns = {"ms": "http://www.microsoft.com/networking/WLAN/profile/v1"}

            ssid = root.find(".//ms:name", ns).text
            key_material = root.find(".//ms:keyMaterial", ns)
            key_ascii = get_ascii_key(ssid)
            key_hex = key_material.text.encode("utf-8").hex() if key_material is not None else ""

            auth = root.find(".//ms:authentication", ns)
            encrypt = root.find(".//ms:encryption", ns)
            conn_type = root.find(".//ms:connectionType", ns)

            raw_guid = path.split("\\")[-2]
            adapter_guid = raw_guid.upper().replace("{", "").replace("}", "")
            adapter_name = adapter_names.get(adapter_guid, "Desconhecido")

            info = {
                "SSID": ssid,
                "Senha (ASCII)": key_ascii,
                "Senha (HEX)": key_hex,
                "Adaptador": adapter_name,
                "GUID Adaptador": raw_guid,
                "Autenticação": auth.text if auth is not None else "",
                "Criptografia": encrypt.text if encrypt is not None else "",
                "Tipo de Conexão": conn_type.text if conn_type is not None else "",
                "Modificado em": time.strftime('%d/%m/%Y %H:%M:%S', time.localtime(os.path.getmtime(path))),
                "Caminho do Perfil": path
            }

            results.append(info)
        except Exception as e:
            print("Erro ao processar XML:", e)
    return results