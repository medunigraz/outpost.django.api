import re
from base64 import (
    b64decode,
    urlsafe_b64encode,
)
from pathlib import PurePosixPath
from uuid import uuid4

import six
from django.core.files.base import ContentFile
from drf_haystack.serializers import HaystackSerializer
from outpost.django.campusonline import search_indexes as campusonline
from outpost.django.geo import search_indexes as geo
from outpost.django.structure import search_indexes as structure
from rest_framework.serializers import (
    FileField,
    IntegerField,
    SerializerMethodField,
)


class AutocompleteSerializer(HaystackSerializer):
    id = IntegerField(source="pk")
    ctype = SerializerMethodField()

    class Meta:
        index_classes = [
            campusonline.RoomIndex,
            campusonline.PersonIndex,
            campusonline.StudentIndex,
            geo.RoomIndex,
            structure.OrganizationIndex,
            structure.PersonIndex,
        ]
        fields = ["presentation", "id", "ctype", "level_id", "room_id", "autocomplete"]
        ignore_fields = ["text", "autocomplete"]
        field_aliases = {"q": "autocomplete"}

    def get_ctype(self, obj):
        return obj.content_type()


class Base64FileField(FileField):
    """
    A Django REST framework field for handling file-uploads through raw post
    data.  It uses base64 for encoding and decoding the contents of the file.

    Heavily based on
    https://stackoverflow.com/a/28036805
    """

    parser = re.compile(r"^data:(?P<mimetype>.*?);base64,")

    def to_internal_value(self, raw):

        # Check if this is a base64 string
        if isinstance(raw, six.string_types):
            header = self.parser.match(raw)
            # Check if the base64 string is in the "data:" format
            if header:
                try:
                    decoded_file = b64decode(self.parser.sub("", raw))
                except TypeError:
                    self.fail("invalid_image")

                # Generate file name:
                p = PurePosixPath()
                uid = uuid4().bytes
                u = urlsafe_b64encode(uid).decode("ascii").rstrip("=")

                filename = p.joinpath(u).as_posix()

                raw = ContentFile(decoded_file, name=filename)

        return super(Base64FileField, self).to_internal_value(raw)
