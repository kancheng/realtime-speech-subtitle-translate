"""PyQt stylesheet definitions."""

MAIN_STYLESHEET = """
QMainWindow {
    background-color: #111418;
}
QLabel {
    color: #E7EDF3;
}
QPushButton {
    background-color: #1E88E5;
    color: #FFFFFF;
    border: none;
    border-radius: 4px;
    padding: 8px 14px;
    font-size: 14px;
}
QPushButton:disabled {
    background-color: #455A64;
    color: #CFD8DC;
}
QComboBox {
    background-color: #1E1E1E;
    color: #E7EDF3;
    border: 1px solid #37474F;
    border-radius: 4px;
    padding: 5px;
}
QFrame#subtitlePanel {
    background-color: #0D1117;
    border: 1px solid #263238;
    border-radius: 8px;
}
QTextEdit {
    background-color: #0D1117;
    color: #E7EDF3;
    border: none;
}
"""

