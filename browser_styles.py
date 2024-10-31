class BrowserStyles:
    LIGHT_STYLE = """
        QMainWindow {
            background-color: #f0f0f0;
        }
        
        QMenuBar {
            background-color: #ffffff;
            border-bottom: 1px solid #dcdcdc;
        }
        
        QMenuBar::item {
            padding: 5px 10px;
            background: transparent;
        }
        
        QMenuBar::item:selected {
            background: #e0e0e0;
            border-radius: 4px;
        }
        
        QMenu {
            background-color: #ffffff;
            border: 1px solid #dcdcdc;
        }
        
        QMenu::item {
            padding: 5px 30px 5px 20px;
        }
        
        QMenu::item:selected {
            background-color: #e0e0e0;
        }
        
        QToolBar {
            background-color: #ffffff;
            border-bottom: 1px solid #dcdcdc;
            padding: 2px;
            spacing: 3px;
        }
        
        QPushButton {
            background-color: #ffffff;
            border: 1px solid #dcdcdc;
            border-radius: 4px;
            padding: 5px 10px;
            min-width: 80px;
        }
        
        QPushButton:hover {
            background-color: #f0f0f0;
            border: 1px solid #c0c0c0;
        }
        
        QPushButton:pressed {
            background-color: #e0e0e0;
        }
        
        QLineEdit {
            border: 1px solid #dcdcdc;
            border-radius: 4px;
            padding: 5px;
            background: #ffffff;
        }
        
        QLineEdit:focus {
            border: 1px solid #0078d4;
        }
        
        QTabWidget::pane {
            border: 1px solid #dcdcdc;
            background: white;
        }
        
        QTabBar::tab {
            background: #f0f0f0;
            border: 1px solid #dcdcdc;
            border-bottom: none;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            padding: 5px 10px;
            margin-right: 2px;
        }
        
        QTabBar::tab:selected {
            background: white;
        }
        
        QTabBar::tab:hover {
            background: #e0e0e0;
        }
        
        QStatusBar {
            background: #ffffff;
            border-top: 1px solid #dcdcdc;
        }
        
        QProgressBar {
            border: 1px solid #dcdcdc;
            border-radius: 4px;
            text-align: center;
        }
        
        QProgressBar::chunk {
            background-color: #0078d4;
        }
    """

    DARK_STYLE = """
        QMainWindow {
            background-color: #1e1e1e;
            color: #ffffff;
        }
        
        QMenuBar {
            background-color: #2d2d2d;
            color: #ffffff;
            border-bottom: 1px solid #3d3d3d;
        }
        
        QMenuBar::item {
            padding: 5px 10px;
            background: transparent;
        }
        
        QMenuBar::item:selected {
            background: #3d3d3d;
            border-radius: 4px;
        }
        
        QMenu {
            background-color: #2d2d2d;
            color: #ffffff;
            border: 1px solid #3d3d3d;
        }
        
        QMenu::item {
            padding: 5px 30px 5px 20px;
        }
        
        QMenu::item:selected {
            background-color: #3d3d3d;
        }
        
        QToolBar {
            background-color: #2d2d2d;
            border-bottom: 1px solid #3d3d3d;
            padding: 2px;
            spacing: 3px;
        }
        
        QPushButton {
            background-color: #3d3d3d;
            color: #ffffff;
            border: 1px solid #4d4d4d;
            border-radius: 4px;
            padding: 5px 10px;
            min-width: 80px;
        }
        
        QPushButton:hover {
            background-color: #4d4d4d;
            border: 1px solid #5d5d5d;
        }
        
        QPushButton:pressed {
            background-color: #5d5d5d;
        }
        
        QLineEdit {
            border: 1px solid #3d3d3d;
            border-radius: 4px;
            padding: 5px;
            background: #2d2d2d;
            color: #ffffff;
        }
        
        QLineEdit:focus {
            border: 1px solid #0078d4;
        }
        
        QTabWidget::pane {
            border: 1px solid #3d3d3d;
            background: #2d2d2d;
        }
        
        QTabBar::tab {
            background: #3d3d3d;
            color: #ffffff;
            border: 1px solid #4d4d4d;
            border-bottom: none;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            padding: 5px 10px;
            margin-right: 2px;
        }
        
        QTabBar::tab:selected {
            background: #4d4d4d;
        }
        
        QTabBar::tab:hover {
            background: #5d5d5d;
        }
        
        QStatusBar {
            background: #2d2d2d;
            color: #ffffff;
            border-top: 1px solid #3d3d3d;
        }
        
        QProgressBar {
            border: 1px solid #3d3d3d;
            border-radius: 4px;
            text-align: center;
            color: #ffffff;
        }
        
        QProgressBar::chunk {
            background-color: #0078d4;
        }
        
        QToolButton {
            background-color: #3d3d3d;
            color: #ffffff;
            border: 1px solid #4d4d4d;
            border-radius: 4px;
            padding: 5px;
        }
        
        QToolButton:hover {
            background-color: #4d4d4d;
        }
        
        QToolButton:pressed {
            background-color: #5d5d5d;
        }
        
        QCheckBox {
            color: #ffffff;
        }
        
        QCheckBox::indicator {
            width: 13px;
            height: 13px;
        }
        
        QCheckBox::indicator:unchecked {
            background-color: #2d2d2d;
            border: 1px solid #4d4d4d;
        }
        
        QCheckBox::indicator:checked {
            background-color: #0078d4;
            border: 1px solid #0078d4;
        }
    """

    @staticmethod
    def get_style(dark_mode=False):
        return BrowserStyles.DARK_STYLE if dark_mode else BrowserStyles.LIGHT_STYLE