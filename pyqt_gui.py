"""An experimental GUI to make filling out the data easier."""

from __future__ import annotations

import sys
from dataclasses import dataclass

import asyncio
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QGridLayout,
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QPushButton,
    QLineEdit,
    QTextEdit,
    QMessageBox,
    QLabel,
    QCalendarWidget,
    QHBoxLayout,
    QDateEdit,
    QComboBox,
)
from PyQt6.QtCore import QDateTime, QTime, QDate
from PyQt6.QtWidgets import QTimeEdit, QMenu


from kuda_idem_template import Event, send_html_message


@dataclass(slots=True)
class VenueInfo:
    name: str
    city: str
    address: str
    map_link: str
    ticket_link: str


VENUES: dict[str, VenueInfo] = {
    "Арт-центр WORM": VenueInfo(
        name="Арт-центр WORM",
        city="Роттердам",
        address="Boomgaardsstraat 71",
        map_link="https://maps.app.goo.gl/3S5DKJii2WiJoN2p6",
        ticket_link="https://worm.stager.co/web/tickets",
    ),
    "Клуб BASIS": VenueInfo(
        name="Клуб BASIS",
        city="Утрехт",
        address="Oudegracht aan de Werf 97",
        map_link="https://maps.app.goo.gl/ziunBp7tArEiSWwa7",
        ticket_link="https://clubbasis.nl/tickets/",
    ),
    "Клуб Bret": VenueInfo(
        name="Клуб Bret",
        city="Амстердам",
        address="Orlyplein 76",
        map_link="https://maps.app.goo.gl/32r9j3DEqsfmYyXE6",
        ticket_link="https://www.bret.bar/ticketshop",
    ),
    "De Hemkade": VenueInfo(
        name="De Hemkade",
        city="Зандаам",
        address="Hemkade 48",
        map_link="https://maps.app.goo.gl/X6X6vHUurbpxZ8et5emkade",
        ticket_link="https://hemkade48.nl/agenda/?e-filter-c5ded3a-event_month=november",
    ),
    "Клуб Der Hintergarten": VenueInfo(
        name="Клуб Der Hintergarten",
        city="Амстердам",
        address="Overschiestraat 188",
        map_link="https://maps.app.goo.gl/rkS97gU2YMNePri39",
        ticket_link="https://www.derhintergarten.nl/events",
    ),
    "Клуб Garage Klub": VenueInfo(
        name="Клуб Garage Klub",
        city="Антверп",
        address="Noorderlaan 72",
        map_link="https://maps.app.goo.gl/t7utfBmoJwtNtBif7",
        ticket_link="https://agenda.paylogic.com/4e407aa066b044e3a9039771a583e896",
    ),
    "Клуб Garage Noord": VenueInfo(
        name="Клуб Garage Noord",
        city="Амстердам",
        address="Gedempt hamerkanaal 40",
        map_link="https://maps.app.goo.gl/HCnFgNhzYbswLicb6",
        ticket_link="https://www.garagenoord.com/club",
    ),
    "Клуб KABUL à GoGo": VenueInfo(
        name="Клуб KABUL à GoGo",
        city="Утрехт",
        address="Gietijzerstraat 3",
        map_link="https://maps.app.goo.gl/wzNTDZ5ZSasMEfM9A",
        ticket_link="https://www.kabulagogo.nl/tickets",
    ),
    "Клуб Laak": VenueInfo(
        name="Клуб Laak",
        city="Гаага",
        address="Theodor Stangstraat 1",
        map_link="https://maps.app.goo.gl/fFN71thiVRMKKDgE6",
        ticket_link="https://laak.stager.co/web/tickets",
    ),
    "Клуб Levenslang": VenueInfo(
        name="Клуб Levenslang",
        city="Амстердам",
        address="H.J.E. Wenckebachweg 48",
        map_link="https://maps.app.goo.gl/JsjmPJ6E4Fv5Lnrh7",
        ticket_link="https://www.levenslang.amsterdam/en/program",
    ),
    "Клуб Lofi": VenueInfo(
        name="Клуб Lofi",
        city="Амстердам",
        address="Basisweg 63",
        map_link="https://maps.app.goo.gl/tmrvEycPcNe1fzQp9",
        ticket_link="https://shop.eventix.io/54a986f2-a7ca-46e4-9b0b-9b49f0e4c92a/events",
    ),
    "Клуб Now & Wow": VenueInfo(
        name="Клуб Now & Wow",
        city="Роттердам",
        address="Maashaven Zuidzijde 1-2",
        map_link="https://maps.app.goo.gl/D6RQg1CJbVVTTGnK8",
        ticket_link="https://www.maassilo.com/agenda/",
    ),
    "Клуб Pip": VenueInfo(
        name="Клуб Pip",
        city="Гаага",
        address="Binckhorstlaan 36",
        map_link="https://maps.app.goo.gl/RHnMwDPaaoxaaEda6",
        ticket_link="https://pipdenhaag.stager.co/web/tickets",
    ),
    "Клуб RADION": VenueInfo(
        name="Клуб RADION",
        city="Амстердам",
        address="Louwesweg 1",
        map_link="https://maps.app.goo.gl/BCp1L74yxzfP2zMm7",
        ticket_link="https://radionamsterdam.stager.co/web/tickets",
    ),
    "Клуб RAUM": VenueInfo(
        name="Клуб RAUM",
        city="Амстердам",
        address="Humberweg 3",
        map_link="https://maps.app.goo.gl/2W543xaXH1gpkrLW8",
        ticket_link="https://www.clubraum.nl/calendar",
    ),
    "Клуб Shelter": VenueInfo(
        name="Клуб Shelter",
        city="Амстердам",
        address="Overhoeksplein 3",
        map_link="https://maps.app.goo.gl/dRFnNgxbkgg8khb99",
        ticket_link="https://shop.eventix.io/bca0fb30-5c63-11e9-af17-65a0f4e2b9f9/events",
    ),
    "Клуб Thuishaven": VenueInfo(
        name="Клуб Thuishaven",
        city="Амстердам",
        address="Contactweg 68",
        map_link="https://maps.app.goo.gl/6xjwgY6zeZZ9Rr817",
        ticket_link="https://thuishaven.nl/#agenda",
    ),
    "Клуб Tilla Tec": VenueInfo(
        name="Клуб Tilla Tec",
        city="Амстердам",
        address="Jan van Bremenstraat 1",
        map_link="https://maps.app.goo.gl/j7HeC94gQPTxXua99",
        ticket_link="https://shop.eventix.io/0e536f93-e4fd-11ee-a9cb-7e126431635e/tickets?shop_code=7mv39gsy",
    ),
    "Клуб Toffler": VenueInfo(
        name="Клуб Toffler",
        city="Роттердам",
        address="Weena-Zuid 33",
        map_link="https://maps.app.goo.gl/itnMGHdAnUhvCY8L7",
        ticket_link="https://www.toffler.nl/",
    ),
    "Клуб Warehouse Elementenstraat": VenueInfo(
        name="Клуб Warehouse Elementenstraat",
        city="Амстердам",
        address="Elementenstraat 25",
        map_link="https://maps.app.goo.gl/61jmWzg7v5Z7ZNFU7",
        ticket_link="https://ra.co/clubs/69321/events",
    ),
    "Клуб WAS.": VenueInfo(
        name="Клуб WAS.",
        city="Утрехт",
        address="Tractieweg 41",
        map_link="https://maps.app.goo.gl/q7nJR3q7Rf7vqcXg8",
        ticket_link="https://www.was030.nl/tickets/",
    ),
}


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


class TimeSelectMenu(QMenu):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #C0C0C0;
                padding: 5px;
            }
            QPushButton {
                background-color: #F5F5F5;
                border: 1px solid #C0C0C0;
                border-radius: 3px;
                padding: 5px;
                text-align: center;
                min-width: 60px;
                color: #333333;
            }
            QPushButton:hover {
                background-color: #0078D7;
                color: white;
                border: 1px solid #0078D7;
            }
        """)

        # Create a grid of hours
        layout = QGridLayout()
        layout.setSpacing(5)  # Add some spacing between buttons
        self.setLayout(layout)

        # Add hours in a 6x4 grid
        for hour in range(24):
            row = hour // 4
            col = hour % 4
            hour_btn = QPushButton(f"{hour:02d}:00")
            hour_btn.clicked.connect(lambda checked, h=hour: self.hour_selected(h))
            layout.addWidget(hour_btn, row, col)

        # Set a fixed size for the menu
        self.setFixedSize(layout.sizeHint())

    def hour_selected(self, hour):
        self.parent().setTime(QTime(hour, 0))
        self.close()


class DateTimePickerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create Date edit with calendar popup
        self.date_edit = QDateEdit(self)
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())

        # Customize calendar
        calendar = QCalendarWidget(self)
        calendar.setGridVisible(True)
        calendar.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        calendar.setStyleSheet("""
            QCalendarWidget {
                background-color: white;
            }
            QCalendarWidget QTableView {
                background-color: white;
                selection-background-color: #0078D7;
                selection-color: white;
            }
        """)
        self.date_edit.setCalendarWidget(calendar)

        # Create Time edit with custom popup
        self.time_edit = QTimeEdit(self)
        self.time_edit.setDisplayFormat("HH:00")
        current = QTime.currentTime()
        self.time_edit.setTime(QTime(current.hour(), 0))

        # Create custom button for time selection
        self.time_button = QPushButton("🕒")
        self.time_button.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 1px solid #C0C0C0;
                border-radius: 3px;
                padding: 4px 8px;
            }
            QPushButton:hover {
                background-color: #F0F0F0;
            }
        """)
        self.time_button.clicked.connect(self.showTimeMenu)

        layout.addWidget(self.date_edit)
        layout.addWidget(self.time_edit)
        layout.addWidget(self.time_button)

    def showTimeMenu(self):
        menu = TimeSelectMenu(self.time_edit)
        pos = self.time_button.mapToGlobal(self.time_button.rect().bottomLeft())
        menu.popup(pos)

    def dateTime(self):
        return QDateTime(self.date_edit.date(), self.time_edit.time())

    def setDateTime(self, datetime):
        self.date_edit.setDate(datetime.date())
        # Ensure time is set to the nearest hour
        time = QTime(datetime.time().hour(), 0)
        self.time_edit.setTime(time)

    def setTime(self, time):
        self.time_edit.setTime(time)


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

        # Create the venue combo box with proper styling
        self.venue_combo = QComboBox()
        self.venue_combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                border: 1px solid #C0C0C0;
                border-radius: 3px;
                padding: 5px;
                color: #333333;  /* Dark text color */
            }
            QComboBox:hover {
                border: 1px solid #0078D7;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                border: 1px solid #C0C0C0;
                selection-background-color: #0078D7;
                selection-color: white;
                color: #333333;  /* Dark text color for dropdown items */
            }
        """)

        self.venue_combo.addItem("-- Select Venue --")
        # Add venues in alphabetical order
        for venue_name in sorted(VENUES.keys()):
            self.venue_combo.addItem(venue_name)

        self.venue_combo.currentTextChanged.connect(self.on_venue_selected)

        # Create horizontal layout for venue selection
        venue_layout = QHBoxLayout()
        venue_layout.addWidget(self.venue_combo)

        # Add clear button
        clear_venue_button = QPushButton("Clear")
        clear_venue_button.setStyleSheet("""
            QPushButton {
                background-color: #DC3545;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #C82333;
            }
        """)
        clear_venue_button.clicked.connect(self.clear_venue_selection)
        venue_layout.addWidget(clear_venue_button)

        # Add to form layout (using only one label)
        form_layout.addRow(RequiredLabel("Venue Selection", required=False), venue_layout)

    def clear_venue_selection(self):
        """Clear venue selection and related fields"""
        self.venue_combo.setCurrentIndex(0)
        self.venue_name.clear()
        self.city.clear()
        self.venue_address.clear()
        self.venue_map_link.clear()
        self.ticket_link.clear()

    def on_venue_selected(self, venue_name: str):
        """Handle venue selection"""
        if venue_name == "-- Select Venue --":
            return

        venue_info = VENUES.get(venue_name)
        if venue_info:
            self.venue_name.setText(venue_info.name)
            self.city.setText(venue_info.city)
            self.venue_address.setText(venue_info.address)
            self.venue_map_link.setText(venue_info.map_link)
            self.ticket_link.setText(venue_info.ticket_link)

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

        self.venue_combo.setCurrentIndex(0)  # Reset to "Select Venue"

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
            
            QComboBox {
                background-color: white;
                border: 1px solid #C0C0C0;
                border-radius: 3px;
                padding: 5px;
            }
            QComboBox:hover {
                border: 1px solid #0078D7;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(down_arrow.png);  # You'd need to provide this image
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                border: 1px solid #C0C0C0;
                selection-background-color: #0078D7;
                selection-color: white;
                outline: none;
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
