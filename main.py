import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from GUI.Gui import LibraryBorrowSystem
from GUI.loan import OverdueGUI

class LibraryApp:
    def __init__(self):
        self.app = LibraryBorrowSystem()
        self.setup_navigation()

    def setup_navigation(self):
        self.app.overdue_button.command = self.open_overdue_gui

    def open_overdue_gui(self):
        self.app.app.hide()
        self.overdue_app = OverdueGUI()
        self.overdue_app.return_button.command = self.return_to_main
        self.overdue_app.app.display()

    def return_to_main(self):
        self.overdue_app.app.destroy()
        self.app.app.show()


if __name__ == "__main__":
    LibraryApp()