import sys
import json
import os
import sqlite3
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QFrame,
    QVBoxLayout, QStackedWidget, QSpacerItem, QSizePolicy, QComboBox, QHBoxLayout,
    QMainWindow, QToolButton
)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QRect
from PyQt5.QtWidgets import QGraphicsDropShadowEffect
from PyQt5.QtGui import QColor, QPixmap
from Cpap_dash import DashboardPage
from BiPap_dash import BiPapDashboardPage

# Database setup
def init_database():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        serial_number TEXT UNIQUE NOT NULL,
        model_number TEXT NOT NULL,
        device_type TEXT NOT NULL,
        contact_number TEXT NOT NULL,
        password TEXT NOT NULL,
        registration_date TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

# Initialize database when module is imported
init_database()

# Save user data to JSON
def save_user_to_json(user_data):
    try:
        json_file = "signupdetails.json"
        data = []
        
        # Load existing data if file exists
        if os.path.exists(json_file):
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
            except:
                data = []
        
        # Check if user already exists
        user_exists = False
        for user in data:
            if user.get('serial_number') == user_data.get('serial_number'):
                user_exists = True
                break
        
        # Add new user if not exists
        if not user_exists:
            data.append(user_data)
            with open(json_file, 'w') as f:
                json.dump(data, f, indent=4)
            return True
        return False
    except Exception as e:
        print(f"Error saving to JSON: {e}")
        return False

# ---------- Database Helper Functions ----------
class DatabaseManager:
    @staticmethod
    def add_user(serial_number, model_number, device_type, contact_number, password):
        try:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            registration_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute('''
                INSERT INTO users (serial_number, model_number, device_type, contact_number, password, registration_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (serial_number, model_number, device_type, contact_number, password, registration_date))
            conn.commit()
            conn.close()
            
            # Also save to JSON
            user_data = {
                "serial_number": serial_number,
                "model_number": model_number,
                "device_type": device_type,
                "contact_number": contact_number,
                "password": password,
                "registration_date": registration_date
            }
            save_user_to_json(user_data)
            
            return True
        except sqlite3.IntegrityError:
            return False  # Serial number already exists
        except Exception as e:
            print(f"Database error: {e}")
            return False

    @staticmethod
    def get_user(serial_number):
        try:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE serial_number = ?', (serial_number,))
            user = cursor.fetchone()
            conn.close()
            
            if user:
                # Convert to dictionary with column names
                columns = ['id', 'serial_number', 'model_number', 'device_type', 'contact_number', 'password', 'registration_date']
                return dict(zip(columns, user))
            return None
        except Exception as e:
            print(f"Database error: {e}")
            return None

    @staticmethod
    def user_exists(serial_number):
        try:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute('SELECT 1 FROM users WHERE serial_number = ?', (serial_number,))
            exists = cursor.fetchone() is not None
            conn.close()
            return exists
        except Exception as e:
            print(f"Database error: {e}")
            return False



# ---------- Modern Popup Notification ----------
class NotificationPopup(QFrame):
    def __init__(self, parent, message, type="info"):
        super().__init__(parent)
        self.setFixedSize(300, 80)
        self.move(parent.width() // 2 - 150, -100)  # start hidden
        self.setStyleSheet("""
            QFrame {
                border-radius: 12px;
                background-color: #ffffff;
                border: 2px solid #ddd;
            }
        """)

        # Colors based on type
        colors = {
            "success": "#28a745",
            "error": "#dc3545",
            "warning": "#ffc107",
            "info": "#17a2b8"
        }
        color = colors.get(type, "#17a2b8")

        # Label inside popup
        self.label = QLabel(message, self)
        self.label.setStyleSheet(f"color: {color}; font-size: 14px; font-weight: bold;")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setGeometry(10, 20, 280, 40)

        # Slide down animation
        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(500)
        self.anim.setStartValue(QRect(self.x(), -100, self.width(), self.height()))
        self.anim.setEndValue(QRect(self.x(), 50, self.width(), self.height()))
        self.anim.start()

        # Auto close after 3 sec
        QTimer.singleShot(3000, self.close_popup)

    def close_popup(self):
        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(500)
        self.anim.setStartValue(QRect(self.x(), self.y(), self.width(), self.height()))
        self.anim.setEndValue(QRect(self.x(), -100, self.width(), self.height()))
        self.anim.finished.connect(self.deleteLater)
        self.anim.start()


# ---------- Shadow Frame ----------
class ShadowFrame(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
            }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 150))
        self.setGraphicsEffect(shadow)


# ---------- Title Bar ----------
class TitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(30)
        self.setStyleSheet("background-color: #f0f0f0;")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 0, 5, 0)

        self.title = QLabel("Device Registration System")
        self.title.setStyleSheet("color: #333; font-weight: bold;")

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        self.minimize_btn = QToolButton()
        self.minimize_btn.setText("−")
        self.minimize_btn.setStyleSheet("QToolButton { border: none; background: transparent; font-size: 16px; }")
        self.minimize_btn.clicked.connect(self.parent.showMinimized)

        self.maximize_btn = QToolButton()
        self.maximize_btn.setText("□")
        self.maximize_btn.setStyleSheet("QToolButton { border: none; background: transparent; font-size: 14px; }")
        self.maximize_btn.clicked.connect(self.toggle_maximize)

        self.close_btn = QToolButton()
        self.close_btn.setText("X")
        self.close_btn.setStyleSheet("QToolButton { border: none; background: transparent; font-size: 16px; }")
        self.close_btn.clicked.connect(self.parent.close)

        layout.addWidget(self.title)
        layout.addWidget(spacer)
        layout.addWidget(self.minimize_btn)
        layout.addWidget(self.maximize_btn)
        layout.addWidget(self.close_btn)

    def toggle_maximize(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
        else:
            self.parent.showMaximized()


# ---------- Login Page ----------
class LoginPage(QWidget):
    def __init__(self, stacked_widget, main_window):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.main_window = main_window
        self.failed_attempts = {}
        self.locked_accounts = {}

        self.setStyleSheet("background: transparent;")
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)

        shadow_frame = ShadowFrame()
        form_layout = QVBoxLayout(shadow_frame)
        form_layout.setAlignment(Qt.AlignCenter)
        shadow_frame.setFixedSize(400, 450)

        # Logo
        logo_label = QLabel()
        logo_path = "CPAP-Dash/Assets/Logo.jpg"
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path).scaled(200, 110, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
        else:
            logo_label.setText("LOGO")
            logo_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        logo_label.setAlignment(Qt.AlignCenter)

        welcome_label = QLabel("Welcome at Deckmount ")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("""
                                    font-size: 22px; 
                                    font-weight: bold; 
                                    color: #2C3E50; 
                                    margin:25px ;
                                    """)

        form_layout.addWidget(logo_label)
        form_layout.addWidget(welcome_label)

        # Fields
        self.serial_number = QLineEdit()
        self.serial_number.setPlaceholderText("Serial Number")
        self.serial_number.setFixedSize(250, 40)
        self.serial_number.setStyleSheet("""
            QLineEdit {
                border: 2px solid #BDC3C7;
                border-radius: 10px;
                padding-left: 10px;
                font-size: 14px;
                background: #FDFEFE;
            }
            QLineEdit:focus {
                border: 2px solid #3498DB;
                background: #ECF6FC;
            }
        """)

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setFixedSize(250, 40)
        self.password.setStyleSheet("""
            QLineEdit {
                border: 2px solid #BDC3C7;
                border-radius: 10px;
                padding-left: 10px;
                font-size: 14px;
                background: #FDFEFE;
            }
            QLineEdit:focus {
                border: 2px solid #3498DB;
                background: #ECF6FC;
            }
        """)

        self.login_btn = QPushButton("Login")
        self.login_btn.setFixedSize(180, 40)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #3498DB, stop:1 #2ECC71);
                color: white;
                border-radius: 12px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #2980B9, stop:1 #27AE60);
            }
        """)
        
        self.signup_btn = QPushButton("Don't have an account? Sign Up")
        self.signup_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #2980B9;
                font-size: 13px;
                text-decoration: underline;
            }
            QPushButton:hover {
                color: #1ABC9C;
            }
        """)

        fields_layout = QVBoxLayout()
        fields_layout.addWidget(self.serial_number, alignment=Qt.AlignCenter)
        fields_layout.addWidget(self.password, alignment=Qt.AlignCenter)
        fields_layout.addWidget(self.login_btn, alignment=Qt.AlignCenter)
        fields_layout.addWidget(self.signup_btn, alignment=Qt.AlignCenter)
        form_layout.addLayout(fields_layout)

        main_layout.addWidget(shadow_frame)

        self.login_btn.clicked.connect(self.login)
        self.signup_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        
        self.bipap_login_btn = QPushButton("Login as BiPAP")
        self.bipap_login_btn.setFixedSize(180, 40)
        self.bipap_login_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #9b59b6, stop:1 #8e44ad);
                color: white;
                border-radius: 12px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #8e44ad, stop:1 #9b59b6);
            }
        """)
        fields_layout.addWidget(self.bipap_login_btn, alignment=Qt.AlignCenter)
        self.bipap_login_btn.clicked.connect(self.login_bipap)
        
    def login_bipap(self):
        serial = self.serial_number.text()
        pwd = self.password.text()
    
        if not serial or not pwd:
            NotificationPopup(self.main_window, "⚠ Please enter both fields", "warning").show()
            return
    
        # Check if user exists in database
        user = DatabaseManager.get_user(serial)
        if not user:
            NotificationPopup(self.main_window, "❌ User not found", "error").show()
            return
    
        if user['password'] == pwd:
            # Successful login to BiPAP
            self.main_window.setStyleSheet("background-color: #cfd1e3;")
            self.main_window.title_bar.hide()
            bipap_dashboard = BiPapDashboardPage(self.stacked_widget, user)
            self.stacked_widget.addWidget(bipap_dashboard)
            self.stacked_widget.setCurrentWidget(bipap_dashboard)
            self.main_window.showFullScreen()
            NotificationPopup(self.main_window, "✅ BiPAP Login Successful!", "success").show()
        else:
            NotificationPopup(self.main_window, "❌ Invalid password", "error").show()

  
    def is_account_locked(self, serial):
        if serial in self.locked_accounts:
            lock_time = self.locked_accounts[serial]
            if datetime.now() < lock_time:
                remaining = lock_time - datetime.now()
                return f"🔒 Account locked. Try again in {int(remaining.total_seconds()//60)}m {int(remaining.total_seconds()%60)}s"
            else:
                del self.locked_accounts[serial]
                self.failed_attempts[serial] = 0
        return None


    def login(self):
        serial = self.serial_number.text()
        pwd = self.password.text()

        if not serial or not pwd:
            NotificationPopup(self.main_window, "⚠ Please enter both fields", "warning").show()
            return

        lock_status = self.is_account_locked(serial)
        if lock_status:
            NotificationPopup(self.main_window, lock_status, "warning").show()
            return

        # Check if user exists in database
        user = DatabaseManager.get_user(serial)
        if not user:
            self.handle_failed_login(serial)
            NotificationPopup(self.main_window, "❌ User not found", "error").show()
            return

        # Verify password
        if user['password'] == pwd:
            # Successful login
            if serial in self.failed_attempts:
                del self.failed_attempts[serial]
            self.main_window.setStyleSheet("background-color: #cfd1e3;")  # bg color of side bar in dashboard
            self.main_window.title_bar.hide()
            dashboard = DashboardPage(self.stacked_widget, user)
            self.stacked_widget.addWidget(dashboard)
            self.stacked_widget.setCurrentWidget(dashboard)
            self.main_window.showFullScreen()
            NotificationPopup(self.main_window, "✅ Login Successful!", "success").show()
        else:
            # Failed login
            self.handle_failed_login(serial)
            
    def handle_failed_login(self, serial):
        self.failed_attempts[serial] = self.failed_attempts.get(serial, 0) + 1
        if self.failed_attempts[serial] >= 3:
            self.locked_accounts[serial] = datetime.now() + timedelta(minutes=5)
            NotificationPopup(self.main_window, "🔒 Account locked for 5 mins", "warning").show()
        else:
            attempts_left = 3 - self.failed_attempts[serial]
            NotificationPopup(self.main_window, f"❌ Invalid login. {attempts_left} attempts left", "error").show()
            
            
        
# ---------- Signup Page ----------
class SignupPage(QWidget):
    def __init__(self, stacked_widget, main_window):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.main_window = main_window
        self.setStyleSheet("background: transparent;")

        main_layout = QVBoxLayout(self)
        shadow_frame = ShadowFrame()
        form_layout = QVBoxLayout(shadow_frame)
        shadow_frame.setFixedSize(380, 500)

        # Title
        title_label = QLabel("Create Account")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2C3E50;
            margin-bottom: 25px;
        """)

        # Fields
        self.serial_number = QLineEdit()
        self.serial_number.setPlaceholderText("🔑 Serial Number")
        self.serial_number.setFixedSize(300, 40)
        self.serial_number.setStyleSheet(self._field_style())

        self.model_number = QLineEdit()
        self.model_number.setPlaceholderText("📦 Model Number")
        self.model_number.setFixedSize(300, 40)
        self.model_number.setStyleSheet(self._field_style())

        self.device_type = QComboBox()
        self.device_type.addItems(["CPAP", "BiPAP"])
        self.device_type.setFixedSize(300, 40)
        self.device_type.setStyleSheet("""
            QComboBox {
                border: 2px solid #BDC3C7;
                border-radius: 10px;
                padding: 5px 10px;
                font-size: 14px;
                background: #FDFEFE;
            }
            QComboBox:focus {
                border: 2px solid #3498DB;
                background: #ECF6FC;
            }
        """)

        self.contact_number = QLineEdit()
        self.contact_number.setPlaceholderText("📞 Contact Number")
        self.contact_number.setFixedSize(300, 40)
        self.contact_number.setStyleSheet(self._field_style())

        self.password = QLineEdit()
        self.password.setPlaceholderText("🔒 Password")
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setFixedSize(300, 40)
        self.password.setStyleSheet(self._field_style())

        # Buttons
        self.signup_btn = QPushButton("Sign Up")
        self.signup_btn.setFixedSize(180, 35)
        self.signup_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #3498DB, stop:1 #2ECC71);
                color: white;
                border-radius: 12px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #2980B9, stop:1 #27AE60);
            }
        """)

        self.back_btn = QPushButton("← Back to Login")
        self.back_btn.setFixedSize(200, 40)
        self.back_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #95A5A6, stop:1 #7F8C8D);
                color: white;
                border-radius: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #7F8C8D, stop:1 #95A5A6);
            }
        """)

        # Layouts
        fields_layout = QVBoxLayout()
        fields_layout.setSpacing(15)
        for widget in [
            self.serial_number, self.model_number, self.device_type,
            self.contact_number, self.password, self.signup_btn, self.back_btn
        ]:
            fields_layout.addWidget(widget, alignment=Qt.AlignCenter)

        form_layout.addWidget(title_label)
        form_layout.addLayout(fields_layout)
        main_layout.addWidget(shadow_frame, alignment=Qt.AlignCenter)

        # Connections
        self.signup_btn.clicked.connect(self.signup)
        self.back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))

    def _field_style(self):
        """Reusable style for QLineEdit"""
        return """
            QLineEdit {
                border: 2px solid #BDC3C7;
                border-radius: 10px;
                padding-left: 10px;
                font-size: 14px;
                background: #FDFEFE;
            }
            QLineEdit:focus {
                border: 2px solid #3498DB;
                background: #ECF6FC;
            }
        """

    def signup(self):
        serial = self.serial_number.text()
        model = self.model_number.text()
        device = self.device_type.currentText()
        contact = self.contact_number.text()
        pwd = self.password.text()

        if not serial or not model or not contact or not pwd:
            NotificationPopup(self.main_window, "⚠ All fields required", "warning").show()
            return

        # Use DatabaseManager to add user (which also saves to JSON)
        success = DatabaseManager.add_user(serial, model, device, contact, pwd)
        if success:
            NotificationPopup(self.main_window, "🎉 Account Created!", "success").show()
            self.serial_number.clear()
            self.model_number.clear()
            self.contact_number.clear()
            self.password.clear()
            self.device_type.setCurrentIndex(0)
            self.stacked_widget.setCurrentIndex(0)
        else:
            NotificationPopup(self.main_window, "⚠ Serial Number already exists", "warning").show()

# ---------- Central Stacked Widget ----------
class CentralStackedWidget(QStackedWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.login_page = LoginPage(self, main_window)
        self.signup_page = SignupPage(self, main_window)
        self.addWidget(self.login_page)
        self.addWidget(self.signup_page)
        self.setCurrentIndex(0)


# ---------- Main Window ----------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        # Create a background label that will scale with the window
        self.background_label = QLabel(self)
        self.background_label.setScaledContents(True)
        self.background_label.setAlignment(Qt.AlignCenter)
        
        # Try to load the background image
        bg_path = "CPAP-Dash/Assets/bg.jpg"
        if os.path.exists(bg_path):
            pixmap = QPixmap(bg_path)
            self.background_label.setPixmap(pixmap)
        else:
            # Fallback to a solid color if image not found
            self.background_label.setStyleSheet("background-color: #cfd1e3;")
        
        # Set the background label to fill the entire window
        self.background_label.setGeometry(self.rect())
        
        self.title_bar = TitleBar(self)
        self.central_widget = CentralStackedWidget(self)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.title_bar)
        main_layout.addWidget(self.central_widget)

        container = QWidget()
        container.setLayout(main_layout)
        container.setAttribute(Qt.WA_TranslucentBackground)  # Make container transparent
        self.setCentralWidget(container)

        self.setWindowTitle("Device Registration System")
        self.resize(800, 600)
        self.setMinimumSize(700, 500)
        self.old_pos = None

    def resizeEvent(self, event):
        # Update background size when window is resized
        self.background_label.setGeometry(self.rect())
        super().resizeEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPos() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = None
            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())