"""This file contains custom modules"""

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.serializers.json import DjangoJSONEncoder


class KJMJsonEncoder(DjangoJSONEncoder):
    """Converting the file into JSONEncoded and returns value as string

    Methods
    --------
    default(self, o):
        Returns readable string file
    """

    def default(self, o):
        """Returns readable string file"""

        if isinstance(o, InMemoryUploadedFile):
            return o.read()
        return str(o)