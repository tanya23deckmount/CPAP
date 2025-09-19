import sys
import sqlite3
import datetime
import re
from uuid import uuid4
from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QFormLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QAbstractItemView, QScrollArea, QWidget, QCheckBox,QComboBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QBrush

# ----------------- Database Init -----------------
def init_db():
    try:
        conn = sqlite3.connect("user_data.db")
        cursor = conn.cursor()

        # Create table with id as TEXT
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                string_serial_number TEXT,
                report_uniq_id_uid TEXT,
                device_user_id TEXT,
                device_reading TEXT,
                start_date TEXT,
                end_date TEXT,
                mask TEXT,
                mask_type TEXT,
                start_hour_min TEXT,
                end_hour_min TEXT,
                timedifferenceinMinute TEXT,
                reading_dev_mode TEXT,
                mode_name TEXT,
                device_name TEXT,
                csa_count TEXT,
                osa_count TEXT,
                hsa_count TEXT,
                a_flex TEXT,
                a_flex_level TEXT,
                a_flex_value TEXT,
                leak TEXT,
                max_pressure TEXT,
                min_pressure TEXT,
                pressurechangecount TEXT,
                ratechangeFactor TEXT,
                final_date TEXT,
                date_time TEXT,
                old_or_new TEXT
            )
        ''')

        # Verify table schema
        cursor.execute("PRAGMA table_info(users)")
        cols = [c[1] for c in cursor.fetchall()]
        expected_cols = [
            'id', 'string_serial_number', 'report_uniq_id_uid', 'device_user_id', 'device_reading',
            'start_date', 'end_date', 'mask', 'mask_type', 'start_hour_min', 'end_hour_min',
            'timedifferenceinMinute', 'reading_dev_mode', 'mode_name', 'device_name',
            'csa_count', 'osa_count', 'hsa_count', 'a_flex', 'a_flex_level', 'a_flex_value',
            'leak', 'max_pressure', 'min_pressure', 'pressurechangecount', 'ratechangeFactor',
            'final_date', 'date_time', 'old_or_new'
        ]
        if set(cols) != set(expected_cols):
            print("Table schema incorrect. Recreating table.")
            cursor.execute("DROP TABLE IF EXISTS users")
            cursor.execute('''
                CREATE TABLE users (
                    id TEXT PRIMARY KEY,
                    string_serial_number TEXT,
                    report_uniq_id_uid TEXT,
                    device_user_id TEXT,
                    device_reading TEXT,
                    start_date TEXT,
                    end_date TEXT,
                    mask TEXT,
                    mask_type TEXT,
                    start_hour_min TEXT,
                    end_hour_min TEXT,
                    timedifferenceinMinute TEXT,
                    reading_dev_mode TEXT,
                    mode_name TEXT,
                    device_name TEXT,
                    csa_count TEXT,
                    osa_count TEXT,
                    hsa_count TEXT,
                    a_flex TEXT,
                    a_flex_level TEXT,
                    a_flex_value TEXT,
                    leak TEXT,
                    max_pressure TEXT,
                    min_pressure TEXT,
                    pressurechangecount TEXT,
                    ratechangeFactor TEXT,
                    final_date TEXT,
                    date_time TEXT,
                    old_or_new TEXT
                )
            ''')

        conn.commit()
    except Exception as e:
        print(f"Database initialization error: {str(e)}")
        raise
    finally:
        conn.close()

# Migrate existing data to new schema (if needed)
def migrate_db():
    try:
        conn = sqlite3.connect("user_data.db")
        cursor = conn.cursor()

        # Check if old table with INTEGER id exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if cursor.fetchone():
            cursor.execute("PRAGMA table_info(users)")
            cols = [c[1] for c in cursor.fetchall()]
            if 'id' in cols:
                cursor.execute("SELECT type FROM pragma_table_info('users') WHERE name='id'")
                id_type = cursor.fetchone()[0]
                if id_type == 'INTEGER':
                    # Create new table with id as TEXT
                    cursor.execute('''
                        CREATE TABLE users_new (
                            id TEXT PRIMARY KEY,
                            string_serial_number TEXT,
                            report_uniq_id_uid TEXT,
                            device_user_id TEXT,
                            device_reading TEXT,
                            start_date TEXT,
                            end_date TEXT,
                            mask TEXT,
                            mask_type TEXT,
                            start_hour_min TEXT,
                            end_hour_min TEXT,
                            timedifferenceinMinute TEXT,
                            reading_dev_mode TEXT,
                            mode_name TEXT,
                            device_name TEXT,
                            csa_count TEXT,
                            osa_count TEXT,
                            hsa_count TEXT,
                            a_flex TEXT,
                            a_flex_level TEXT,
                            a_flex_value TEXT,
                            leak TEXT,
                            max_pressure TEXT,
                            min_pressure TEXT,
                            pressurechangecount TEXT,
                            ratechangeFactor TEXT,
                            final_date TEXT,
                            date_time TEXT,
                            old_or_new TEXT
                        )
                    ''')

                    # Copy data, converting id to string
                    cursor.execute("SELECT * FROM users")
                    rows = cursor.fetchall()
                    for row in rows:
                        cursor.execute('''
                            INSERT INTO users_new (
                                id, string_serial_number, report_uniq_id_uid, device_user_id, device_reading,
                                start_date, end_date, mask, mask_type, start_hour_min, end_hour_min,
                                timedifferenceinMinute, reading_dev_mode, mode_name, device_name,
                                csa_count, osa_count, hsa_count, a_flex, a_flex_level, a_flex_value,
                                leak, max_pressure, min_pressure, pressurechangecount, ratechangeFactor,
                                final_date, date_time, old_or_new
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (str(row[0]),) + row[1:])

                    # Drop old table and rename new table
                    cursor.execute("DROP TABLE users")
                    cursor.execute("ALTER TABLE users_new RENAME TO users")
                    conn.commit()
                    print("Database migration completed: id converted to TEXT")
        conn.close()
    except Exception as e:
        print(f"Database migration error: {str(e)}")
        raise
    finally:
        conn.close()

# Call init and migration at program start
init_db()
migrate_db()

# ----------------- Add/Edit User Dialog -----------------
class UserDetailsDialog(QDialog):
    def __init__(self, parent=None, user_data=None, mode="add"):
        super().__init__(parent)
        self.user_data = user_data or {}
        self.mode = mode
        self.setWindowTitle("Add Device Record" if mode == "add" else "Edit Device Record")
        self.setMinimumWidth(500)
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(self.get_stylesheet())
        main_layout = QVBoxLayout()

        # Header
        header = QLabel("Add Device Record" if self.mode == "add" else "Edit Device Record")
        header.setObjectName("header")
        main_layout.addWidget(header)

        # Form inside a scroll area for many fields
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        form_widget = QWidget()
        form = QFormLayout()

        # Input fields with descriptive labels
        self.string_serial_number = QLineEdit()
        self.string_serial_number.setPlaceholderText("e.g., SN123456")
        self.report_uniq_id_uid = QLineEdit()
        self.report_uniq_id_uid.setPlaceholderText("e.g., UID789")
        self.device_user_id = QLineEdit()
        self.device_user_id.setPlaceholderText("e.g., USER001")
        self.device_reading = QLineEdit()
        self.device_reading.setPlaceholderText("e.g., 123.45")
        self.start_date = QLineEdit()
        self.start_date.setPlaceholderText("DD/MM/YYYY")
        self.end_date = QLineEdit()
        self.end_date.setPlaceholderText("DD/MM/YYYY")
        self.mask = QLineEdit()
        self.mask.setPlaceholderText("e.g., Full Face")
        self.mask_type = QLineEdit()
        self.mask_type.setPlaceholderText("e.g., Nasal")
        self.start_hour_min = QLineEdit()
        self.start_hour_min.setPlaceholderText("HH:MM")
        self.end_hour_min = QLineEdit()
        self.end_hour_min.setPlaceholderText("HH:MM")
        self.timedifferenceinMinute = QLineEdit()
        self.timedifferenceinMinute.setPlaceholderText("e.g., 480")
        self.reading_dev_mode = QLineEdit()
        self.reading_dev_mode.setPlaceholderText("e.g., Auto")
        self.mode_name = QLineEdit()
        self.mode_name.setPlaceholderText("e.g., CPAP")
        self.device_name = QLineEdit()
        self.device_name.setPlaceholderText("e.g., ResMed AirSense")
        self.csa_count = QLineEdit()
        self.csa_count.setPlaceholderText("e.g., 5")
        self.osa_count = QLineEdit()
        self.osa_count.setPlaceholderText("e.g., 10")
        self.hsa_count = QLineEdit()
        self.hsa_count.setPlaceholderText("e.g., 2")
        self.a_flex = QLineEdit()
        self.a_flex.setPlaceholderText("e.g., Enabled")
        self.a_flex_level = QLineEdit()
        self.a_flex_level.setPlaceholderText("e.g., 3")
        self.a_flex_value = QLineEdit()
        self.a_flex_value.setPlaceholderText("e.g., 1.5")
        self.leak = QLineEdit()
        self.leak.setPlaceholderText("e.g., 24 L/min")
        self.max_pressure = QLineEdit()
        self.max_pressure.setPlaceholderText("e.g., 20 cmH2O")
        self.min_pressure = QLineEdit()
        self.min_pressure.setPlaceholderText("e.g., 4 cmH2O")
        self.pressurechangecount = QLineEdit()
        self.pressurechangecount.setPlaceholderText("e.g., 15")
        self.ratechangeFactor = QLineEdit()
        self.ratechangeFactor.setPlaceholderText("e.g., 0.5")
        self.final_date = QLineEdit()
        self.final_date.setPlaceholderText("DD/MM/YYYY")
        self.date_time = QLineEdit()
        self.date_time.setPlaceholderText("DD/MM/YYYY HH:MM")
        self.old_or_new = QLineEdit()
        self.old_or_new.setPlaceholderText("e.g., New")

        # Add fields to form with clear labels
        form.addRow("Serial Number:", self.string_serial_number)
        form.addRow("Report Unique ID:", self.report_uniq_id_uid)
        form.addRow("Device User ID:", self.device_user_id)
        form.addRow("Device Reading:", self.device_reading)
        form.addRow("Start Date:", self.start_date)
        form.addRow("End Date:", self.end_date)
        form.addRow("Mask:", self.mask)
        form.addRow("Mask Type:", self.mask_type)
        form.addRow("Start Time (HH:MM):", self.start_hour_min)
        form.addRow("End Time (HH:MM):", self.end_hour_min)
        form.addRow("Time Difference (min):", self.timedifferenceinMinute)
        form.addRow("Device Mode:", self.reading_dev_mode)
        form.addRow("Mode Name:", self.mode_name)
        form.addRow("Device Name:", self.device_name)
        form.addRow("CSA Count:", self.csa_count)
        form.addRow("OSA Count:", self.osa_count)
        form.addRow("HSA Count:", self.hsa_count)
        form.addRow("A-Flex:", self.a_flex)
        form.addRow("A-Flex Level:", self.a_flex_level)
        form.addRow("A-Flex Value:", self.a_flex_value)
        form.addRow("Leak (L/min):", self.leak)
        form.addRow("Max Pressure (cmH2O):", self.max_pressure)
        form.addRow("Min Pressure (cmH2O):", self.min_pressure)
        form.addRow("Pressure Change Count:", self.pressurechangecount)
        form.addRow("Rate Change Factor:", self.ratechangeFactor)
        form.addRow("Final Date:", self.final_date)
        form.addRow("Date & Time:", self.date_time)
        form.addRow("Old/New:", self.old_or_new)

        form_widget.setLayout(form)
        scroll.setWidget(form_widget)
        main_layout.addWidget(scroll)

        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("💾 Save")
        cancel_btn = QPushButton("❌ Cancel")
        save_btn.clicked.connect(self.save_data)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

        # Load data if editing
        if self.mode == "edit" and self.user_data:
            self.load_user_data()

    def load_user_data(self):
        self.string_serial_number.setText(self.user_data.get('string_serial_number', ''))
        self.report_uniq_id_uid.setText(self.user_data.get('report_uniq_id_uid', ''))
        self.device_user_id.setText(self.user_data.get('device_user_id', ''))
        self.device_reading.setText(self.user_data.get('device_reading', ''))
        self.start_date.setText(self.user_data.get('start_date', ''))
        self.end_date.setText(self.user_data.get('end_date', ''))
        self.mask.setText(self.user_data.get('mask', ''))
        self.mask_type.setText(self.user_data.get('mask_type', ''))
        self.start_hour_min.setText(self.user_data.get('start_hour_min', ''))
        self.end_hour_min.setText(self.user_data.get('end_hour_min', ''))
        self.timedifferenceinMinute.setText(self.user_data.get('timedifferenceinMinute', ''))
        self.reading_dev_mode.setText(self.user_data.get('reading_dev_mode', ''))
        self.mode_name.setText(self.user_data.get('mode_name', ''))
        self.device_name.setText(self.user_data.get('device_name', ''))
        self.csa_count.setText(self.user_data.get('csa_count', ''))
        self.osa_count.setText(self.user_data.get('osa_count', ''))
        self.hsa_count.setText(self.user_data.get('hsa_count', ''))
        self.a_flex.setText(self.user_data.get('a_flex', ''))
        self.a_flex_level.setText(self.user_data.get('a_flex_level', ''))
        self.a_flex_value.setText(self.user_data.get('a_flex_value', ''))
        self.leak.setText(self.user_data.get('leak', ''))
        self.max_pressure.setText(self.user_data.get('max_pressure', ''))
        self.min_pressure.setText(self.user_data.get('min_pressure', ''))
        self.pressurechangecount.setText(self.user_data.get('pressurechangecount', ''))
        self.ratechangeFactor.setText(self.user_data.get('ratechangeFactor', ''))
        self.final_date.setText(self.user_data.get('final_date', ''))
        self.date_time.setText(self.user_data.get('date_time', ''))
        self.old_or_new.setText(self.user_data.get('old_or_new', ''))

    def validate_date(self, date_str):
        """Validate date format DD/MM/YYYY"""
        pattern = r'^\d{2}/\d{2}/\d{4}$'
        if not re.match(pattern, date_str):
            return False
        try:
            day, month, year = map(int, date_str.split('/'))
            datetime.datetime(year, month, day)
            return True
        except ValueError:
            return False

    def validate_datetime(self, datetime_str):
        """Validate datetime format DD/MM/YYYY HH:MM"""
        pattern = r'^\d{2}/\d{2}/\d{4} \d{2}:\d{2}$'
        if not re.match(pattern, datetime_str):
            return False
        try:
            day, month, year_time = datetime_str.split('/')
            year, time = year_time.split(' ')
            hour, minute = map(int, time.split(':'))
            datetime.datetime(int(year), int(month), int(day), hour, minute)
            return True
        except ValueError:
            return False

    def validate_time(self, time_str):
        """Validate time format HH:MM"""
        pattern = r'^\d{2}:\d{2}$'
        if not re.match(pattern, time_str):
            return False
        try:
            hour, minute = map(int, time_str.split(':'))
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                return True
            return False
        except ValueError:
            return False

    def get_user_data(self):
        return {
            'string_serial_number': self.string_serial_number.text(),
            'report_uniq_id_uid': self.report_uniq_id_uid.text(),
            'device_user_id': self.device_user_id.text(),
            'device_reading': self.device_reading.text(),
            'start_date': self.start_date.text(),
            'end_date': self.end_date.text(),
            'mask': self.mask.text(),
            'mask_type': self.mask_type.text(),
            'start_hour_min': self.start_hour_min.text(),
            'end_hour_min': self.end_hour_min.text(),
            'timedifferenceinMinute': self.timedifferenceinMinute.text(),
            'reading_dev_mode': self.reading_dev_mode.text(),
            'mode_name': self.mode_name.text(),
            'device_name': self.device_name.text(),
            'csa_count': self.csa_count.text(),
            'osa_count': self.osa_count.text(),
            'hsa_count': self.hsa_count.text(),
            'a_flex': self.a_flex.text(),
            'a_flex_level': self.a_flex_level.text(),
            'a_flex_value': self.a_flex_value.text(),
            'leak': self.leak.text(),
            'max_pressure': self.max_pressure.text(),
            'min_pressure': self.min_pressure.text(),
            'pressurechangecount': self.pressurechangecount.text(),
            'ratechangeFactor': self.ratechangeFactor.text(),
            'final_date': self.final_date.text(),
            'date_time': self.date_time.text(),
            'old_or_new': self.old_or_new.text()
        }

    def save_data(self):
        user_data = self.get_user_data()

        # Validate required fields
        if not user_data['start_date'] or not self.validate_date(user_data['start_date']):
            QMessageBox.warning(self, "Warning", "Valid Start Date (DD/MM/YYYY) is required.")
            return
        if user_data['end_date'] and not self.validate_date(user_data['end_date']):
            QMessageBox.warning(self, "Warning", "Valid End Date (DD/MM/YYYY) is required.")
            return
        if user_data['start_hour_min'] and not self.validate_time(user_data['start_hour_min']):
            QMessageBox.warning(self, "Warning", "Valid Start Time (HH:MM) is required.")
            return
        if user_data['end_hour_min'] and not self.validate_time(user_data['end_hour_min']):
            QMessageBox.warning(self, "Warning", "Valid End Time (HH:MM) is required.")
            return
        if user_data['final_date'] and not self.validate_date(user_data['final_date']):
            QMessageBox.warning(self, "Warning", "Valid Final Date (DD/MM/YYYY) is required.")
            return
        if user_data['date_time'] and not self.validate_datetime(user_data['date_time']):
            QMessageBox.warning(self, "Warning", "Valid Date & Time (DD/MM/YYYY HH:MM) is required.")
            return

        try:
            conn = sqlite3.connect("user_data.db")
            cursor = conn.cursor()

            # Verify table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            if not cursor.fetchone():
                raise Exception("Table 'users' does not exist.")

            if self.mode == "add":
                # Generate a unique string ID
                user_id = str(uuid4())
                cursor.execute('''
                    INSERT INTO users (
                        id, string_serial_number, report_uniq_id_uid, device_user_id, device_reading,
                        start_date, end_date, mask, mask_type, start_hour_min, end_hour_min,
                        timedifferenceinMinute, reading_dev_mode, mode_name, device_name,
                        csa_count, osa_count, hsa_count, a_flex, a_flex_level, a_flex_value,
                        leak, max_pressure, min_pressure, pressurechangecount, ratechangeFactor,
                        final_date, date_time, old_or_new
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id,
                    user_data['string_serial_number'], user_data['report_uniq_id_uid'],
                    user_data['device_user_id'], user_data['device_reading'],
                    user_data['start_date'], user_data['end_date'], user_data['mask'],
                    user_data['mask_type'], user_data['start_hour_min'], user_data['end_hour_min'],
                    user_data['timedifferenceinMinute'], user_data['reading_dev_mode'],
                    user_data['mode_name'], user_data['device_name'], user_data['csa_count'],
                    user_data['osa_count'], user_data['hsa_count'], user_data['a_flex'],
                    user_data['a_flex_level'], user_data['a_flex_value'], user_data['leak'],
                    user_data['max_pressure'], user_data['min_pressure'],
                    user_data['pressurechangecount'], user_data['ratechangeFactor'],
                    user_data['final_date'], user_data['date_time'], user_data['old_or_new']
                ))
            else:
                cursor.execute('''
                    UPDATE users SET
                        string_serial_number=?, report_uniq_id_uid=?, device_user_id=?,
                        device_reading=?, start_date=?, end_date=?, mask=?, mask_type=?,
                        start_hour_min=?, end_hour_min=?, timedifferenceinMinute=?,
                        reading_dev_mode=?, mode_name=?, device_name=?, csa_count=?,
                        osa_count=?, hsa_count=?, a_flex=?, a_flex_level=?, a_flex_value=?,
                        leak=?, max_pressure=?, min_pressure=?, pressurechangecount=?,
                        ratechangeFactor=?, final_date=?, date_time=?, old_or_new=?
                    WHERE id=?
                ''', (
                    user_data['string_serial_number'], user_data['report_uniq_id_uid'],
                    user_data['device_user_id'], user_data['device_reading'],
                    user_data['start_date'], user_data['end_date'], user_data['mask'],
                    user_data['mask_type'], user_data['start_hour_min'], user_data['end_hour_min'],
                    user_data['timedifferenceinMinute'], user_data['reading_dev_mode'],
                    user_data['mode_name'], user_data['device_name'], user_data['csa_count'],
                    user_data['osa_count'], user_data['hsa_count'], user_data['a_flex'],
                    user_data['a_flex_level'], user_data['a_flex_value'], user_data['leak'],
                    user_data['max_pressure'], user_data['min_pressure'],
                    user_data['pressurechangecount'], user_data['ratechangeFactor'],
                    user_data['final_date'], user_data['date_time'], user_data['old_or_new'],
                    self.user_data['id']
                ))

            conn.commit()
            QMessageBox.information(self, "Success", "Device record saved successfully.")
            self.accept()

            # Refresh parent table if exists
            if self.parent() and hasattr(self.parent(), "refresh_table"):
                self.parent().refresh_table()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save data: {str(e)}")
        finally:
            conn.close()

    def get_stylesheet(self):
        return """
            QDialog {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #e6f0fa, stop:1 #ffffff
                );
                border-radius: 15px;
                padding: 10px;
            }
            #header {
                font-size: 24px;
                font-weight: bold;
                color: #1e3a8a;
                margin-bottom: 20px;
                text-align: center;
            }
            QLabel {
                font-size: 14px;
                font-weight: 600;
                color: #1e3a8a;
                padding: 5px;
            }
            QLineEdit {
                padding: 10px;
                border: 1px solid #93c5fd;
                border-radius: 8px;
                font-size: 14px;
                background: #ffffff;
                selection-background-color: #3b82f6;
            }
            QLineEdit:focus {
                border: 2px solid #3b82f6;
                background: #f8fbff;
            }
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollArea QWidget {
                background: transparent;
            }
            QPushButton {
                padding: 12px 20px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 15px;
                border: none;
                transition: all 0.3s;
            }
            QPushButton:hover {
                transform: scale(1.05);
            }
            QPushButton:pressed {
                transform: scale(0.95);
            }
            QPushButton[text*="💾"] {
                background-color: #22c55e;
                color: white;
            }
            QPushButton[text*="💾"]:hover {
                background-color: #16a34a;
                box-shadow: 0px 4px 12px rgba(34,197,94,0.4);
            }
            QPushButton[text*="❌"] {
                background-color: #ef4444;
                color: white;
            }
            QPushButton[text*="❌"]:hover {
                background-color: #dc2626;
                box-shadow: 0px 4px 12px rgba(239,68,68,0.4);
            }
        """

# ----------------- Column Selector Dialog -----------------
class ColumnSelectorDialog(QDialog):
    def __init__(self, parent=None, current_visible=None):
        super().__init__(parent)
        self.setWindowTitle("Select Columns to Display")
        self.setMinimumWidth(400)
        self.current_visible = current_visible or set(range(1, 29))
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(self.get_stylesheet())
        main_layout = QVBoxLayout()

        # Header
        header = QLabel("Select Columns to Display")
        header.setObjectName("header")
        main_layout.addWidget(header)

        # Scroll area for checkboxes
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        widget = QWidget()
        vbox = QVBoxLayout()

        # Column labels (excluding ID and Action)
        column_labels = [
            "Serial Number", "Report UID", "User ID", "Device Reading",
            "Start Date", "End Date", "Mask", "Mask Type", "Start Time",
            "End Time", "Time Diff (min)", "Device Mode", "Mode Name", "Device Name",
            "CSA Count", "OSA Count", "HSA Count", "A-Flex", "A-Flex Level",
            "A-Flex Value", "Leak", "Max Pressure", "Min Pressure", "Pressure Changes",
            "Rate Change Factor", "Final Date", "Date & Time", "Old/New"
        ]

        self.checkboxes = {}
        for idx, label in enumerate(column_labels, start=1):
            cb = QCheckBox(label)
            cb.setChecked(idx in self.current_visible)
            self.checkboxes[idx] = cb
            vbox.addWidget(cb)

        widget.setLayout(vbox)
        scroll.setWidget(widget)
        main_layout.addWidget(scroll)

        # Buttons
        btn_layout = QHBoxLayout()
        apply_btn = QPushButton("Apply")
        select_all_btn = QPushButton("Select All")
        deselect_all_btn = QPushButton("Deselect All")
        cancel_btn = QPushButton("Cancel")
        apply_btn.clicked.connect(self.accept)
        select_all_btn.clicked.connect(self.select_all)
        deselect_all_btn.clicked.connect(self.deselect_all)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(select_all_btn)
        btn_layout.addWidget(deselect_all_btn)
        btn_layout.addWidget(apply_btn)
        btn_layout.addWidget(cancel_btn)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

    def select_all(self):
        for cb in self.checkboxes.values():
            cb.setChecked(True)

    def deselect_all(self):
        for cb in self.checkboxes.values():
            cb.setChecked(False)

    def get_selected_columns(self):
        return {idx for idx, cb in self.checkboxes.items() if cb.isChecked()}

    def get_stylesheet(self):
        return """
            QDialog {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #edf2fb, stop:1 #ffffff
                );
                border-radius: 18px;
                padding: 15px;
            }
            #header {
                font-size: 26px;
                font-weight: 800;
                color: #1e3a8a;
                margin-bottom: 20px;
                text-align: center;
                letter-spacing: 0.5px;
            }
            QCheckBox {
                font-size: 15px;
                color: #1e293b;
                padding: 6px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid #3b82f6;
                background: #ffffff;
            }
            QCheckBox::indicator:checked {
                background: #3b82f6;
                image: url(:/qt-project.org/styles/commonstyle/images/checkboxindicator.png);
            }
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollArea QWidget {
                background: transparent;
            }
            QPushButton {
                padding: 12px 22px;
                border-radius: 12px;
                font-weight: bold;
                font-size: 15px;
                border: none;
                transition: all 0.25s ease;
            }
            QPushButton:hover {
                transform: scale(1.05);
            }
            QPushButton:pressed {
                transform: scale(0.95);
            }
            QPushButton[text="Apply"] {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                            stop:0 #60a5fa, stop:1 #2563eb);
                color: white;
                box-shadow: 0px 4px 10px rgba(37,99,235,0.35);
            }
            QPushButton[text="Apply"]:hover {
                background: #1d4ed8;
            }
            QPushButton[text="Select All"] {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                            stop:0 #4ade80, stop:1 #16a34a);
                color: white;
                box-shadow: 0px 4px 10px rgba(34,197,94,0.35);
            }
            QPushButton[text="Select All"]:hover {
                background: #15803d;
            }
            QPushButton[text="Deselect All"] {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                            stop:0 #fbbf24, stop:1 #d97706);
                color: white;
                box-shadow: 0px 4px 10px rgba(245,158,11,0.35);
            }
            QPushButton[text="Deselect All"]:hover {
                background: #b45309;
            }
            QPushButton[text="Cancel"] {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                            stop:0 #f87171, stop:1 #dc2626);
                color: white;
                box-shadow: 0px 4px 10px rgba(239,68,68,0.35);
            }
            QPushButton[text="Cancel"]:hover {
                background: #b91c1c;
            }
        """

# ----------------- View User Dialog -----------------
class ViewUserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Device Records")
        self.setMinimumSize(1100, 800)
        self.selected_row = -1
        self.filters = {}  # Store active filters
        self.visible_columns = set(range(1, 29))  # Columns 1 to 28 are data columns
        self.init_ui()

    # def init_ui(self):
    #     self.setStyleSheet(self.get_stylesheet())
    #     main_layout = QVBoxLayout()

    #     header_layout = QHBoxLayout()
    #     header = QLabel("Device Records")
    #     header.setObjectName("header")
        
    #     add_btn = QPushButton("Add New")       
    #     columns_btn = QPushButton("Select Columns")
        
    #     add_btn.clicked.connect(self.add_user)        
    #     columns_btn.clicked.connect(self.open_column_selector)
    #     header_layout.addWidget(header)
    #     header_layout.addStretch()
    #     header_layout.addWidget(add_btn)
      
    #     header_layout.addWidget(columns_btn)
    #     main_layout.addLayout(header_layout)

    #     search_layout = QHBoxLayout()
    #     from_label = QLabel("From Date:")
    #     self.from_date = QLineEdit()
    #     self.from_date.setPlaceholderText("DD/MM/YYYY")
    #     to_label = QLabel("To Date:")
    #     self.to_date = QLineEdit()
    #     self.to_date.setPlaceholderText("DD/MM/YYYY")
    #     search_btn = QPushButton("🔍 Search")
    #     clear_btn = QPushButton("Clear")
    #     search_btn.clicked.connect(self.search_records)
    #     clear_btn.clicked.connect(self.clear_search)
    #     search_layout.addWidget(from_label)
    #     search_layout.addWidget(self.from_date)
    #     search_layout.addWidget(to_label)
    #     search_layout.addWidget(self.to_date)
    #     search_layout.addWidget(search_btn)
    #     search_layout.addWidget(clear_btn)
    #     main_layout.addLayout(search_layout)

    #     self.table = QTableWidget()
    #     self.table.setColumnCount(30)  # Updated for new fields + action
    #     self.table.setHorizontalHeaderLabels([
    #         "ID", "Serial Number", "Report UID", "User ID", "Device Reading",
    #         "Start Date", "End Date", "Mask", "Mask Type", "Start Time",
    #         "End Time", "Time Diff (min)", "Device Mode", "Mode Name", "Device Name",
    #         "CSA Count", "OSA Count", "HSA Count", "A-Flex", "A-Flex Level",
    #         "A-Flex Value", "Leak", "Max Pressure", "Min Pressure", "Pressure Changes",
    #         "Rate Change Factor", "Final Date", "Date & Time", "Old/New", "Action"
    #     ])
    #     self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
    #     self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
    #     self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    #     self.table.verticalHeader().setVisible(False)
    #     self.table.setAlternatingRowColors(True)
    #     self.table.cellClicked.connect(self.on_cell_clicked)
    #     self.table.cellDoubleClicked.connect(self.on_double_click)
    #     self.table.setColumnHidden(0, True)
    #     main_layout.addWidget(self.table)
    #     self.setLayout(main_layout)

    def init_ui(self):
        self.setStyleSheet(self.get_stylesheet())
        main_layout = QVBoxLayout()
    
        header_layout = QHBoxLayout()
        header = QLabel("Device Records")
        header.setObjectName("header")
        
        add_btn = QPushButton("Add New")       
        columns_btn = QPushButton("Select Columns")
        
        add_btn.clicked.connect(self.add_user)        
        columns_btn.clicked.connect(self.open_column_selector)
        header_layout.addWidget(header)
        header_layout.addStretch()
        header_layout.addWidget(add_btn)
      
        header_layout.addWidget(columns_btn)
        main_layout.addLayout(header_layout)
    
        search_layout = QHBoxLayout()
        from_label = QLabel("From Date:")
        self.from_date = QLineEdit()
        self.from_date.setPlaceholderText("DD/MM/YYYY")
        to_label = QLabel("To Date:")
        self.to_date = QLineEdit()
        self.to_date.setPlaceholderText("DD/MM/YYYY")
        
        # Add CPAP Type selection
        cpap_type_label = QLabel("CPAP Type:")
        self.cpap_type_combo = QComboBox()
        self.cpap_type_combo.addItems(["CPAP", "Auto CPAP"])
        self.cpap_type_combo.setCurrentText("All")
        
        search_btn = QPushButton("🔍 Search")
        clear_btn = QPushButton("Clear")
        search_btn.clicked.connect(self.search_records)
        clear_btn.clicked.connect(self.clear_search)
        
        search_layout.addWidget(from_label)
        search_layout.addWidget(self.from_date)
        search_layout.addWidget(to_label)
        search_layout.addWidget(self.to_date)
        search_layout.addWidget(cpap_type_label)
        search_layout.addWidget(self.cpap_type_combo)
        search_layout.addWidget(search_btn)
        search_layout.addWidget(clear_btn)
        main_layout.addLayout(search_layout)
    
        self.table = QTableWidget()
        self.table.setColumnCount(30)  # Updated for new fields + action
        self.table.setHorizontalHeaderLabels([
            "ID", "Serial Number", "Report UID", "User ID", "Device Reading",
            "Start Date", "End Date", "Mask", "Mask Type", "Start Time",
            "End Time", "Time Diff (min)", "Device Mode", "Mode Name", "Device Name",
            "CSA Count", "OSA Count", "HSA Count", "A-Flex", "A-Flex Level",
            "A-Flex Value", "Leak", "Max Pressure", "Min Pressure", "Pressure Changes",
            "Rate Change Factor", "Final Date", "Date & Time", "Old/New", "Action"
        ])
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.cellClicked.connect(self.on_cell_clicked)
        self.table.cellDoubleClicked.connect(self.on_double_click)
        self.table.setColumnHidden(0, True)
        main_layout.addWidget(self.table)
        self.setLayout(main_layout)
    
    def showEvent(self, event):
        self.refresh_table()
        super().showEvent(event)

    def get_data_as_array(self):
        try:
            conn = sqlite3.connect("user_data.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
            rows = cursor.fetchall()
            conn.close()
            # Convert to list of lists, ensuring all values are strings
            return [[str(value) for value in row] for row in rows]
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load data: {str(e)}")
            return []


    def open_column_selector(self):
        dialog = ColumnSelectorDialog(self, self.visible_columns)
        if dialog.exec_() == QDialog.Accepted:
            self.visible_columns = dialog.get_selected_columns()
            self.refresh_table()

    def refresh_table(self):
        data_array = self.get_data_as_array()
        fields = [
            "id", "string_serial_number", "report_uniq_id_uid", "device_user_id", "device_reading",
            "start_date", "end_date", "mask", "mask_type", "start_hour_min", "end_hour_min",
            "timedifferenceinMinute", "reading_dev_mode", "mode_name", "device_name",
            "csa_count", "osa_count", "hsa_count", "a_flex", "a_flex_level", "a_flex_value",
            "leak", "max_pressure", "min_pressure", "pressurechangecount", "ratechangeFactor",
            "final_date", "date_time", "old_or_new"
        ]

        # Apply filters
        filtered_array = []
        for row in data_array:
            row_dict = dict(zip(fields, row))
            include = True
            for field, filter_value in self.filters.items():
                if filter_value:
                    if field in row_dict and filter_value.lower() not in str(row_dict[field]).lower():
                        include = False
                        break
            if include:
                filtered_array.append(row)

        def parse_date_for_sort(date_str):
            try:
                day, mon, year = map(int, date_str.split('/'))
                return datetime.date(year, mon, day)
            except:
                return datetime.date(1900, 1, 1)

        filtered_array = sorted(filtered_array, key=lambda row: parse_date_for_sort(row[5] if row[5] else row[26]), reverse=True)

        self.table.setRowCount(len(filtered_array))
        for r, row in enumerate(filtered_array):
            for c, value in enumerate(row):
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(r, c, item)

            delete_btn = QPushButton("🗑️")
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ef4444;
                    color: white;
                    border: none;
                    padding: 5px;
                    border-radius: 10px;
                }
                QPushButton:hover {
                    background-color: #dc2626;
                }
            """)
            delete_btn.clicked.connect(lambda _, row=r: self.delete_user(row))
            self.table.setCellWidget(r, 29, delete_btn)

        self.table.horizontalHeader().setSectionResizeMode(29, QHeaderView.ResizeToContents)

        # Apply column visibility
        for col in range(1, 29):
            self.table.setColumnHidden(col, col not in self.visible_columns)

    def search_records(self):
        from_date_str = self.from_date.text().strip()
        to_date_str = self.to_date.text().strip()

        if not from_date_str and not to_date_str:
            self.refresh_table()
            return

        if from_date_str and not to_date_str:
            to_date_str = from_date_str
        elif not from_date_str and to_date_str:
            from_date_str = to_date_str

        def parse_date(d):
            try:
                day, mon, year = map(int, d.split('/'))
                return datetime.date(year, mon, day)
            except:
                return None

        from_d = parse_date(from_date_str)
        to_d = parse_date(to_date_str)

        if from_d is None or to_d is None:
            self.refresh_table()
            return

        if from_d > to_d:
            self.refresh_table()
            return

        data_array = self.get_data_as_array()
        fields = [
            "id", "string_serial_number", "report_uniq_id_uid", "device_user_id", "device_reading",
            "start_date", "end_date", "mask", "mask_type", "start_hour_min", "end_hour_min",
            "timedifferenceinMinute", "reading_dev_mode", "mode_name", "device_name",
            "csa_count", "osa_count", "hsa_count", "a_flex", "a_flex_level", "a_flex_value",
            "leak", "max_pressure", "min_pressure", "pressurechangecount", "ratechangeFactor",
            "final_date", "date_time", "old_or_new"
        ]

        def parse_date_for_sort(date_str):
            try:
                day, mon, year = map(int, date_str.split('/'))
                return datetime.date(year, mon, day)
            except:
                return datetime.date(1900, 1, 1)

        filtered_array = []
        for row in data_array:
            row_dict = dict(zip(fields, row))
            date_str = row_dict['start_date'] or row_dict['final_date']
            d = parse_date(date_str)
            if d is None:
                continue
            if from_d <= d <= to_d:
                # Apply additional column filters
                include = True
                for field, filter_value in self.filters.items():
                    if filter_value:
                        if field in row_dict and filter_value.lower() not in str(row_dict[field]).lower():
                            include = False
                            break
                if include:
                    filtered_array.append(row)

        filtered_array = sorted(filtered_array, key=lambda row: parse_date_for_sort(row[5] if row[5] else row[26]), reverse=True)

        self.table.setRowCount(len(filtered_array))
        for r, row in enumerate(filtered_array):
            for c, value in enumerate(row):
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(r, c, item)

            delete_btn = QPushButton("🗑️")
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ef4444;
                    color: white;
                    border: none;
                    padding: 5px;
                    border-radius: 10px;
                }
                QPushButton:hover {
                    background-color: #dc2626;
                }
            """)
            delete_btn.clicked.connect(lambda _, row=r: self.delete_user(row))
            self.table.setCellWidget(r, 29, delete_btn)

        # Apply column visibility
        for col in range(1, 29):
            self.table.setColumnHidden(col, col not in self.visible_columns)

    def clear_search(self):
        self.from_date.clear()
        self.to_date.clear()
        self.filters = {}
        self.refresh_table()

    def on_cell_clicked(self, row, col):
        if col == 29:
            return
        self.selected_row = row
        for r in range(self.table.rowCount()):
            for c in range(self.table.columnCount()):
                item = self.table.item(r, c)
                if item:
                    if r == row:
                        item.setBackground(QBrush(QColor("#dbeafe")))
                    else:
                        item.setBackground(QBrush(QColor("white")))

    def on_double_click(self, row, col):
        if col == 29:
            return
        self.edit_user(row)

    def add_user(self):
        dialog = UserDetailsDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_table()

    def edit_user(self, row):
        fields = [
            "id", "string_serial_number", "report_uniq_id_uid", "device_user_id", "device_reading",
            "start_date", "end_date", "mask", "mask_type", "start_hour_min", "end_hour_min",
            "timedifferenceinMinute", "reading_dev_mode", "mode_name", "device_name",
            "csa_count", "osa_count", "hsa_count", "a_flex", "a_flex_level", "a_flex_value",
            "leak", "max_pressure", "min_pressure", "pressurechangecount", "ratechangeFactor",
            "final_date", "date_time", "old_or_new"
        ]
        user_data = {}
        for col in range(len(fields)):
            item = self.table.item(row, col)
            if item:
                user_data[fields[col]] = item.text()

        dialog = UserDetailsDialog(self, user_data, "edit")
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_table()

    def delete_user(self, row):
        id_item = self.table.item(row, 0)
        if not id_item:
            return

        user_id = id_item.text()
        reply = QMessageBox.question(self, 'Confirm Delete',
                                    'Are you sure you want to delete this record?',
                                    QMessageBox.Yes | QMessageBox.No,
                                    QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                conn = sqlite3.connect("user_data.db")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
                conn.commit()
                conn.close()
                QMessageBox.information(self, "Success", "Record deleted successfully.")
                self.refresh_table()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete record: {str(e)}")

    def get_stylesheet(self):
        return """
            QDialog {
                background: #f8fafc;
            }
            #header {
                font-size: 26px;
                font-weight: bold;
                color: #1e3a8a;
                margin-bottom: 15px;
            }
            QTableWidget {
                border: 1px solid #bfdbfe;
                border-radius: 8px;
                background: white;
                alternate-background-color: #eff6ff;
                gridline-color: #bfdbfe;
            }
            QHeaderView::section {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #6B3F69, stop:1 #3b82f6
                );
                color: white;
                padding: 8px;
                font-weight: bold;
                border: none;
                border-bottom: 1px solid #bfdbfe;
            }
            QTableWidget::item:selected {
                background: #A376A2;
                color: white;
            }
            QTableWidget::item:hover {
                background: #c385ed;
            }
            QPushButton {
                padding: 10px 18px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 15px;
                border: none;
                color: white;
                transition: all 0.3s;
            }
            QPushButton[text="Add New"] {
                background-color: #4CAF50;
            }
            QPushButton[text="Add New"]:hover {
                background-color: #45a049;
                box-shadow: 0px 2px 8px rgba(76,175,80,0.3);
            }
            QPushButton[text="Add New"]:pressed {
                background-color: #3d8b40;
            }
            QPushButton[text="Filter"] {
                background-color: #26A69A;
            }
            QPushButton[text="Filter"]:hover {
                background-color: #2c7a7b;
                box-shadow: 0px 2px 8px rgba(38,166,154,0.3);
            }
            QPushButton[text="Filter"]:pressed {
                background-color: #285e61;
            }
            QPushButton[text="Select Columns"] {
                background-color: #2196F3;
            }
            QPushButton[text="Select Columns"]:hover {
                background-color: #1e88e5;
                box-shadow: 0px 2px 8px rgba(33,150,243,0.3);
            }
            QPushButton[text="Select Columns"]:pressed {
                background-color: #1976d2;
            }
            QPushButton[text*="🔍"] {
                background-color: #3F51B5;
            }
            QPushButton[text*="🔍"]:hover {
                background-color: #3949ab;
                box-shadow: 0px 2px 8px rgba(63,81,181,0.3);
            }
            QPushButton[text*="🔍"]:pressed {
                background-color: #303f9f;
            }
            QPushButton[text="Clear"] {
                background-color: #F44336;
            }
            QPushButton[text="Clear"]:hover {
                background-color: #e53935;
                box-shadow: 0px 2px 8px rgba(244,67,54,0.3);
            }
            QPushButton[text="Clear"]:pressed {
                background-color: #d32f2f;
            }
            QLabel {
                color: #1e3a8a;
                font-weight: 600;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #93c5fd;
                border-radius: 6px;
                background: white;
            }
            QLineEdit:focus {
                border: 2px solid #3b82f6;
            }
        """

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dlg = ViewUserDialog()
    dlg.show()
    sys.exit(app.exec_())