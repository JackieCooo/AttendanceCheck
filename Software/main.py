import sys
import os
from PySide6.QtWidgets import QApplication
from Gui.Panels import MainWindow


def main():
    if not os.path.exists('./data'):
        os.mkdir('./data')
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == '__main__':
    main()
