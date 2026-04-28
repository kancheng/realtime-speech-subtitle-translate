"""PyQt stylesheet definitions."""

MAIN_STYLESHEET = """
QMainWindow {
    background-color: #111418;
}
QLabel {
    color: #E7EDF3;
    font-size: 18px;
}
QPushButton {
    background-color: #2E7D32;
    color: #FFFFFF;
    border: none;
    border-radius: 10px;
    padding: 12px 16px;
    font-size: 20px;
    font-weight: 600;
    min-height: 52px;
}
QPushButton:disabled {
    background-color: #455A64;
    color: #CFD8DC;
}
QPushButton#stopButton {
    background-color: #1B5E20;
}
QPushButton#pptButton {
    background-color: #388E3C;
}
QComboBox {
    background-color: #1E1E1E;
    color: #E7EDF3;
    border: 1px solid #2E7D32;
    border-radius: 8px;
    padding: 8px;
    min-height: 42px;
    font-size: 18px;
}
QFrame#subtitlePanel {
    background-color: #0D1117;
    border: 1px solid #1B5E20;
    border-radius: 12px;
}
QTextEdit {
    background-color: #0D1117;
    color: #E7EDF3;
    border: 1px solid #1B5E20;
    border-radius: 10px;
    padding: 8px;
    font-size: 28px;
}
"""

