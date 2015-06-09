import re
from django import forms

po_box_format = re.compile(r'p\.? *o\.? .+\d+', re.IGNORECASE)
zip_format = re.compile(r'^\d{5}$')
zip_plus_four_format = re.compile(r'^\d{5}-\d{4}$')

def zip_code_validator(value):
    if not zip_format.match(value) \
            and not zip_plus_four_format.match(value):
        raise forms.ValidationError("Zip code is improperly formatted.")

    return value

def validate_zip_code_and_clean(value):
    value = value.strip()

    if not zip_format.match(value) \
            and not zip_plus_four_format.match(value):
        raise forms.ValidationError("Zip code is improperly formatted.")

    return value

def phone_validator(value):
    non_numbers = re.compile(r'[^\d]')
    value = non_numbers.sub('', value)

    if not 9 < len(value) < 16:
        message = "Phone number must be between 10 to 15 digits."
        raise forms.ValidationError(message)

    return value

def po_box_validator(value, message):
    """
    Matches the following strings:

    * PO Box 1234
    * P.O. Box 1234
    * P.O Box 1234
    * Po 1234
    * po 1234
    """

    if po_box_format.search(value):
        raise forms.ValidationError(message)

