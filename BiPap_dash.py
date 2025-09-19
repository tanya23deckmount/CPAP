import sys
import json
import os
import sqlite3
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QStackedWidget,
                             QFrame, QLineEdit, QDialog, QDialogButtonBox, 
                             QMessageBox, QFormLayout, QGroupBox, QTextEdit, QComboBox,
                             QTableWidget, QTableWidgetItem, QHeaderView, QScrollArea,
                             QGridLayout, QMenu, QSizePolicy)
from PyQt5.QtCore import Qt, QSize, QRect, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QIcon, QPalette, QColor, QPainter, QPen
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis
from PyQt5.QtCore import QPointF
from userdetails import  ViewUserDialog

 # Make sure BiPap_dash.py has BiPapDashboardPage class



class BiPapDashboardPage(QWidget):
    def __init__(self, stacked_widget, user):
        super().__init__()
        self.stacked_widget = stacked_widget
        layout = QVBoxLayout()
        label = QLabel(f"Welcome to BiPAP Dashboard, {user['serial_number']}")
        layout.addWidget(label)
        self.setLayout(layout)
class TitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(40)
        self.setStyleSheet("""
            background-color: #2c3e50;
            color: white;
            font-weight: bold;
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
        """)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 0, 10, 0)
        
        # Logo and title on the left
        logo_layout = QHBoxLayout()
        
        # Logo
        self.logo = QLabel()
        self.logo.setFixedSize(30, 30)
        self.logo.setStyleSheet("background: transparent;")
        
        # Create a simple logo programmatically
        pixmap = QPixmap(30, 30)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(52, 152, 219))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(5, 5, 20, 20)
        painter.setPen(QPen(Qt.white, 2))
        painter.drawText(QRect(5, 5, 20, 20), Qt.AlignCenter, "C")
        painter.end()
        
        self.logo.setPixmap(pixmap)
        
        # Title
        self.title = QLabel("BiPAP Therapy Dashboard")
        self.title.setStyleSheet("color: white; font-size: 14px;")
        
        logo_layout.addWidget(self.logo)
        logo_layout.addSpacing(5)
        logo_layout.addWidget(self.title)
        logo_layout.addSpacing(10)
        
        # Buttons on the right
        self.minimize_btn = QPushButton("−")
        self.maximize_btn = QPushButton("□")
        self.close_btn = QPushButton("×")
        
        # Style buttons
        button_style = """
            QPushButton {
                color: white;
                background-color: transparent;
                border: none;
                font-weight: bold;
                font-size: 16px;
                padding: 0px 5px;
            }
            QPushButton:hover {
                background-color: #34495e;
                border-radius: 5px;
            }
        """
        
        close_style = """
            QPushButton {
                color: white;
                background-color: transparent;
                border: none;
                font-weight: bold;
                font-size: 16px;
                padding: 0px 5px;
            }
            QPushButton:hover {
                background-color: #e74c3c;
                border-radius: 5px;
            }
        """
        
        self.minimize_btn.setStyleSheet(button_style)
        self.maximize_btn.setStyleSheet(button_style)
        self.close_btn.setStyleSheet(close_style)
        
        # Set fixed sizes for buttons
        self.minimize_btn.setFixedSize(QSize(25, 25))
        self.maximize_btn.setFixedSize(QSize(25, 25))
        self.close_btn.setFixedSize(QSize(25, 25))
        
        # Connect buttons
        self.minimize_btn.clicked.connect(self.parent.showMinimized)
        self.maximize_btn.clicked.connect(self.toggle_maximize)
        self.close_btn.clicked.connect(self.parent.close)
        
        # Add widgets to layout
        layout.addLayout(logo_layout)
        layout.addStretch(1)
        layout.addWidget(self.minimize_btn)
        layout.addWidget(self.maximize_btn)
        layout.addWidget(self.close_btn)
        
        self.setLayout(layout)
        
        # For window dragging
        self.start = None
        self.maximized = False
        
    def toggle_maximize(self):
        if self.maximized:
            self.parent.showNormal()
            self.maximized = False
            self.maximize_btn.setText("□")
        else:
            self.parent.showMaximized()
            self.maximized = True
            self.maximize_btn.setText("❐")   
            
                  
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start = self.mapToGlobal(event.pos())
            
    def mouseMoveEvent(self, event):
        if self.start and not self.maximized:
            move_to = self.mapToGlobal(event.pos())
            diff = move_to - self.start
            new_pos = self.parent.pos() + diff
            self.parent.move(new_pos)
            self.start = move_to
            
    def mouseReleaseEvent(self, event):
        self.start = None
        
class SideBar(QWidget):
    userActionRequested = pyqtSignal(str)  # Signal to communicate user actions
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(250)
        # Sidebar theme
        self.setStyleSheet("""
            QWidget {
                background-color: #9da3cf;
                color: #2c3e50;
                border: none;
            }
            QPushButton {
                background-color: transparent;
                color: #2c3e50;
                border: none;
                text-align: left;
                padding: 15px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8aacd6;
            }
            QPushButton:pressed {
                background-color: #7299c9;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 20)
        
        # ---------- Logo Section ----------
        logo_container = QWidget()
        logo_container.setStyleSheet("background-color: #6d76b5;")
        logo_container.setFixedHeight(80)
        logo_container.setFixedWidth(250)
        
        logo_layout = QHBoxLayout(logo_container)
        logo_layout.setContentsMargins(10, 10, 10, 10)
        
        logo_label = QLabel()
        logo_label.setFixedSize(60, 60)
        logo_label.setStyleSheet("background: transparent;")
        
        # Draw a circle with "C"
        pixmap = QPixmap(60, 60)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(52, 152, 219))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(10, 10, 40, 40)
        painter.setPen(QPen(Qt.white, 3))
        font = QFont()
        font.setPointSize(20)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(QRect(10, 10, 40, 40), Qt.AlignCenter, "C")
        painter.end()
        
        logo_label.setPixmap(pixmap)
        
        company_name = QLabel("BiPAP Therapy")
        company_name.setStyleSheet("color: #2c3e50; font-size: 16px; font-weight: bold; font-weight: bold;")
        
        logo_layout.addWidget(logo_label)
        logo_layout.addSpacing(10)
        logo_layout.addWidget(company_name)
        logo_layout.addStretch()
        
        layout.addWidget(logo_container)
        
        # ---------- Buttons ----------
        self.dashboard_btn = QPushButton("📊 Dashboard")
        self.dashboard_btn.setIconSize(QSize(20, 20))
        
        # User button with dropdown
        self.user_btn = QPushButton("👤 User Details")
        self.user_btn.setIconSize(QSize(20, 20))
        
        self.user_menu = QMenu(self)
        self.user_menu.setStyleSheet("""
            QMenu {
                background-color: #a3c4e0;
                color: #2c3e50;
                border: 1px solid #8aacd6;
            }
            QMenu::item {
                padding: 8px 20px;
            }
            QMenu::item:selected {
                background-color: #8aacd6;
            }
        """)
        # self.user_menu.addAction("Add User", lambda: self.userActionRequested.emit("add_user"))
        self.user_menu.addAction("View User", lambda: self.userActionRequested.emit("view_user"))
        
        self.user_btn.setMenu(self.user_menu)

        # 🔑 Fix: make dropdown same width as button
        self.user_menu.aboutToShow.connect(
            lambda: self.user_menu.setFixedWidth(self.user_btn.width())
        )
        
        # Other buttons
        self.therapy_btn = QPushButton("💤 Therapy Data")
        self.therapy_btn.setIconSize(QSize(20, 20))
        
        self.settings_btn = QPushButton("⚙️ Settings")
        self.settings_btn.setIconSize(QSize(20, 20))
        
        layout.addWidget(self.dashboard_btn)
        layout.addWidget(self.user_btn)
        layout.addWidget(self.therapy_btn)
        layout.addWidget(self.settings_btn)
        layout.addStretch(1)
        
        # ---------- Logout ----------
        self.logout_btn = QPushButton("🚶 Logout")
        self.logout_btn.setStyleSheet("""
        QPushButton {
             background-color: qlineargradient(
                 x1:0, y1:0, x2:1, y2:1,
                 stop:0 #ff5f6d, stop:1 #d62828
             );
             color: white;
             border: none;
             text-align: center;
             padding: 10px 20px;
             font-size: 14px;
             font-weight: bold;
             border-radius: 15px;
             min-width: 120px;
             max-width: 140px;
             box-shadow: 2px 2px 6px rgba(0,0,0,0.25);
         }
         QPushButton:hover {
             background-color: qlineargradient(
                 x1:0, y1:0, x2:1, y2:1,
                 stop:0 #ff7f83, stop:1 #b71c1c
             );
         }
         QPushButton:pressed {
             background-color: #a31212;
         }
        """)
        layout.addWidget(self.logout_btn, alignment=Qt.AlignHCenter)
        
        self.setLayout(layout)
        
        
class DashboardPage(QWidget):
    def __init__(self, stacked_widget, user_data, show_form=None):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.user_data = user_data
        self.user_details_added = False
        self.user_form = None
        self.show_form_on_load = show_form  # Track which form to show on load

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create sidebar
        self.sidebar = SideBar()
        main_layout.addWidget(self.sidebar)
        
        # Content area
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #f5f6fa;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        
        # Welcome message
        self.welcome_label = QLabel("Welcome to BiPAP Therapy Dashboard")
        self.welcome_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
        """)
        
        # Back to dashboard button (initially hidden)
        self.back_btn = QPushButton("Back to Dashboard")
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.back_btn.hide()
        self.back_btn.clicked.connect(self.show_normal_dashboard)
        
        header_layout.addWidget(self.welcome_label)
        header_layout.addStretch()
        header_layout.addWidget(self.back_btn)
        
        content_layout.addLayout(header_layout)
        content_layout.addSpacing(20)
        
        # Dashboard content
        self.content_frame = QFrame()
        self.content_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
            }
        """)
        
        self.content_frame_layout = QVBoxLayout(self.content_frame)
        self.content_frame_layout.setContentsMargins(20, 20, 20, 230)
        
        # Show the appropriate content based on show_form parameter
        if show_form == "add_user":
            self.show_add_user_form()
        elif show_form == "view_user":
            self.show_view_user()
        else:
            self.show_normal_dashboard()
        
        content_layout.addWidget(self.content_frame)
        content_layout.addStretch()
        
        main_layout.addWidget(content_widget)
        self.setLayout(main_layout)
        
        # Connect sidebar buttons
        self.sidebar.logout_btn.clicked.connect(self.logout)
        self.sidebar.userActionRequested.connect(self.handle_user_action)
        self.sidebar.therapy_btn.clicked.connect(self.show_therapy_data)
        self.sidebar.settings_btn.clicked.connect(self.show_settings)
        self.sidebar.dashboard_btn.clicked.connect(self.show_normal_dashboard)
        
        # Update the display based on initial user data
        self.update_display()
    
    def show_normal_dashboard(self):
        # Hide the back button
        self.back_btn.hide()
        
        # Clear the content frame
        self.clear_layout(self.content_frame_layout)
        
        # Stats section
        stats_layout = QHBoxLayout()        
        
        # Get total users count
        total_users = self.get_total_users()        
        
        # Create stat cards
        # stats = [
        #   {"title": "🧑‍⚕️ Active Patient", "value": str(total_users), "unit": "", "color": "#216491"},
        #    {"title": "💊 Device Compliance", "value": "92", "unit": "%", "color": "#1f864a"},
        #    {"title": "💾 Active Storage", "value": "85", "unit": "GB", "color": "#bb780e"},
        #    {"title": "🫁 Avg AHI Score", "value": "2.1", "unit": "events/hr", "color": "#da2c19"}
        # ]
        
        # for stat in stats:
        #     card = QFrame()
        #     card.setFixedHeight(120)
        #     card.setMinimumWidth(250)
        #     card.setStyleSheet(f"""
        #         QFrame {{
        #             background-color: {stat['color']};
        #             border-radius: 10px;
        #             padding: 4px;
                    
        #         }}
        #         QLabel {{
        #             color: white;
        #         }}
        #     """)
            
        #     card_layout = QVBoxLayout(card)
            
            # title = QLabel(stat['title'])
            # title.setStyleSheet("font-size: 22px; font-weight: bold;")
            
            # value = QLabel(f"<span style='font-size: 28px; font-weight: bold;'>{stat['value']}</span> {stat['unit']}")
            # value.setAlignment(Qt.AlignCenter)
            
            # card_layout.addWidget(title)
            # card_layout.addStretch()
            # card_layout.addWidget(value)
            
        #     stats_layout.addWidget(card)
        
        # self.content_frame_layout.addLayout(stats_layout)
        # self.content_frame_layout.addSpacing(20)
        
        # Graph section
        graph_label = QLabel("BiPAP- Dashboard")
        graph_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        self.content_frame_layout.addWidget(graph_label)
        
        # Create a simple graph (simulated with a frame)
        graph_frame = QFrame()
        graph_frame.setFixedHeight(300)
        graph_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #e0e0e0;
                border-radius: 5px;
            }
        """)
        
        # Create a simple chart (simulated)
        chart_layout = QVBoxLayout(graph_frame)
        
        # Add chart title
        chart_title = QLabel("AHI Score Over Time")
        chart_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        chart_title.setAlignment(Qt.AlignCenter)
        chart_layout.addWidget(chart_title)
        
        # Add a simulated chart image or drawing
        chart_content = QLabel()
        chart_content.setAlignment(Qt.AlignCenter)
        chart_content.setText("Chart visualization would appear here")
        chart_content.setStyleSheet("color: #7f8c8d; font-size: 14px;")
        chart_layout.addWidget(chart_content)
        
        self.content_frame_layout.addWidget(graph_frame)
    
    def get_total_users(self):
      try:
          connection = sqlite3.connect('user_data.db')  # Use your actual database name
          cursor = connection.cursor()
          cursor.execute("SELECT COUNT(*) FROM users")  # Use your actual table name
          count = cursor.fetchone()[0]
          connection.close()
          return count
      except Exception as e:
          print(f"Error fetching user count: {e}")
          return 0   
        
        
    def clear_layout(self, layout):
        # Clear all widgets from a layout
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def handle_user_action(self, action):
        # Handle user actions from the sidebar menu
        if action == "add_user":
            self.show_add_user_form()
        elif action == "view_user":
            self.show_view_user()
    
    def show_add_user_form(self):
        # Show the back button
        self.back_btn.show()
        
        # Hide the welcome label
        self.welcome_label.hide()  # Add this line
        
        # Clear the content frame
        self.clear_layout(self.content_frame_layout)
        
        # Create a container for the user details form
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(0, 0, 0, 0)
        
        # Use your existing UserDetailsDialog but as a widget instead of dialog
        # We'll create it without parent to avoid dialog behavior
        # self.user_form = UserDetailsDialog(None, self.user_data, "add")
        
        # Remove dialog buttons and add our own to integrate with dashboard
        if hasattr(self.user_form, 'button_box'):
            self.user_form.button_box.hide()
        
        # Add the form to our container
        form_layout.addWidget(self.user_form)
        
        # Create our own buttons for the dashboard
        # button_layout = QHBoxLayout()
        # save_btn = QPushButton("Save")
        # cancel_btn = QPushButton("Cancel")
        
        # save_btn.setStyleSheet("""
        #     QPushButton {
        #         background-color: #27ae60;
        #         color: white;
        #         border: none;
        #         padding: 10px 20px;
        #         border-radius: 8px;
        #         font-weight: bold;
        #     }
        #     QPushButton:hover {
        #         background-color: #219653;
        #     }
        # """)
        
        # cancel_btn.setStyleSheet("""
        #     QPushButton {
        #         background-color: #e74c3c;
        #         color: white;
        #         border: none;
        #         padding: 10px 20px;
        #         border-radius: 8px;
        #         font-weight: bold;
        #     }
        #     QPushButton:hover {
        #         background-color: #c0392b;
        #     }
        # """)
        
        # button_layout.addStretch()
        # button_layout.addWidget(cancel_btn)
        # button_layout.addWidget(save_btn)
        # form_layout.addLayout(button_layout)
        
        # Connect buttons
        # cancel_btn.clicked.connect(self.show_normal_dashboard)
        # save_btn.clicked.connect(self.save_user_data_from_form)
        
        # Add the form container to the content frame
        self.content_frame_layout.addWidget(form_container)
    

    def show_view_user(self):
       # Show the back button
       self.back_btn.show()
       
        # Hide the welcome label
       self.welcome_label.hide() 
       
       # Clear the content frame
       self.clear_layout(self.content_frame_layout)
       
       # Create a container for the user details view
       view_container = QWidget()
       view_layout = QVBoxLayout(view_container)
       view_layout.setContentsMargins(0, 0, 0, 0)
       
       # Use the new ViewUserDialog
       self.user_view = ViewUserDialog()
       
       # Remove dialog buttons if any
       if hasattr(self.user_view, 'button_box'):
           self.user_view.button_box.hide()
       
       # Add the form to our container
       view_layout.addWidget(self.user_view)
       
       # Add the view container to the content frame
       self.content_frame_layout.addWidget(view_container)
    
    def save_user_data_from_form(self):
        # Get data from the form
        if self.user_form:
            self.user_data = self.user_form.get_user_data()
            
            # Save to JSON file
            try:
                with open('user_data.json', 'w') as f:
                    json.dump(self.user_data, f)
                QMessageBox.information(self, "Success", "User data saved successfully!")
                self.show_normal_dashboard()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to save user data: {str(e)}")
            
            # Update display
            self.update_display()
        
    def update_display(self):
        # Update the display based on user data
        self.user_data and any(self.user_data.values())
        self.user_details_added = True
        self.welcome_label.setText("Welcome to BiPAP Therapy Dashboard")
        # else:
        #     self.user_details_added = False
        #     self.welcome_label.setText("Welcome to BiPAP Therapy Dashboard")
    
    def show_therapy_data(self):
        # Switch to therapy data page
        therapy_page = TherapyDataPage(self.stacked_widget)
        self.stacked_widget.addWidget(therapy_page)
        self.stacked_widget.setCurrentWidget(therapy_page)
    
    def show_settings(self):
        # Switch to settings page
        settings_page = SettingsPage(self.stacked_widget)
        self.stacked_widget.addWidget(settings_page)
        self.stacked_widget.setCurrentWidget(settings_page)
    
    def logout(self):
        # Confirm logout
        reply = QMessageBox.question(
            self, 'Confirm Logout',
            'Are you sure you want to logout?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
    
        if reply == QMessageBox.Yes:
            # Close the main window (and app will exit)
            self.window().close()


class TherapyDataPage(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create sidebar
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
        self.sidebar.userActionRequested.connect(self.handle_user_action)
        self.sidebar.logout_btn.clicked.connect(self.logout)
        self.sidebar.settings_btn.clicked.connect(self.show_settings)
    
    def handle_user_action(self, action):
        # Instead of showing a message, navigate to dashboard with the appropriate form
        # Load user data if it exists
        user_data = {}
        try:
            if os.path.exists('user_data.json'):
                with open('user_data.json', 'r') as f:
                    user_data = json.load(f)
        except:
            pass
        
        # Create dashboard with the form to show
        dashboard = DashboardPage(self.stacked_widget, user_data, action)
        self.stacked_widget.addWidget(dashboard)
        self.stacked_widget.setCurrentWidget(dashboard)
    
    def show_dashboard(self):
        # Load user data if it exists
        user_data = {}
        try:
            if os.path.exists('user_data.json'):
                with open('user_data.json', 'r') as f:
                    user_data = json.load(f)
        except:
            pass
        
        dashboard = DashboardPage(self.stacked_widget, user_data)
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


class SettingsPage(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create sidebar
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
        title_label = QLabel("Settings")
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
        """)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        content_layout.addLayout(header_layout)
        content_layout.addSpacing(20)
        
        # Settings content
        settings_frame = QFrame()
        settings_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        
        settings_layout = QVBoxLayout(settings_frame)
        
        # Add settings content here
        settings_label = QLabel("Application settings will be displayed here.")
        settings_label.setStyleSheet("font-size: 16px; color: #7f8c8d;")
        settings_label.setAlignment(Qt.AlignCenter)
        
        settings_layout.addWidget(settings_label)
        settings_layout.addStretch()
        
        content_layout.addWidget(settings_frame)
        content_layout.addStretch()
        
        main_layout.addWidget(content_widget)
        self.setLayout(main_layout)
        
        # Connect sidebar buttons
        self.sidebar.dashboard_btn.clicked.connect(self.show_dashboard)
        self.sidebar.userActionRequested.connect(self.handle_user_action)
        self.sidebar.therapy_btn.clicked.connect(self.show_therapy_data)
        self.sidebar.logout_btn.clicked.connect(self.logout)
    
    def handle_user_action(self, action):
        # Instead of showing a message, navigate to dashboard with the appropriate form
        # Load user data if it exists
        user_data = {}
        try:
            if os.path.exists('user_data.json'):
                with open('user_data.json', 'r') as f:
                    user_data = json.load(f)
        except:
            pass
        
        # Create dashboard with the form to show
        dashboard = DashboardPage(self.stacked_widget, user_data, action)
        self.stacked_widget.addWidget(dashboard)
        self.stacked_widget.setCurrentWidget(dashboard)
    
    def show_dashboard(self):
        # Load user data if it exists
        user_data = {}
        try:
            if os.path.exists('user_data.json'):
                with open('user_data.json', 'r') as f:
                    user_data = json.load(f)
        except:
            pass
        
        dashboard = DashboardPage(self.stacked_widget, user_data)
        self.stacked_widget.addWidget(dashboard)
        self.stacked_widget.setCurrentWidget(dashboard)
    
    def show_therapy_data(self):
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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BiPAP Therapy Dashboard")
        self.setGeometry(100, 100, 1200, 800)  # Increased window size
        
        # Remove default window frame
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        # Set central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Create main layout
        self.central_layout = QVBoxLayout(self.central_widget)
        self.central_layout.setContentsMargins(0, 0, 0, 0)
        self.central_layout.setSpacing(0)
        
        # Create title bar
        self.title_bar = TitleBar(self)
        self.central_layout.addWidget(self.title_bar)
        
        # Create stacked widget for content
        self.stacked_widget = QStackedWidget()
        self.central_layout.addWidget(self.stacked_widget)
        
        # Load user data if it exists
        user_data = {}
        try:
            if os.path.exists('user_data.json'):
                with open('user_data.json', 'r') as f:
                    user_data = json.load(f)
        except:
            pass
        
        # Add dashboard page first
        self.dashboard_page = DashboardPage(self.stacked_widget, user_data)
        self.stacked_widget.addWidget(self.dashboard_page)
        
        # Set styles
        self.setStyleSheet("""
            QMainWindow {
                background-color: white;
                border-radius: 10px;
            }
        """)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Set palette for a consistent color scheme
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(245, 246, 250))
    palette.setColor(QPalette.WindowText, Qt.black)
    palette.setColor(QPalette.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.AlternateBase, QColor(233, 235, 239))
    palette.setColor(QPalette.ToolTipBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.black)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Highlight, QColor(142, 158, 171).lighter())
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())