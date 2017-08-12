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

import StringIO
import base64
import mimetypes

from django.core.files import File
from django.core.files.storage import Storage

from lionheart.models import UploadedFile

class Base64DatabaseStorage(Storage):
    """
    Class DatabaseStorage provides storing files in the database.
    """

    def _open(self, name, mode='rb'):
        assert mode == 'rb', "You've tried to open binary file without specifying binary mode! You specified: %s" % mode

        obj = UploadedFile.objects.get(filename=name)
        file = StringIO.StringIO(base64.b64decode(obj.blob))
        file.name = name
        file.mode = mode
        return File(file)

    def _save(self, name, content):
        name = name.replace('\\', '/')
        binary = content.read()
        encoded = base64.b64encode(binary)
        size = len(binary)

        UploadedFile.objects.get_or_create(filename=name, defaults={
            'blob': encoded,
            'size': size })
        return name

    def get_available_name(self, name):
        return name

    def delete(self, name):
        UploadedFile.objects.filter(filename=name).delete()

    def url(self, name):
        uploaded_file = UploadedFile.objects.get(filename=name)
        mtype, encoding = mimetypes.guess_type(name)
        return "data:{0};base64,{1}".format(mtype, uploaded_file.blob)

    def size(self, name):
        uploaded_file = UploadedFile.objects.get(filename=name)
        return uploaded_file.size


