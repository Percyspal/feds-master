import json
import datetime
from feds.settings import FEDS_NOTIONAL_FIELD_TYPES


def is_legal_json(to_check):
    """ Ckeck whether object is legal JSON. """
    try:
        json_object = json.loads(to_check)
    except ValueError:
        return False
    return True


def json_string_to_dict(str_to_process):
    """
    Convert a string with JSON to a dictionary.
    :param str_to_process: The string.
    :return: The dictionary.
    """
    if not isinstance(str_to_process, str):
        message = 'json_string_to_dict: Not string: {thing}'
        raise TypeError(message.format(thing=str_to_process))
    if str_to_process == '':
        str_to_process = '{}'
    if not is_legal_json(str_to_process):
        message = 'json_string_to_dict: Not JSON: {thing}'
        raise TypeError(message.format(thing=str_to_process))
    return json.loads(str_to_process)



def stringify_json(to_check):
    """
    Change dict to string for storage.
    :param to_check: Thing to check
    :return: Stringified dict.
    """
    if isinstance(to_check, dict):
        to_check = json.dumps(to_check)
    elif to_check == '':
        to_check = '{}'
    return to_check


def check_field_type_known(field_type_in):
    """
    Check whether field type is known.
    :param field_type_in: Field type to check.
    :return: True if known, false if not.
    """
    for type_label, type_desc in FEDS_NOTIONAL_FIELD_TYPES:
        if type_label == field_type_in:
            return True
    return False


def stringify_date(date_to_format):
    """
    Return a string representation of a date.
    :param date_to_format: The date object.
    :return: String rep.
    """
    if isinstance(date_to_format, datetime.date):
        result = date_to_format.strftime('%Y/%m/%d')
        return result
    return date_to_format
