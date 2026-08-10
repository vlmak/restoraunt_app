import sys
import traceback
from PyQt5.QtWidgets import QApplication, QMessageBox
from src.ui.auth_window import AuthWindow


def main():
    try:
        app = QApplication(sys.argv)
        window = AuthWindow()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print("=" * 60)
        print("КРИТИЧЕСКАЯ ОШИБКА:")
        traceback.print_exc()
        print("=" * 60)
        app = QApplication(sys.argv)
        QMessageBox.critical(
            None,
            "Ошибка запуска",
            f"Произошла критическая ошибка:\n\n{str(e)}\n\n"
            "Смотри консоль"
        )
        sys.exit(1)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AuthWindow()
    window.show()
    sys.exit(app.exec_())