import sys
from PyQt5.QtWidgets import QApplication
from ui import WiFiProfileViewerUI
from system import WiFiProfileSystem


class WiFiProfileController:
    def __init__(self):
        self.system = WiFiProfileSystem()
        self.app = QApplication(sys.argv)
        self.ui = WiFiProfileViewerUI(self)

    def show_profiles(self):
        try:
            profiles = self.system.extract_profiles()
            if profiles:
                self.ui.display_profiles(profiles)
            else:
                self.ui.status_bar.showMessage(
                    "Nenhum perfil encontrado ou erro na leitura"
                )
        except Exception as e:
            self.ui.status_bar.showMessage(f"Erro: {str(e)}")
            print(f"Erro ao buscar perfis: {e}")

    def get_current_time(self):
        from datetime import datetime

        return datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    def run(self):
        self.ui.show()
        sys.exit(self.app.exec_())


if __name__ == "__main__":
    controller = WiFiProfileController()
    controller.run()
