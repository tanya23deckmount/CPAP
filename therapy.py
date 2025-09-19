from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QMessageBox)
from PyQt5.QtCore import Qt
from settings import SettingsPage
import json
import os


class TherapyDataPage(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create sidebar
        from Cpap_dash import SideBar
        self.sidebar = SideBar()
        main_layout.addWidget(self.sidebar)
        
        # Content area
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #f5f6fa;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        
        # Title
        title_label = QLabel("Therapy Data")
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
        """)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        content_layout.addLayout(header_layout)
        content_layout.addSpacing(20)
        
        # Therapy data content
        data_frame = QFrame()
        data_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        
        data_layout = QVBoxLayout(data_frame)
        
        # Add therapy data content here
        data_label = QLabel("Therapy data will be displayed here.")
        data_label.setStyleSheet("font-size: 16px; color: #7f8c8d;")
        data_label.setAlignment(Qt.AlignCenter)
        
        data_layout.addWidget(data_label)
        data_layout.addStretch()
        
        content_layout.addWidget(data_frame)
        content_layout.addStretch()
        
        main_layout.addWidget(content_widget)
        self.setLayout(main_layout)
        
        # Connect sidebar buttons
        self.sidebar.dashboard_btn.clicked.connect(self.show_dashboard)
        self.sidebar.user_btn.clicked.connect(self.show_user_details)
        self.sidebar.logout_btn.clicked.connect(self.logout)
        self.sidebar.settings_btn.clicked.connect(self.show_settings)
    
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
    
    def show_settings(self):
        settings_page = SettingsPage(self.stacked_widget)
        self.stacked_widget.addWidget(settings_page)
        self.stacked_widget.setCurrentWidget(settings_page)
    
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