from Menu.menu_model           import MenuModel
from Menu.menu_view            import MenuView
from Menu.main_menu_controller import MainMenuController
from PyQt5.QtWidgets           import QApplication
import sys

if __name__ == "__main__":

    app   = QApplication( sys.argv )
    size  = app.primaryScreen().size()
    model = MenuModel()
    view  = MenuView( size, model )
    controller = MainMenuController( model )
    controller.startThread()
    view.show()
    model.run()