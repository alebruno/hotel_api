""" Functions to extract information from text."""

import dateparser
import datetime
from text_to_num import alpha2digit
import spacy
import re
from actions.city_aliases import berlin_in_many_languages, munich_in_many_languages, stuttgart_in_many_languages

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")


def search_email(input_text: str) -> str:
    """Searches the email in a string of text using a regex compliant with the HTML5 specification.

    Args:
        input_text (str): The string of text

    Returns:
        str: The email address if exactly one email address has been found, None otherwise.
    """
    # Adapted from HTML5 specification. See https://html.spec.whatwg.org/#email-state-(type=email)
    # Initial ^ and final $ have been removed to match any email address embedded in a larger string.
    email_validation_regexp = r"[a-zA-Z0-9.!#$%&'*+\/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*"
    results = re.findall(email_validation_regexp, input_text)
    if len(results) == 1:
        return results[0]
    return None


def search_date(input_text: str) -> datetime.date:
    """Searches a date in the string of text.

    Args:
        input_text (str): The string of text

    Returns:
        datetime.date: The found date if exactly one date has been reliably found, None otherwise.
    """
    datetime_parser = lambda text: dateparser.parse(
        text, settings={"DATE_ORDER": "DMY", "PREFER_DATES_FROM": "future", "REQUIRE_PARTS": ["day", "month"]}
    )
    # Try to parse the text directly
    parse_result = datetime_parser(input_text)
    if parse_result is not None:
        return parse_result.date()
    # First fallback: convert substrings to digits, then try to parse the string again.
    input_text_with_digits = alpha2digit(input_text, "en")
    parse_result = datetime_parser(input_text_with_digits)
    if parse_result is not None:
        return parse_result.date()
    # Second fallback: remove elements that don't belong to the date using spaCy.
    doc = nlp(input_text_with_digits)
    filtered_text_chunks = [ent.text for ent in doc.ents if ent.label_ in ["DATE", "ORDINAL", "CARDINAL"]]
    filted_text_with_digits = "".join(filtered_text_chunks)
    parse_result = datetime_parser(filted_text_with_digits)
    if parse_result is not None:
        return parse_result.date()
    return None


def convert_date_to_string(input_date: datetime.date) -> str:
    """Converts a date to a string.

    Args:
        input_date (datetime.date): The date or None.

    Returns:
        str: The date as a string.
    """
    if input_date is not None:
        return input_date.strftime("%A %d. %B %Y")
    return None


def search_single_digit_number(input_text: str) -> str:
    """Searches a single digit number in the text.
       It is assumed that the chatbot is not required to handle bookings for more than 9 people.

    Args:
        input_text (str): The string of text.

    Returns:
        str: The number as a string with a single character if exactly one number has been found, None otherwise.
    """
    text_with_digits = alpha2digit(input_text, "en")
    digits = re.sub(r"\D", "", text_with_digits)
    if len(digits) == 1:
        return digits[0]
    else:
        return None

munich_in_many_languages_lowercase = [name.lower() for name in munich_in_many_languages]
stuttgart_in_many_languages_lowercase = [name.lower() for name in stuttgart_in_many_languages]
berlin_in_many_languages_lowercase = [name.lower() for name in berlin_in_many_languages]


def search_city(input_text: str) -> str:
    """Search the name of a city in the given text.

    Args:
        input_text (str): The text.

    Returns:
        str: The string uniquely identifying a city if exactly one city has been found, None otherwise.
    """
    input_text_lowercase = input_text.lower()

    munich_detected = any(name in input_text_lowercase for name in munich_in_many_languages_lowercase)
    stuttgart_detected = any(name in input_text_lowercase for name in stuttgart_in_many_languages_lowercase)
    berlin_detected = any(name in input_text_lowercase for name in berlin_in_many_languages_lowercase)

    number_of_detected_known_cities = sum([munich_detected, stuttgart_detected, berlin_detected])

    if number_of_detected_known_cities == 1:
        if munich_detected:
            return "Munich"
        if stuttgart_detected:
            return "Stuttgart"
        if berlin_detected:
            return "Berlin"
    return None
