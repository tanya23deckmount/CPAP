from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QMessageBox, QSlider, 
                             QSpinBox, QComboBox, QGroupBox, QScrollArea)
from PyQt5.QtCore import Qt
import json
import os


class SettingsPage(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.settings_file = 'cpap_settings.json'
        self.current_settings = self.load_settings()
        
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create sidebar
        from Cpap_dash import SideBar
        self.sidebar = SideBar()
        main_layout.addWidget(self.sidebar)
        
        # Content area
        content_widget = QWidget()
        content_widget.setStyleSheet("""
            QWidget {
                background-color: #f8fafc;
            }
        """)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header_layout = QHBoxLayout()
        
        # Title
        title_label = QLabel("CPAP Settings")
        title_label.setStyleSheet("""
            font-size: 26px;
            font-weight: bold;
            color: #1e293b;
        """)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Save button
        self.save_button = QPushButton("Save Changes")
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                padding: 10px 24px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QPushButton:pressed {
                background-color: #1d4ed8;
            }
        """)
        self.save_button.clicked.connect(self.save_settings)
        header_layout.addWidget(self.save_button)
        
        content_layout.addLayout(header_layout)
        content_layout.addSpacing(20)
        
        # Create scroll area for settings
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        # Settings container
        settings_container = QWidget()
        settings_layout = QVBoxLayout(settings_container)
        settings_layout.setSpacing(20)
        
        # GroupBox CSS (reusable)
        groupbox_css = """
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #e2e8f0;
                border-radius: 10px;
                margin-top: 12px;
                padding: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px;
                color: #334155;
            }
        """
        label_css = "font-size: 14px; color: #475569;"
        spinbox_css = """
            QSpinBox {
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 4px 8px;
                min-width: 80px;
            }
        """
        combobox_css = """
            QComboBox {
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 4px 8px;
                min-width: 100px;
                background-color: white;
            }
        """
        slider_css = """
            QSlider::groove:horizontal {
                border: 1px solid #cbd5e1;
                height: 6px;
                background: #e2e8f0;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #3b82f6;
                border: none;
                width: 16px;
                height: 16px;
                border-radius: 8px;
                margin: -5px 0;
            }
        """

        # Pressure Settings Group
        pressure_group = QGroupBox("Pressure Settings")
        pressure_group.setStyleSheet(groupbox_css)
        pressure_layout = QVBoxLayout(pressure_group)
        
        # Mode selection
        mode_layout = QHBoxLayout()
        mode_label = QLabel("Therapy Mode:")
        mode_label.setStyleSheet(label_css)
        self.mode_combo = QComboBox()
        self.mode_combo.setStyleSheet(combobox_css)
        self.mode_combo.addItems(["CPAP", "APAP", "BiPAP"])
        self.mode_combo.setCurrentText(self.current_settings.get("mode", "CPAP"))
        self.mode_combo.currentTextChanged.connect(self.on_mode_changed)
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.mode_combo)
        mode_layout.addStretch()
        pressure_layout.addLayout(mode_layout)
        
        # Pressure settings container
        self.pressure_widget = QWidget()
        self.pressure_layout = QVBoxLayout(self.pressure_widget)
        pressure_layout.addWidget(self.pressure_widget)
        self.update_pressure_ui(self.current_settings.get("mode", "CPAP"))
        
        # Comfort Settings Group
        comfort_group = QGroupBox("Comfort Settings")
        comfort_group.setStyleSheet(groupbox_css)
        comfort_layout = QVBoxLayout(comfort_group)
        
        # Ramp settings
        ramp_layout = QHBoxLayout()
        ramp_label = QLabel("Ramp Time (minutes):")
        ramp_label.setStyleSheet(label_css)
        self.ramp_spin = QSpinBox()
        self.ramp_spin.setStyleSheet(spinbox_css)
        self.ramp_spin.setRange(0, 45)
        self.ramp_spin.setValue(self.current_settings.get("ramp_time", 0))
        self.ramp_spin.setSuffix(" min")
        ramp_layout.addWidget(ramp_label)
        ramp_layout.addWidget(self.ramp_spin)
        ramp_layout.addStretch()
        comfort_layout.addLayout(ramp_layout)
        
        # EPR
        epr_layout = QHBoxLayout()
        epr_label = QLabel("EPR Level:")
        epr_label.setStyleSheet(label_css)
        self.epr_combo = QComboBox()
        self.epr_combo.setStyleSheet(combobox_css)
        self.epr_combo.addItems(["Off", "1", "2", "3"])
        self.epr_combo.setCurrentText(str(self.current_settings.get("epr", "Off")))
        epr_layout.addWidget(epr_label)
        epr_layout.addWidget(self.epr_combo)
        epr_layout.addStretch()
        comfort_layout.addLayout(epr_layout)
        
        # Humidity
        humidity_layout = QHBoxLayout()
        humidity_label = QLabel("Humidity Level:")
        humidity_label.setStyleSheet(label_css)
        self.humidity_slider = QSlider(Qt.Horizontal)
        self.humidity_slider.setStyleSheet(slider_css)
        self.humidity_slider.setRange(1, 8)
        self.humidity_slider.setValue(self.current_settings.get("humidity", 4))
        self.humidity_value = QLabel(str(self.current_settings.get("humidity", 4)))
        self.humidity_value.setStyleSheet("font-size: 14px; min-width: 24px; color: #1e293b;")
        self.humidity_slider.valueChanged.connect(lambda v: self.humidity_value.setText(str(v)))
        humidity_layout.addWidget(humidity_label)
        humidity_layout.addWidget(self.humidity_slider)
        humidity_layout.addWidget(self.humidity_value)
        humidity_layout.addStretch()
        comfort_layout.addLayout(humidity_layout)
        
        # Advanced Settings Group
        advanced_group = QGroupBox("Advanced Settings")
        advanced_group.setStyleSheet(groupbox_css)
        advanced_layout = QVBoxLayout(advanced_group)
        
        # Mask type
        mask_layout = QHBoxLayout()
        mask_label = QLabel("Mask Type:")
        mask_label.setStyleSheet(label_css)
        self.mask_combo = QComboBox()
        self.mask_combo.setStyleSheet(combobox_css)
        self.mask_combo.addItems(["Nasal", "Nasal Pillows", "Full Face"])
        self.mask_combo.setCurrentText(self.current_settings.get("mask_type", "Nasal"))
        mask_layout.addWidget(mask_label)
        mask_layout.addWidget(self.mask_combo)
        mask_layout.addStretch()
        advanced_layout.addLayout(mask_layout)
        
        # Tube temperature
        tube_layout = QHBoxLayout()
        tube_label = QLabel("Tube Temperature:")
        tube_label.setStyleSheet(label_css)
        self.tube_slider = QSlider(Qt.Horizontal)
        self.tube_slider.setStyleSheet(slider_css)
        self.tube_slider.setRange(60, 86)
        self.tube_slider.setValue(self.current_settings.get("tube_temp", 70))
        self.tube_value = QLabel(f"{self.current_settings.get('tube_temp', 70)}°F")
        self.tube_value.setStyleSheet("font-size: 14px; min-width: 40px; color: #1e293b;")
        self.tube_slider.valueChanged.connect(lambda v: self.tube_value.setText(f"{v}°F"))
        tube_layout.addWidget(tube_label)
        tube_layout.addWidget(self.tube_slider)
        tube_layout.addWidget(self.tube_value)
        tube_layout.addStretch()
        advanced_layout.addLayout(tube_layout)
        
        # Add groups to layout
        settings_layout.addWidget(pressure_group)
        settings_layout.addWidget(comfort_group)
        settings_layout.addWidget(advanced_group)
        settings_layout.addStretch()
        
        scroll_area.setWidget(settings_container)
        content_layout.addWidget(scroll_area)
        
        main_layout.addWidget(content_widget)
        self.setLayout(main_layout)

        # Sidebar navigation
        self.sidebar.dashboard_btn.clicked.connect(self.show_dashboard)
        self.sidebar.user_btn.clicked.connect(self.show_user_details)
        self.sidebar.therapy_btn.clicked.connect(self.show_therapy_data)
        self.sidebar.logout_btn.clicked.connect(self.logout)

    # (keep rest of methods same: update_pressure_ui, on_mode_changed, load_settings, save_settings, navigation)

    def update_pressure_ui(self, mode):
        # Clear previous pressure widgets
        for i in reversed(range(self.pressure_layout.count())): 
            self.pressure_layout.itemAt(i).widget().setParent(None)
        
        if mode == "CPAP":
            # Single pressure setting for CPAP
            cpap_layout = QHBoxLayout()
            cpap_label = QLabel("Pressure:")
            cpap_label.setStyleSheet("font-size: 14px;")
            self.cpap_spin = QSpinBox()
            self.cpap_spin.setRange(4, 20)
            self.cpap_spin.setValue(self.current_settings.get("pressure", 8))
            self.cpap_spin.setSuffix(" cmH₂O")
            cpap_layout.addWidget(cpap_label)
            cpap_layout.addWidget(self.cpap_spin)
            cpap_layout.addStretch()
            self.pressure_layout.addLayout(cpap_layout)
            
        elif mode == "APAP":
            # Min and max pressure for APAP
            min_layout = QHBoxLayout()
            min_label = QLabel("Min Pressure:")
            min_label.setStyleSheet("font-size: 14px;")
            self.min_spin = QSpinBox()
            self.min_spin.setRange(4, 15)
            self.min_spin.setValue(self.current_settings.get("min_pressure", 5))
            self.min_spin.setSuffix(" cmH₂O")
            min_layout.addWidget(min_label)
            min_layout.addWidget(self.min_spin)
            min_layout.addStretch()
            self.pressure_layout.addLayout(min_layout)
            
            max_layout = QHBoxLayout()
            max_label = QLabel("Max Pressure:")
            max_label.setStyleSheet("font-size: 14px;")
            self.max_spin = QSpinBox()
            self.max_spin.setRange(6, 20)
            self.max_spin.setValue(self.current_settings.get("max_pressure", 15))
            self.max_spin.setSuffix(" cmH₂O")
            max_layout.addWidget(max_label)
            max_layout.addWidget(self.max_spin)
            max_layout.addStretch()
            self.pressure_layout.addLayout(max_layout)
            
        elif mode == "BiPAP":
            # IPAP and EPAP for BiPAP
            ipap_layout = QHBoxLayout()
            ipap_label = QLabel("IPAP Pressure:")
            ipap_label.setStyleSheet("font-size: 14px;")
            self.ipap_spin = QSpinBox()
            self.ipap_spin.setRange(4, 25)
            self.ipap_spin.setValue(self.current_settings.get("ipap", 12))
            self.ipap_spin.setSuffix(" cmH₂O")
            ipap_layout.addWidget(ipap_label)
            ipap_layout.addWidget(self.ipap_spin)
            ipap_layout.addStretch()
            self.pressure_layout.addLayout(ipap_layout)
            
            epap_layout = QHBoxLayout()
            epap_label = QLabel("EPAP Pressure:")
            epap_label.setStyleSheet("font-size: 14px;")
            self.epap_spin = QSpinBox()
            self.epap_spin.setRange(4, 20)
            self.epap_spin.setValue(self.current_settings.get("epap", 6))
            self.epap_spin.setSuffix(" cmH₂O")
            epap_layout.addWidget(epap_label)
            epap_layout.addWidget(self.epap_spin)
            epap_layout.addStretch()
            self.pressure_layout.addLayout(epap_layout)
    
    def on_mode_changed(self, mode):
        self.update_pressure_ui(mode)
    
    def load_settings(self):
        default_settings = {
            "mode": "CPAP",
            "pressure": 8,
            "min_pressure": 5,
            "max_pressure": 15,
            "ipap": 12,
            "epap": 6,
            "ramp_time": 0,
            "epr": "Off",
            "humidity": 4,
            "mask_type": "Nasal",
            "tube_temp": 70
        }
        
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    for key in default_settings:
                        if key not in loaded_settings:
                            loaded_settings[key] = default_settings[key]
                    return loaded_settings
        except Exception as e:
            print(f"Error loading settings: {e}")
        
        return default_settings
    
    def save_settings(self):
        try:
            # Gather all settings based on current mode
            settings = {
                "mode": self.mode_combo.currentText(),
                "ramp_time": self.ramp_spin.value(),
                "epr": self.epr_combo.currentText(),
                "humidity": self.humidity_slider.value(),
                "mask_type": self.mask_combo.currentText(),
                "tube_temp": self.tube_slider.value()
            }
            
            # Add pressure settings based on mode
            mode = self.mode_combo.currentText()
            if mode == "CPAP":
                settings["pressure"] = self.cpap_spin.value()
            elif mode == "APAP":
                settings["min_pressure"] = self.min_spin.value()
                settings["max_pressure"] = self.max_spin.value()
            elif mode == "BiPAP":
                settings["ipap"] = self.ipap_spin.value()
                settings["epap"] = self.epap_spin.value()
            
            # Save to file
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=4)
            
            self.current_settings = settings
            
            QMessageBox.information(
                self, 
                "Settings Saved", 
                "Your CPAP settings have been saved successfully."
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Save Error",
                f"An error occurred while saving settings: {str(e)}"
            )
    
    def show_dashboard(self):
        # Load user data if it exists
        user_data = {}
        try:
            if os.path.exists('user_data.json'):
                with open('user_data.json', 'r') as f:
                    user_data = json.load(f)
        except:
            pass
        
        from Cpap_dash import DashboardPage
        dashboard = DashboardPage(self.stacked_widget, user_data)
        self.stacked_widget.addWidget(dashboard)
        self.stacked_widget.setCurrentWidget(dashboard)

    def show_user_details(self):
        # Load user data if it exists
        user_data = {}
        try:
            if os.path.exists('user_data.json'):
                with open('user_data.json', 'r') as f:
                    user_data = json.load(f)
        except:
            pass
        
        from Cpap_dash import DashboardPage
        dashboard = DashboardPage(self.stacked_widget, user_data, "view_user")
        self.stacked_widget.addWidget(dashboard)
        self.stacked_widget.setCurrentWidget(dashboard)
    
    def show_therapy_data(self):
        from therapy import TherapyDataPage
        therapy_page = TherapyDataPage(self.stacked_widget)
        self.stacked_widget.addWidget(therapy_page)
        self.stacked_widget.setCurrentWidget(therapy_page)
    
    def logout(self):
        reply = QMessageBox.question(
            self, 'Confirm Logout',
            'Are you sure you want to logout?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
    
        if reply == QMessageBox.Yes:
            # Close the main window (and app will exit)
            self.window().close()