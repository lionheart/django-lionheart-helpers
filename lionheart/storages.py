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


