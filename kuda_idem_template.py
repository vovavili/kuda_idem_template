"""Generate HTML code for 'Куда идём?' and send it via a Telegram bot."""

from __future__ import annotations

import datetime as dt
from collections.abc import Collection
from enum import Enum, auto
from typing import Annotated

import asyncio
from pydantic import BaseModel, HttpUrl, SecretStr, BeforeValidator, TypeAdapter
from pydantic_settings import BaseSettings, SettingsConfigDict
from jinja2 import Template

from telegram import Bot
from telegram.constants import ParseMode

http_url_adapter = TypeAdapter(HttpUrl)
Url = Annotated[str, BeforeValidator(lambda value: str(http_url_adapter.validate_python(value)))]

# Modify the start and the end day of the message to be something other than next Friday and
# next Sunday
START_DATE: dt.datetime | None = None
END_DATE: dt.datetime | None = None


class Action(Enum):
    """Pick whether write HTML to a file or send in to a Telegram group chat topic."""
    LOAD_TO_FILE = auto()
    SEND_MESSAGE = auto()


class Settings(BaseSettings):
    """
    Please make sure your .env contains the following variables:
    - BOT_TOKEN - an API token for your bot.
    - TOPIC_ID - an ID for your group chat topic.
    - GROUP_CHAT_ID - an ID for your group chat.
    """

    # Telegram bot configuration
    BOT_TOKEN: SecretStr
    TOPIC_ID: int
    GROUP_CHAT_ID: int

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.prod"),
        env_file_encoding="utf-8",
    )


class Event(BaseModel):
    """Represents an event with its details and location information.

    Attributes:
        city: City where the event takes place
        title: Name of the event
        title_link: Optional URL with more information about the event
        description: Optional description of the event
        start_datetime: When the event starts
        end_datetime: When the event ends
        venue_name: Name of the venue
        venue_address: Street address of the venue
        venue_map_link: URL to the venue's location on a map
        ticket_link: Optional URL where tickets can be purchased
        ticket_info: Optional information about tickets, defaults to "Билет не нужен."
    """
    city: str
    title: str
    title_link: Url | None = None
    description: str | None = None
    start_datetime: dt.datetime
    end_datetime: dt.datetime
    venue_name: str
    venue_address: str
    venue_map_link: Url
    ticket_link: Url | None = None
    ticket_info: str | None = "Билет не нужен."


def get_next_weekend_dates() -> tuple[dt.datetime, dt.datetime]:
    """Calculate the dates for next weekend (Friday to Sunday).

    Returns:
        tuple[dt.datetime, dt.datetime]: Start date (Friday) and end date (Sunday)
    """

    today = dt.datetime.now()
    friday = today + dt.timedelta((4 - today.weekday()) % 7)
    sunday = friday + dt.timedelta(days=2)
    return friday, sunday


def get_russian_weekday(date: dt.datetime) -> str:
    """Convert a datetime weekday to its Russian name.

    Args:
        date: The datetime to get the weekday name for

    Returns:
        str: Russian name of the weekday
    """
    # Russian weekday names
    russian_weekdays = {
        0: "понедельник",
        1: "вторник",
        2: "среда",
        3: "четверг",
        4: "пятница",
        5: "суббота",
        6: "воскресенье",
    }
    return russian_weekdays[date.weekday()]


def format_date_range(start_date: dt.datetime, end_date: dt.datetime) -> str:
    """Format a date range in Russian style (e.g., "1-3 января" or "30 декабря - 1 января").

    Args:
        start_date: Beginning of the date range
        end_date: End of the date range

    Returns:
        str: Formatted date range string in Russian
    """
    russian_months = {
        1: "января",
        2: "февраля",
        3: "марта",
        4: "апреля",
        5: "мая",
        6: "июня",
        7: "июля",
        8: "августа",
        9: "сентября",
        10: "октября",
        11: "ноября",
        12: "декабря",
    }

    start, end = start_date.strftime("%d").lstrip("0"), end_date.strftime("%d").lstrip("0")

    return (
        f"{start}-{end} {russian_months[start_date.month]}"
        if start_date.month == end_date.month
        else f"{start} {russian_months[start_date.month]} - {end} {russian_months[end_date.month]}"
    )


def generate_event_page(
    events: Collection[Event],
) -> str:
    """Generate HTML page from events using a Jinja2 template.

    Args:
        events: Collection of Event objects to include in the page

    Returns:
        str: Generated HTML content
    """
    if START_DATE is None or END_DATE is None:
        start_date, end_date = get_next_weekend_dates()
    else:
        start_date, end_date = START_DATE, END_DATE

    with open("template.j2", mode="r", encoding="utf-8") as f:
        template = Template(f.read())
    return template.render(
        events=events,
        date_range=format_date_range(start_date, end_date),
        get_russian_weekday=get_russian_weekday,
    )


async def send_html_message(events: Collection[Event]) -> None:
    """Send HTML message with events and create a poll in Telegram.

    Args:
        events: Collection of Event objects to include in the message
    """
    html_message = generate_event_page(events).replace('<meta charset="UTF-8">', "")
    settings = Settings()

    # Create bot instance
    bot = Bot(token=settings.BOT_TOKEN.get_secret_value())
    # Send message with HTML parsing
    await bot.send_message(
        chat_id=settings.GROUP_CHAT_ID,
        text=html_message,
        message_thread_id=settings.TOPIC_ID,
        parse_mode=ParseMode.HTML,
    )

    # Create poll options from event titles
    options = [event.title for event in events] + [
        "Иду в другое место",
        "Ещё не уверен/-а",
        "Никуда не иду",
    ]

    # Send poll
    await bot.send_poll(
        chat_id=settings.GROUP_CHAT_ID,
        message_thread_id=settings.TOPIC_ID,
        question="Куда идём на эти выходные?",
        options=options,
        is_anonymous=False,
        allows_multiple_answers=True,
    )


def main(action: Action) -> None:
    """Execute the main program logic.

    Args:
        action: Whether to write HTML to a file or send to Telegram
    """
    events = (
        Event(
            city="Амстердам",
            title="RAUM invites BASSIANI 🇬🇪",
            title_link="https://www.instagram.com/club.raum/p/DArEX2oIko8/?locale=nl",
            description="Лучший клуб СНГ прилетает в лучший клуб Амстердама. Такое я бы не пропускал!",
            start_datetime=dt.datetime(2024, 11, 22, 23, 0),
            end_datetime=dt.datetime(2024, 11, 23, 7, 0),
            venue_name="Клуб RAUM",
            venue_address="Humberweg 3",
            venue_map_link="https://maps.app.goo.gl/RfpFD8iWguaMHSEe8",
            ticket_link="https://shop.paylogic.com/ea94b94aa341470e96e4be2916ee397f/",
        ),
        Event(
            city="Амстердам",
            title="VAULT SESSIONS X VULGED // RØDHÅD ANL",
            title_link="https://www.instagram.com/p/DAl1dxaglZ5/?hl=en",
            start_datetime=dt.datetime(2024, 11, 22, 23, 0),
            end_datetime=dt.datetime(2024, 11, 23, 8, 0),
            venue_name="Клуб RADION",
            venue_address="Louwesweg 1",
            venue_map_link="https://maps.app.goo.gl/BCp1L74yxzfP2zMm7",
            ticket_link="https://shop.eventix.io/d56aad36-a0b7-4ded-80c7-5774f32d6857/tickets?shop_code=awjk4xvv/",
        ),
        Event(
            city="Роттердам",
            title="CODA Collective, Free Pop-up rave",
            title_link="https://www.instagram.com/p/DCXJbe4oqV0/",
            description="Бесплатная вечеринка в очень милом месте и с приятной атмосферой!",
            start_datetime=dt.datetime(2024, 11, 21, 22, 0),
            end_datetime=dt.datetime(2024, 11, 22, 2, 0),
            venue_name="Арт-центр WORM",
            venue_address="Boomgaardsstraat 71",
            venue_map_link="https://maps.app.goo.gl/3S5DKJii2WiJoN2p6",
        ),
    )

    match action:
        case Action.LOAD_TO_FILE:
            with open("events.html", mode="w", encoding="utf-8") as f:
                f.write(generate_event_page(events))
        case Action.SEND_MESSAGE:
            asyncio.run(send_html_message(events))


if __name__ == "__main__":
    main(Action.SEND_MESSAGE)
