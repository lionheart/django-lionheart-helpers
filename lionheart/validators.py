# Copyright 2015-2017 Lionheart Software LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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

