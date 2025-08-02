from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QStackedWidget, QWidget, QLineEdit,
    QGridLayout, QHBoxLayout, QVBoxLayout, QPushButton, QFrame, QLabel, QSizePolicy
)
from PyQt5.QtGui import QIcon, QPainter, QColor, QMovie, QTextCharFormat, QFont, QPixmap
from PyQt5.QtCore import Qt, QSize, QTimer, pyqtSignal, QObject
from dotenv import dotenv_values
import sys
import os

env_vars = dotenv_values(".env")
ASSISTANT_NAME = env_vars.get("Assistantname", "Assistant")
CURRENT_DIR = os.getcwd()
TEMP_DIR_PATH = os.path.join(CURRENT_DIR, "Frontend", "Files")
GRAPHICS_DIR_PATH = os.path.join(CURRENT_DIR, "Frontend", "Graphics")

# --- Signal Emitter for thread-safe communication ---
class SignalEmitter(QObject):
    status_signal = pyqtSignal(str)
    text_signal = pyqtSignal(str)

_signal_emitter = SignalEmitter()

def set_assistant_status(status):
    _signal_emitter.status_signal.emit(status)

def show_text_to_screen(text):
    _signal_emitter.text_signal.emit(text)

def answer_modifier(answer):
    """Remove empty lines from answer."""
    return '\n'.join(line for line in answer.split('\n') if line.strip())

def query_modifier(query):
    """Format query as a question or statement."""
    new_query = query.lower().strip()
    question_words = [
        "how", "what", "who", "where", "when", "why", "which", "whose", "whom",
        "can you", "what's", "where's", "how's"
    ]
    if any(new_query.startswith(word + " ") for word in question_words):
        new_query = new_query.rstrip('.?!') + '?'
    else:
        new_query = new_query.rstrip('.?!') + '.'
    return new_query.capitalize()

def set_microphone_status(command):
    with open(os.path.join(TEMP_DIR_PATH, "Mic.data"), "w", encoding='utf-8') as file:
        file.write(command)

def get_microphone_status():
    with open(os.path.join(TEMP_DIR_PATH, "Mic.data"), "r", encoding='utf-8') as file:
        return file.read()

def get_assistant_status():
    with open(os.path.join(TEMP_DIR_PATH, "Status.data"), "r", encoding='utf-8') as file:
        return file.read()

def mic_button_initialized():
    set_microphone_status("False")

def mic_button_closed():
    set_microphone_status("True")

def graphics_directory_path(filename):
    return os.path.join(GRAPHICS_DIR_PATH, filename)

def temp_directory_path(filename):
    return os.path.join(TEMP_DIR_PATH, filename)

# --- Chat Section Widget ---
class ChatSection(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(-10, 40, -10, 100)
        layout.setSpacing(-100)

        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        font = QFont()
        font.setPointSize(13)
        self.chat_text_edit.setFont(font)
        layout.addWidget(self.chat_text_edit)

        self.gif_label = QLabel(self)
        self.gif_label.setStyleSheet("border: none;")
        movie = QMovie(graphics_directory_path('Jarvis.gif'))
        movie.setScaledSize(QSize(480, 270))
        self.gif_label.setMovie(movie)
        self.gif_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        movie.start()
        layout.addWidget(self.gif_label)

        self.label = QLabel("")
        self.label.setStyleSheet(
            "color: white; font-size:16px; margin-right: 195px; border: none; margin-top: -30px;"
        )
        self.label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.label)
        layout.setSpacing(-10)

        _signal_emitter.status_signal.connect(self.speech_recog_text)
        _signal_emitter.text_signal.connect(self.load_messages)
        self.chat_text_edit.viewport().installEventFilter(self)

        self.setStyleSheet("""
            QScrollBar:vertical {
                border: none;
                background: black;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: white;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                background: black;
                height: 10px;
            }
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                border: none;
                color: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)

    def load_messages(self, text):
        self.add_message(text, color='White')
        self.chat_text_edit.verticalScrollBar().setValue(
            self.chat_text_edit.verticalScrollBar().maximum()
        )

    def speech_recog_text(self, text):
        self.label.setText(text)

    def add_message(self, message, color):
        cursor = self.chat_text_edit.textCursor()
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        fmt.setTopMargin(10)
        fmt.setLeftMargin(10)
        cursor.setCharFormat(fmt)
        cursor.insertText(message + "\n")
        self.chat_text_edit.setTextCursor(cursor)

# --- Initial Screen Widget ---
class InitialScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)

        gif_label = QLabel(self)
        movie = QMovie(graphics_directory_path('Jarvis.gif'))
        max_gif_size_h = int(screen_width / 16 * 9)
        movie.setScaledSize(QSize(screen_width, max_gif_size_h))
        gif_label.setMovie(movie)
        gif_label.setScaledContents(True)
        gif_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        gif_label.setAlignment(Qt.AlignCenter)
        movie.start()

        self.icon = QLabel(self)
        self.toggled = True
        self.load_icon(graphics_directory_path('Mic_on.png'))
        self.icon.setScaledContents(True)
        self.icon.setAlignment(Qt.AlignCenter)
        self.icon.mousePressEvent = self.toggle_icon

        self.label = QLabel("")
        self.label.setStyleSheet("color: white; font-size:16px; margin-bottom:0;")
        self.label.setAlignment(Qt.AlignCenter)

        content_layout.addWidget(gif_label, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.icon, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.label, alignment=Qt.AlignCenter)
        content_layout.setContentsMargins(0, 0, 0, 150)
        self.setLayout(content_layout)
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)
        self.setStyleSheet("background-color: black;")

        _signal_emitter.status_signal.connect(self.speech_recog_text)

    def speech_recog_text(self, text):
        self.label.setText(text)

    def load_icon(self, path, width=60, height=60):
        pixmap = QPixmap(path)
        new_pixmap = pixmap.scaled(width, height)
        self.icon.setPixmap(new_pixmap)

    def toggle_icon(self, event=None):
        if self.toggled:
            self.load_icon(graphics_directory_path('Mic_on.png'))
            mic_button_initialized()
        else:
            self.load_icon(graphics_directory_path('Mic_off.png'))
            mic_button_closed()
        self.toggled = not self.toggled

# --- Message Screen Widget ---
class MessageScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        layout = QVBoxLayout()
        label = QLabel("")
        chat_section = ChatSection()
        layout.addWidget(label)
        layout.addWidget(chat_section)
        self.setLayout(layout)
        self.setStyleSheet("background-color: black;")
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)

# --- Custom Top Bar Widget ---
class CustomTopBar(QWidget):
    def __init__(self, parent, stacked_widget):
        super().__init__(parent)
        self.stacked_widget = stacked_widget
        self.init_ui()

    def init_ui(self):
        self.setFixedHeight(50)
        layout = QHBoxLayout()
        self.setLayout(layout)

        title_label = QLabel(f" {ASSISTANT_NAME.capitalize()} AI ")
        title_label.setStyleSheet("color: black; font-size: 18px; background-color:white;")

        self.home_button = QPushButton()
        self.home_button.setIcon(QIcon(graphics_directory_path("Home.png")))
        self.home_button.setText(" Home")
        self.home_button.setStyleSheet("height:40px; line-height:40px; background-color:white; color: black;")

        self.message_button = QPushButton()
        self.message_button.setIcon(QIcon(graphics_directory_path("Chats.png")))
        self.message_button.setText(" Chat")
        self.message_button.setStyleSheet("height:40px; line-height:40px; background-color:white; color: black;")

        self.minimize_button = QPushButton()
        self.minimize_button.setIcon(QIcon(graphics_directory_path("Minimize2.png")))
        self.minimize_button.setStyleSheet("background-color:white;")
        self.minimize_button.clicked.connect(self.minimize_window)

        self.maximize_button = QPushButton()
        self.maximize_icon = QIcon(graphics_directory_path("Maximize.png"))
        self.restore_icon = QIcon(graphics_directory_path('Minimize.png'))
        self.maximize_button.setIcon(self.maximize_icon)
        self.maximize_button.setStyleSheet("background-color:white;")
        self.maximize_button.setFlat(True)
        self.maximize_button.clicked.connect(self.maximize_window)

        self.close_button = QPushButton()
        self.close_button.setIcon(QIcon(graphics_directory_path("Close.png")))
        self.close_button.setStyleSheet("background-color:white;")
        self.close_button.clicked.connect(self.close_window)

        line_frame = QFrame()
        line_frame.setFrameShape(QFrame.HLine)
        line_frame.setFrameShadow(QFrame.Sunken)
        line_frame.setStyleSheet("border-color: black; capitalize;")

        self.home_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        self.message_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))

        layout.addWidget(title_label)
        layout.addStretch(1)
        layout.addWidget(self.home_button)
        layout.addWidget(self.message_button)
        layout.addStretch(1)
        layout.addWidget(self.minimize_button)
        layout.addWidget(self.maximize_button)
        layout.addWidget(self.close_button)
        layout.addWidget(line_frame)

        self.draggable = True
        self.offset = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.white)
        super().paintEvent(event)

    def minimize_window(self):
        self.parent().showMinimized()

    def maximize_window(self):
        if self.parent().isMaximized():
            self.parent().showNormal()
            self.maximize_button.setIcon(self.maximize_icon)
        else:
            self.parent().showMaximized()
            self.maximize_button.setIcon(self.restore_icon)

    def close_window(self):
        self.parent().close()

    def mousePressEvent(self, event):
        if self.draggable:
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.draggable and self.offset:
            new_pos = event.globalPos() - self.offset
            self.parent().move(new_pos)

# --- Main Window ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.init_ui()

    def init_ui(self):
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        stacked_widget = QStackedWidget(self)
        initial_screen = InitialScreen()
        message_screen = MessageScreen()
        stacked_widget.addWidget(initial_screen)
        stacked_widget.addWidget(message_screen)

        self.setGeometry(0, 0, screen_width, screen_height)
        self.setStyleSheet("background-color: black;")

        top_bar = CustomTopBar(self, stacked_widget)
        self.setMenuWidget(top_bar)
        self.setCentralWidget(stacked_widget)

# Entry point for GUI creation
def GraphicalUserInterface():
    return MainWindow()

# --- Standalone Run Block ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GraphicalUserInterface()
    window.show()
    sys.exit(app.exec_())