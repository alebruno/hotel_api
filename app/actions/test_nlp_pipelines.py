""" Tests of the functions to extract information from text."""

import datetime
from actions.nlp_pipelines import (
    search_email,
    search_date,
    search_single_digit_number,
    search_city,
    convert_date_to_string,
)


def test_search_email():
    """Tests the function search_email."""
    assert search_email("I don't remember my email.") is None
    assert search_email("Sorry I don't know wh@t my email adress is") is None
    assert search_email("My email is testmail@gmx.ch, thank you") == "testmail@gmx.ch"
    assert search_email("Of course!messy-writer@g-mail.us. That's my email.") == "messy-writer@g-mail.us"
    assert search_email("nice.user@hotmail.de") == "nice.user@hotmail.de"
    assert search_email(" space.loving.user@nasa.us   ") == "space.loving.user@nasa.us"
    assert search_email("I have two emails: maybe.this@gmail.com and maybe.this.other.one@gmx.de.") is None


def test_search_date():
    """Tests the function search_date."""
    assert search_date("On the 12.12.2025.") == datetime.date(day=12, month=12, year=2025)
    assert search_date("7th June 2025 please") == datetime.date(day=7, month=6, year=2025)
    assert search_date("I want to check out on the twenty-first of october 2026, thank you") == datetime.date(
        day=21, month=10, year=2026
    )
    assert search_date("Book it for today please.") == datetime.date.today()
    assert search_date("I want to order two icecreams") is None
    assert search_date("after the 27 february 2023 would be perfect") == datetime.date(day=27, month=2, year=2023)
    assert search_date("Maybe before the 14.5.2022 or after the 27th of February 2023, I don't know.") is None


def test_convert_date_to_string():
    """Tests the function date_to_string."""
    assert convert_date_to_string(datetime.date(day=20, month=7, year=1969)) == "Sunday 20. July 1969"


def test_search_single_digit_number():
    """Tests the function single_digit_number."""
    assert search_single_digit_number("There will be four guests") == "4"
    assert search_single_digit_number("1 guest") == "1"
    assert search_single_digit_number("Make a reservation for 21 people") is None
    assert search_single_digit_number("I have to ask my wife about the number of guests.") is None
    assert search_single_digit_number("five dudes") == "5"
    assert search_single_digit_number("for a family of four") == "4"
    assert search_single_digit_number("just the 2 of us") == "2"
    assert search_single_digit_number("eleven players") is None
    assert search_single_digit_number("between 5 and 6, I don't know") is None


def test_search_city():
    """Tests the function search_city."""
    assert search_city("In München please.") == "Munich"
    assert search_city("bErLiN! let's goooo!!!!!!") == "Berlin"
    assert search_city("I will visit my grandson in Stuttgart.") == "Stuttgart"
    assert search_city("No idea. Are the best car museums in Munich or in Stuttgart?") == None
    assert search_city("I don't know, can you suggest a nice city to visit?") == None
    assert search_city("I want to book a room in Frankfurt.") == None
    assert search_city("Bielefeld") == None
