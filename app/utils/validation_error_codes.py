from typing import List, Tuple, Union

class ValidationErrorCodes():
    """
    Stores all custom validation error codes and corresponding error messages
    used throughout request validation.

    This class provides:
    - Integer codes to categorize validation errors for chemicals, lots, and lists.
    - Consistent static message strings for each error type.
    - A utility method to format error messages for API responses.

    Each constant and message has a one-to-one mapping. Messages are used
    when returning structured error responses to the front end or test suite.
    """
    
    # Request validation error codes
    MISS_REQ_FIELD = 1       # Required key not present
    WRONG_TYPE = 2           # Value is wrong type
    INVAL_LIST_ENTRY = 3     # Value does not exist in validated list
    UNEXP_FIELD = 4          # Unexpected field in request form
    CHEM_NOT_FOUND = 5       # Chemical not found in database
    WRONG_DATE_FORMAT = 6    # Date not in ISO 8601 format
    MISSING_COMP = 7         # All prepared chemicals require at least one component
    LOT_NOT_FOUND = 8        # Lot not found in database
    CHEM_DUPLICATE = 9       # Chemical already exists in database
    INVALID_ID = 10          # ID field is not a valid ObjectId()
    MISS_REQ_VALUE = 11      # Required field left blank in request
    LIST_DUPLICATE = 12      # List already exists in database
    LIST_NOT_FOUND = 13      # List not fond in database

    # Static portion of error messages
    MISS_REQ_FIELD_MSG = "Missing required field:"
    WRONG_TYPE_MSG = "Incorrect data type for field:"
    INVAL_LIST_ENTRY_MSG = "Invalid entry of correct data type for field:"
    UNEXP_FIELD_MSG = "Unexpected fields:"
    CHEM_NOT_FOUND_MSG = "Chemical _id not found in database:"
    WRONG_DATE_FORMAT_MSG = "Date string must be in ISO 8601 format:"
    MISSING_COMP_MSG = "Prepared lots require at least one component:"
    LOT_NOT_FOUND_MSG = "Lot _id not found in database:"
    CHEM_DUPLICATE_MSG = "Chemical already exists in database with primary key:"
    INVALID_ID_MSG = "_id cannot be converted to valid ObjectId:"
    MISS_REQ_VALUE_MSG = "Field missing required value:"
    LIST_DUPLICATE_MSG = "List already exists with name:"
    LIST_NOT_FOUND_MSG = "List not found in database with name:"

    @staticmethod
    def gen_val_err_msg(error_info: Tuple[Union[str, List[str]], int]) -> str:
        """
        Accepts a tuple containing:
        - error_info[0]: field or fields triggering the error (str or list[str])
        - error_info[1]: error code (int)

        Returns a formatted error message string based on the matching error code.
        These messages are served back to the client in 422 error responses.

        Example:
            error_info = ("Storage_Condition", 3)
            → "Invalid entry of correct data type for field: Storage_Condition"
        """

        match error_info[1]:
            case ValidationErrorCodes.MISS_REQ_FIELD:
                msg = f"{ValidationErrorCodes.MISS_REQ_FIELD_MSG} {error_info[0]}"
            case ValidationErrorCodes.WRONG_TYPE:
                msg = f"{ValidationErrorCodes.WRONG_TYPE_MSG} {error_info[0]}"
            case ValidationErrorCodes.INVAL_LIST_ENTRY:
                msg = f"{ValidationErrorCodes.INVAL_LIST_ENTRY_MSG} {error_info[0]}"
            case ValidationErrorCodes.UNEXP_FIELD:
                msg = f"{ValidationErrorCodes.UNEXP_FIELD_MSG} {error_info[0]}"
            case ValidationErrorCodes.CHEM_NOT_FOUND:
                msg = f"{ValidationErrorCodes.CHEM_NOT_FOUND_MSG} {error_info[0]}"
            case ValidationErrorCodes.WRONG_DATE_FORMAT:
                msg = f"{ValidationErrorCodes.WRONG_DATE_FORMAT_MSG} {error_info[0]}"
            case ValidationErrorCodes.MISSING_COMP:
                msg = f"{ValidationErrorCodes.MISSING_COMP_MSG} {error_info[0]}"
            case ValidationErrorCodes.LOT_NOT_FOUND:
                msg = f"{ValidationErrorCodes.LOT_NOT_FOUND_MSG} {error_info[0]}"
            case ValidationErrorCodes.CHEM_DUPLICATE:
                msg = f"{ValidationErrorCodes.CHEM_DUPLICATE_MSG} {error_info[0]}"
            case ValidationErrorCodes.INVALID_ID:
                msg = f"{ValidationErrorCodes.INVALID_ID_MSG} {error_info[0]}"
            case ValidationErrorCodes.MISS_REQ_VALUE:
                msg = f"{ValidationErrorCodes.MISS_REQ_VALUE_MSG} {error_info[0]}"
            case ValidationErrorCodes.LIST_DUPLICATE:
                msg = f"{ValidationErrorCodes.LIST_DUPLICATE_MSG} {error_info[0]}"
            case ValidationErrorCodes.LIST_NOT_FOUND:
                msg = f"{ValidationErrorCodes.LIST_NOT_FOUND_MSG} {error_info[0]}"
        return msg