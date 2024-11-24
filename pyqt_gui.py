import sys

import asyncio
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QPushButton,
    QLineEdit,
    QDateTimeEdit,
    QTextEdit,
    QMessageBox,
    QLabel,
    QCalendarWidget,
    QHBoxLayout,
)
from PyQt6.QtCore import QDateTime


from kuda_idem_template import Event, send_html_message


class RequiredLabel(QLabel):
    """Custom label for form fields that indicates if a field is required"""

    def __init__(self, text: str, required: bool = False):
        super().__init__()
        self.setText(f"{text}{'*' if required else ' (optional)'}")  # Add '(optional)' text
        if required:
            self.setStyleSheet(
                "color: #D32F2F; font-weight: bold;"
            )  # Red color for required fields
        else:
            self.setStyleSheet(
                "color: #666666; font-weight: normal;"
            )  # Grey color for optional fields


class DateTimePickerWidget(QWidget):
    """Custom DateTime picker with calendar popup"""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create DateTime edit
        self.datetime_edit = QDateTimeEdit(self)
        self.datetime_edit.setCalendarPopup(True)

        # Set 24-hour format
        self.datetime_edit.setDisplayFormat("dd.MM.yyyy HH:00")

        # Get current time and set minutes to 00
        current = QDateTime.currentDateTime()
        current = current.addSecs(-current.time().minute() * 60 - current.time().second())
        self.datetime_edit.setDateTime(current)

        # Customize the calendar popup
        calendar = QCalendarWidget(self)
        calendar.setGridVisible(True)
        calendar.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)

        # Set explicit styles for the calendar
        calendar.setStyleSheet("""
            QCalendarWidget {
                background-color: white;
            }
            QCalendarWidget QTableView {
                background-color: white;
                selection-background-color: #0078D7;
                selection-color: white;
            }
            /* Style for dates */
            QCalendarWidget QTableView QTableCornerButton::section {
                color: #333333;
                background-color: white;
            }
            QCalendarWidget QTableView QTableCell {
                color: #333333;
            }
        """)

        self.datetime_edit.setCalendarWidget(calendar)
        layout.addWidget(self.datetime_edit)

    def dateTime(self):
        return self.datetime_edit.dateTime()

    def setDateTime(self, datetime):
        # When setting datetime externally, ensure minutes are set to 00
        datetime = datetime.addSecs(-datetime.time().minute() * 60 - datetime.time().second())
        self.datetime_edit.setDateTime(datetime)


class PlainTextEdit(QTextEdit):
    """Custom QTextEdit that forces plain text paste without formatting"""

    def insertFromMimeData(self, source):
        """Override paste behavior to insert plain text only"""
        if source.hasText():
            self.insertPlainText(source.text())


class EventInputWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Event Input Form")
        self.setGeometry(100, 100, 600, 800)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Add header with legend
        legend_label = QLabel("* indicates required fields")
        legend_label.setStyleSheet("color: #D32F2F; font-style: italic; padding: 5px;")
        layout.addWidget(legend_label)

        # Set the main window background
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F5F5F5;
            }
            QWidget {
                background-color: #F5F5F5;
            }
        """)

        # Create form layout
        form_layout = QFormLayout()

        # Create input fields with required indicators
        self.city = QLineEdit()
        self.title = QLineEdit()
        self.title_link = QLineEdit()
        self.description = PlainTextEdit()  # Create PlainTextEdit here instead of QTextEdit
        self.description.setAcceptRichText(False)
        self.start_datetime = DateTimePickerWidget()
        self.end_datetime = DateTimePickerWidget()
        self.venue_name = QLineEdit()
        self.venue_address = QLineEdit()
        self.venue_map_link = QLineEdit()
        self.ticket_link = QLineEdit()
        self.ticket_info = QLineEdit()

        # Add placeholder texts for optional fields

        self.title_link.setPlaceholderText("Optional - URL to event details")
        self.description.setPlaceholderText("Optional - Event description")
        self.ticket_link.setPlaceholderText("Optional - URL to purchase tickets")
        self.ticket_info.setPlaceholderText(
            "Optional - Default: 'Билет не нужен.', displays only if the ticket URL is missing"
        )

        # Add fields to form layout with required indicators
        form_layout.addRow(RequiredLabel("City", required=True), self.city)
        form_layout.addRow(RequiredLabel("Title", required=True), self.title)
        form_layout.addRow(RequiredLabel("Title Link"), self.title_link)  # optional
        form_layout.addRow(RequiredLabel("Description"), self.description)  # optional
        form_layout.addRow(RequiredLabel("Start DateTime", required=True), self.start_datetime)
        form_layout.addRow(RequiredLabel("End DateTime", required=True), self.end_datetime)
        form_layout.addRow(RequiredLabel("Venue Name", required=True), self.venue_name)
        form_layout.addRow(RequiredLabel("Venue Address", required=True), self.venue_address)
        form_layout.addRow(RequiredLabel("Venue Map Link", required=True), self.venue_map_link)
        form_layout.addRow(RequiredLabel("Ticket Link"), self.ticket_link)  # optional
        form_layout.addRow(RequiredLabel("Ticket Info"), self.ticket_info)  # optional

        # Style required fields
        required_fields = [
            self.city,
            self.title,
            self.venue_name,
            self.venue_address,
            self.venue_map_link,
        ]
        for field in required_fields:
            field.setStyleSheet("""
                    QLineEdit {
                        border: 1px solid #C0C0C0;
                        border-radius: 3px;
                        padding: 5px;
                    }
                    QLineEdit:focus {
                        border: 2px solid #0078D7;
                    }
                """)

        # Add form layout to main layout
        layout.addLayout(form_layout)

        # Create button layout
        button_layout = QHBoxLayout()

        # Add submit button
        self.submit_button = QPushButton("Submit Event")
        self.submit_button.setStyleSheet("""
            QPushButton {
                background-color: #0078D7;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #005A9E;
            }
            QPushButton:pressed {
                background-color: #004275;
            }
        """)
        self.submit_button.clicked.connect(self.submit_event)
        button_layout.addWidget(self.submit_button)

        # Add view events button
        self.view_events_button = QPushButton("View Events")
        self.view_events_button.setStyleSheet("""
            QPushButton {
                background-color: #6C757D;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #5A6268;
            }
        """)
        self.view_events_button.clicked.connect(self.show_events)
        button_layout.addWidget(self.view_events_button)

        # Add send telegram button
        self.send_telegram_button = QPushButton("Send to Telegram")
        self.send_telegram_button.setStyleSheet("""
            QPushButton {
                background-color: #28A745;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1E7E34;
            }
        """)
        self.send_telegram_button.clicked.connect(self.send_to_telegram)
        button_layout.addWidget(self.send_telegram_button)

        # Add button layout to main layout
        layout.addLayout(button_layout)

        # Initialize events list
        self.events = []

    def validate_form(self) -> tuple[bool, str]:
        """Validate form fields"""
        required_fields = {
            "City": self.city.text(),
            "Title": self.title.text(),
            "Venue Name": self.venue_name.text(),
            "Venue Address": self.venue_address.text(),
            "Venue Map Link": self.venue_map_link.text(),
        }

        # Check required fields are not empty
        for field_name, value in required_fields.items():
            if not value.strip():
                return False, f"{field_name} is required!"

        # Validate datetime
        start = self.start_datetime.dateTime().toPyDateTime()
        end = self.end_datetime.dateTime().toPyDateTime()
        if end <= start:
            return False, "End time must be after start time!"

        # Validate URLs if provided
        urls_to_validate = {
            "Title Link": self.title_link.text(),
            "Venue Map Link": self.venue_map_link.text(),
            "Ticket Link": self.ticket_link.text(),
        }

        for field_name, url in urls_to_validate.items():
            if url and not url.startswith(("http://", "https://")):
                return False, f"{field_name} must be a valid URL starting with http:// or https://"

        return True, ""

    def submit_event(self) -> Event:
        """Create an Event object from form data"""
        try:
            return Event(
                city=self.city.text().strip(),
                title=self.title.text().strip(),
                title_link=self.title_link.text().strip() or None,
                description=self.description.toPlainText().strip() or None,
                start_datetime=self.start_datetime.dateTime().toPyDateTime(),
                end_datetime=self.end_datetime.dateTime().toPyDateTime(),
                venue_name=self.venue_name.text().strip(),
                venue_address=self.venue_address.text().strip(),
                venue_map_link=self.venue_map_link.text().strip(),
                ticket_link=self.ticket_link.text().strip() or None,
                ticket_info=self.ticket_info.text().strip() or None,
            )
        except Exception as e:
            raise ValueError(f"Error creating event: {str(e)}")

    def show_events(self):
        if not self.events:
            QMessageBox.information(self, "Events", "No events submitted yet.")
            return

        events_text = "Submitted Events:\n\n"
        for i, event in enumerate(self.events, 1):
            events_text += f"Event {i}:\n"
            events_text += f"Title: {event.title}\n"
            events_text += f"City: {event.city}\n"
            events_text += f"Venue: {event.venue_name}\n"
            events_text += f"Start: {event.start_datetime}\n"
            events_text += f"End: {event.end_datetime}\n"
            events_text += "-" * 40 + "\n"

        msg = QMessageBox()
        msg.setWindowTitle("Submitted Events")
        msg.setText(events_text)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

    def clear_form(self):
        """Clear all form fields"""
        self.city.clear()
        self.title.clear()
        self.title_link.clear()
        self.description.clear()
        self.venue_name.clear()
        self.venue_address.clear()
        self.venue_map_link.clear()
        self.ticket_link.clear()
        self.ticket_info.clear()

        current_datetime = QDateTime.currentDateTime()
        self.start_datetime.setDateTime(current_datetime)
        self.end_datetime.setDateTime(current_datetime)

    def send_to_telegram(self):
        """Send events to Telegram"""
        if not self.events:
            QMessageBox.warning(self, "Warning", "No events to send!")
            return

        try:
            # Disable buttons while sending
            self.submit_button.setEnabled(False)
            self.send_telegram_button.setEnabled(False)
            self.send_telegram_button.setText("Sending...")
            QApplication.processEvents()  # Update UI

            # Send the message
            asyncio.run(send_html_message(self.events))

            # Show success message with event count
            QMessageBox.information(
                self, "Success", f"Successfully sent {len(self.events)} event(s) to Telegram!"
            )

            # Clear events after successful sending
            self.events.clear()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to send to Telegram:\n{str(e)}")
        finally:
            # Re-enable buttons
            self.submit_button.setEnabled(True)
            self.send_telegram_button.setEnabled(True)
            self.send_telegram_button.setText("Send to Telegram")

    def closeEvent(self, event):
        """Handle application closing"""
        if self.events:
            reply = QMessageBox.question(
                self,
                "Confirm Exit",
                f"You have {len(self.events)} unsent event(s). Are you sure you want to quit?",
                QMessageBox.StandardButton.Yes,
                QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


def main():
    try:
        app = QApplication(sys.argv)
        app.setStyle("Fusion")

        app.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #F5F5F5;
            }
            QLineEdit, QTextEdit, QDateTimeEdit {
                background-color: white;
                border: 1px solid #C0C0C0;
                border-radius: 3px;
                padding: 5px;
                color: #333333;
            }
            QLineEdit:focus, QTextEdit:focus, QDateTimeEdit:focus {
                border: 2px solid #0078D7;
            }
            QLabel {
                font-size: 11pt;
                color: #333333;
            }
            QPushButton {
                min-width: 100px;
                min-height: 30px;
            }
            QCalendarWidget {
                background-color: white;
            }
            QCalendarWidget QToolButton {
                color: #333333;
                background-color: #F0F0F0;
            }
            QCalendarWidget QMenu {
                background-color: white;
                color: #333333;
            }
            QCalendarWidget QSpinBox {
                background-color: white;
                color: #333333;
            }
            QCalendarWidget QWidget {
                alternate-background-color: #F9F9F9;
                color: #333333;
            }
            QCalendarWidget QAbstractItemView:enabled {
                color: #333333;
                background-color: white;
                selection-background-color: #0078D7;
                selection-color: white;
            }
            QCalendarWidget QAbstractItemView:disabled {
                color: #999999;
            }
            QDateTimeEdit::down-button, QDateTimeEdit::up-button {
                background-color: #F0F0F0;
                border: 1px solid #C0C0C0;
            }
            QLineEdit::placeholder, QTextEdit::placeholder {
                color: #999999;
            }
            QTextEdit {
                background-color: white;
            }
            /* Ensure pasted text maintains the proper colors */
            QTextEdit#description {
                background-color: white;
                color: #333333;
            }
        """)

        window = EventInputWindow()
        window.show()

        sys.exit(app.exec())

    except Exception as e:
        QMessageBox.critical(None, "Critical Error", f"Application failed to start:\n{str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
