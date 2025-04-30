import sys
from PyQt5.QtWidgets import QApplication
from screening_app import ScreeningApp

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ScreeningApp()
    ex.show()
    sys.exit(app.exec_())