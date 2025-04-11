from datetime import datetime, timezone
from typing import Any, List, Tuple, Union
import re

class HelperFunctions():
    """
    A utility class containing static methods for common validation and
    conversion operations used throughout the chemical inventory system.

    Includes logic for checking field and value presence, type validation, 
    list membership, and conversion of date strings to UTC datetime objects.

    Class Attributes:
        ISO_8601_WITH_OFFSET_REGEX (str): Regex pattern for validating
        ISO 8601 datetime strings with time zone offset.
    """
    ISO_8601_WITH_OFFSET_REGEX = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?([+-]\d{2}:\d{2}|Z)$"
    
    @staticmethod
    def get_schema_keys(dictionary: dict[str, Any]) -> Tuple[List[str], int]:
        """
        Extracts all keys from a dicionary with nested dictionary or list-of-dict 
        structures. Ignores the "Amount" list of types in the schema definitions.

        Primarily used to validate incoming JSON against required keys in complex schemas.

        Parameters:
            dictionary (dict[str, Any]): A schema dictionary (e.g. chemical or lot) either from the
            schema definitions or from an incoming request.

        Returns:
            Tuple[List[str], int]: A list of all key paths, and the count of repeated list elements
            (used to anticipate multiple component entries in prepared lot validation).
        """

        keys = []
        num_list_dict_elements = 0

        for key, value in dictionary.items():
            if isinstance(value, dict):
                # Adds "Purchased_Fields"/"Prepared_Fields" key and their subkeys then
                # parses subkeys
                keys.append(key)
                for subkey in value:
                    keys.append(f"{key}.{subkey}")
            elif isinstance(value, list):
                keys.append(key)
                for element in value:
                    if not isinstance(element, dict):
                        # Do nothing else if it's an "Amount" schema key as this list in the
                        # schema only stores acceptable value types.
                        break
                    else:
                        # Adds "Components" as a key then parses subkeys for each component
                        num_list_dict_elements += 1
                        for subkey in element:
                            keys.append(f"{key}.{subkey}")
            else:
                keys.append(key)
        
        return keys, num_list_dict_elements
    
    @staticmethod
    def to_datetime_utc(alleged_iso_8601_string: Union[str, datetime]) -> datetime:
        """
        Converts an ISO 8601 string (with timezone offset) or datetime object into UTC 
        datetime.

        Parameters:
            alleged_iso_8601_string (Union[str, datetime]):
                An ISO 8601 string with a time zone offset or a datetime object.

        Returns:
            datetime: A timezone-aware datetime in UTC.

        Raises:
            ValueError: If input is a string and does not match ISO 8601 format.
        """

        if isinstance(alleged_iso_8601_string, datetime):
            # Method called again when building records; after str->datetime in validation
            utc_dt = alleged_iso_8601_string
        elif isinstance(alleged_iso_8601_string, str):
            if not re.match(
                HelperFunctions.ISO_8601_WITH_OFFSET_REGEX,
                alleged_iso_8601_string
            ):
                raise ValueError("Date string must be ISO 8601 with time offset.")
            else:
                dt = datetime.fromisoformat(alleged_iso_8601_string)
                utc_dt = dt.astimezone(timezone.utc)

        return utc_dt
    
    @staticmethod
    def miss_req_field(key: str, keys: List[str]) -> bool:
        """
        Checks whether a required field is missing.

        Parameters:
            key (str): Schema field to search for.
            keys (List[str]): List of keys in the incoming request.

        Returns:
            bool: True if the key is missing, False otherwise.
        """
        
        missing_field = not key in keys
        return missing_field
    
    @staticmethod
    def miss_req_value(value: Any) -> bool:
        """
        Determines whether a value is missing or falsy. Only call for fields 
        that require a value; the method itself does not know whether a field
        is required.

        Parameters:
            value (Any): The value to check.

        Returns:
            bool: True if the value is falsy, False otherwise.
        """
        
        missing_value = not value
        return missing_value
    
    @staticmethod
    def wrong_type(value: Any, expected_type: Union[type, List[type], Any]) -> bool:
        """
        Checks whether the value is of the expected type(s).

        Parameters:
            value (Any): The value to check.
            expected_type (Union[type, List[type], Any]): Either a single type,
                list of types (e.g. [int, float]), or a reference value of the correct type.

        Returns:
            bool: True if the type is incorrect, False otherwise.
        """

        if isinstance(expected_type, type):
            # Most common condition: Receive value and type
            wrong_type = not isinstance(value, expected_type)
        elif isinstance(expected_type, list):
            # If receiving a list of types as for the "Amount" field
            if not type(expected_type[0]) == type:
                # Some schema define a value as being a list of objects (e.g. 
                # "Components"). The field itself containing a list value 
                # must have the type of its value checked. This case is here 
                # distinguished from fields like "Amount" whose value is 
                # itself a list of values.
                # 
                # Accounts for empty lists (edge case).
                wrong_type = not type(value) == type(expected_type)
            else:
                # If receiving a list of acceptable types from a schema
                wrong_type = not type(value) in expected_type
        else:
            # If receiving two values whose types must match
            wrong_type = not isinstance(value, type(expected_type))

        return wrong_type
    
    @staticmethod
    def inval_list_entry(val: Any, validated_list: List[Any]) -> bool:
        """
        Checks whether a value is not present in a validated list.

        Parameters:
            val (Any): The value to check.
            validated_list (List[Any]): A list of acceptable values.

        Returns:
            bool: True if value is not found in list, False otherwise.
        """
        
        not_in_list = not val in validated_list
        return not_in_list