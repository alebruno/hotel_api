""" Rasa Action definitions """

from typing import Text, List, Any, Dict
import datetime

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import AllSlotsReset

from actions.nlp_pipelines import (
    search_email,
    search_date,
    search_single_digit_number,
    search_city,
    convert_date_to_string,
)

SPECIAL_CHARACTERS = r"""!@#$"%^&*()-+?_=,<>/"""


def contains_numbers(input_string):
    """Check if a string contains numbers.

    Args:
        input_string (Text): Text to be processed.

    Returns:
        bool: True if the string contains at least one number, false otherwise.
    """
    return any(character.isdigit() for character in input_string)


def contains_symbols(input_string):
    """Check if a string contains special characters.

    Args:
        input_string (Text): Text to be processed.

    Returns:
        bool: True if the string contains at least one special character, false otherwise.
    """
    return any(c in SPECIAL_CHARACTERS for c in input_string)


def validate_name(dispatcher: CollectingDispatcher, name: Text, description: Text) -> Text:
    """Validate a name using simple checks.

    Args:
        dispatcher (CollectingDispatcher): Rasa dispatcher
        name (Text): The text containing the name
        description (Type): Adjective describing the name, for example First or Last.

    Returns:
        Text: The given text if the name is plausible, None otherwise.
    """
    if len(name) <= 1:
        dispatcher.utter_message(text=description + " shall be at least two letter long.")
        return None
    if contains_numbers(name):
        dispatcher.utter_message(text=description + " shall not contain numbers.")
        return None
    if contains_symbols(name):
        dispatcher.utter_message(
            text=description + " shall not contain any of the following symbols: " + SPECIAL_CHARACTERS
        )
        return None
    return name


class ValidateReservationForm(FormValidationAction):
    def name(self) -> Text:
        """Get name of action to validate the reservation form.

        Returns:
            Text: Name of the action.
        """
        return "validate_reservation_form"

    def validate_first_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validates the first name and returns the request to save it to the appropriate slot.

        Args:
            slot_value (Text): Text entered by the user
            dispatcher (CollectingDispatcher): Rasa dispatcher
            tracker (Tracker): Rasa tracker
            domain (DomainDict): Domain of the chatbot

        Returns:
            Dict[Text, Any]: The request to update the first_name slot with the extracted first name or with 
            None if the given name is not plausible.
        """
        return {"first_name": validate_name(dispatcher=dispatcher, name=slot_value, description="First name")}

    def validate_last_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validates the last name and returns the request to save it to the appropriate slot.

        Args:
            slot_value (Text): Text entered by the user
            dispatcher (CollectingDispatcher): Rasa dispatcher
            tracker (Tracker): Rasa tracker
            domain (DomainDict): Domain of the chatbot

        Returns:
            Dict[Text, Any]: The request to update the last_name slot with the extracted last name or with None
            if the given name is not plausible.
        """
        return {"last_name": validate_name(dispatcher=dispatcher, name=slot_value, description="Last name")}

    def validate_number_of_guests(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Extracts the number of guests and returns the request to save it to the appropriate slot.

        Args:
            slot_value (Text): Text entered by the user
            dispatcher (CollectingDispatcher): Rasa dispatcher
            tracker (Tracker): Rasa tracker
            domain (DomainDict): Domain of the chatbot

        Returns:
            Dict[Text, Any]: The request to update the number_of_guests slot with the extracted number of guests 
            or with None if the extraction failed or if the extracted number is not plausible.
        """
        extracted_number = search_single_digit_number(slot_value)
        if extracted_number is None:
            dispatcher.utter_message(text="I could not understand now many.")
            return {"number_of_guests": None}
        return {"number_of_guests": extracted_number}

    def validate_arrival_date(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Extracts the arrival date and returns the request to save it to the appropriate slot.

        Args:
            slot_value (Text): Text entered by the user
            dispatcher (CollectingDispatcher): Rasa dispatcher
            tracker (Tracker): Rasa tracker
            domain (DomainDict): Domain of the chatbot

        Returns:
            Dict[Text, Any]: The request to update the arrival_date slot with the extracted arrival date or with None 
            if the extraction failed or if the extracted date is not plausible.
        """
        extracted_date = search_date(slot_value)
        if extracted_date is None:
            dispatcher.utter_message(text="I could not understand the date.")
            return {"arrival_date": None}
        if extracted_date < datetime.date.today():
            dispatcher.utter_message(text="Arrival date shall be in the future.")
            return {"arrival_date": None}
        self.arrival_date = extracted_date
        return {"arrival_date": convert_date_to_string(extracted_date)}

    def validate_departure_date(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Extracts the departure date and returns the request to save it to the appropriate slot.

        Args:
            slot_value (Text): Text entered by the user
            dispatcher (CollectingDispatcher): Rasa dispatcher
            tracker (Tracker): Rasa tracker
            domain (DomainDict): Domain of the chatbot

        Returns:
            Dict[Text, Any]: The request to update the departure_date slot with the extracted departure date or with 
            None if the extraction failed or if the extracted date is not plausible.
        """
        extracted_date = search_date(slot_value)
        if extracted_date is None:
            dispatcher.utter_message(text="I could not understand the date.")
            return {"departure_date": None}
        if extracted_date < datetime.date.today():
            dispatcher.utter_message(text="Departure date shall be in the future.")
            return {"departure_date": None}
        # Arrival date shall be asked by the rasa form before the departure date.
        assert self.arrival_date is not None
        if self.arrival_date >= extracted_date:
            dispatcher.utter_message(text="Departure shall be at least one day after the arrival.")
            return {"departure_date": None}
        # Validation of departure date done. Arrival date can be reset:
        self.arrival_date = None
        return {"departure_date": convert_date_to_string(extracted_date)}

    def validate_email(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Extracts the email and returns the request to save it to the appropriate slot.

        Args:
            slot_value (Text): Text entered by the user
            dispatcher (CollectingDispatcher): Rasa dispatcher
            tracker (Tracker): Rasa tracker
            domain (DomainDict): Domain of the chatbot

        Returns:
            Dict[Text, Any]: The request to update the email slot with the extracted email or with None if the 
            extraction failed.
        """
        email = search_email(slot_value)
        if email is None:
            dispatcher.utter_message(text="I could not understand the email.")
            return {"email": None}
        return {"email": email}

    def validate_city(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Extracts the name of the city and returns the request to save it to the appropriate slot.

        Args:
            slot_value (Text): Text entered by the user
            dispatcher (CollectingDispatcher): Rasa dispatcher
            tracker (Tracker): Rasa tracker
            domain (DomainDict): Domain of the chatbot

        Returns:
            Dict[Text, Any]: The request to update the city slot with the extracted name or with None if the
            extraction failed.
        """
        city = search_city(slot_value)
        if city is None:
            dispatcher.utter_message(text="I did not understand in which city.")
            return {"city": None}
        return {"city": city}


class ActionClearSlots(Action):
    """Class defining the action to clear the slots."""

    def name(self) -> Text:
        """Get name of action to clear the slots.
        Returns:
            Text: Name of the action.
        """
        return "action_clear_slots"

    async def run(self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """It returns the request to reset of all the slots.

        Args:
            dispatcher (CollectingDispatcher): Rasa dispatcher
            tracker (Tracker): Rasa tracker
            domain (Dict[Text, Any]): Domain of the chatbot

        Returns:
            List[Dict[Text, Any]]: The request to reset all slots.
        """
        return [AllSlotsReset()]
