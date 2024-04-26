from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from rest_framework.compat import unicode_to_repr
from rest_framework.exceptions import ValidationError
from rest_framework.utils.representation import smart_repr


class EntryThrottleValidator(object):
    """"""

    def __init__(self, queryset, search, field, delta):
        self.queryset = queryset
        self.search = search
        self.field = field
        self.delta = delta

    def set_context(self, serializer):
        """
        This hook is called by the serializer instance,
        prior to the validation call being made.
        """
        # Determine the existing instance, if this is an update operation.
        self.instance = getattr(serializer, "instance", None)

    def __call__(self, attrs):
        if self.instance:
            return
        kwargs = {self.search: attrs.get(self.search)}
        try:
            latest = self.queryset.filter(**kwargs).latest(self.field)
            if getattr(latest, self.field) + self.delta > timezone.now():
                raise ValidationError(_("Requests coming in too fast"))
        except self.queryset.model.DoesNotExist:
            return

    def __repr__(self):
        return unicode_to_repr(
            "<%s(queryset=%s)>" % (self.__class__.__name__, smart_repr(self.queryset))
        )
