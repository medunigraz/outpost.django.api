from drf_haystack.filters import HaystackAutocompleteFilter
from drf_haystack.viewsets import HaystackViewSet
from outpost.django.campusonline import models as campusonline
from outpost.django.geo import models as geo
from outpost.django.structure import models as structure
from rest_framework.permissions import AllowAny
from xapian_backend import NGRAM_MAX_LENGTH

from . import serializers


class LimitingHaystackAutocompleteFilter(HaystackAutocompleteFilter):
    """
    Filter class that truncates all search query tokens to NGRAM_MAX_LENGTH
    chars.
    """

    @staticmethod
    def get_request_filters(request):
        data = request.query_params.copy()
        if "q" in data:
            data["q"] = " ".join([t[:NGRAM_MAX_LENGTH] for t in data["q"].split()])
        return data


class AutocompleteViewSet(HaystackViewSet):
    """
    Get autocomplete suggestions for geographic objects:

        .../?q=<Word>

    To limit results to certain models use the `m` parameter:

        .../?q=<Word>&m=<Model>,<Model>,...

    Possible models are currently:

     * `campusonline.Person`
     * `campusonline.Room`
     * `geo.Room`
     * `structure.Organization`
     * `structure.Person`

    The `ctype` property determines the content type of each suggested item.
    This can be used to do further queries at other endpoints.
    """

    serializer_class = serializers.AutocompleteSerializer
    index_models = (
        geo.Room,
        structure.Organization,
        structure.Person,
        campusonline.Person,
        campusonline.Room,
    )
    authenticated_index_models = (campusonline.Student,)
    permission_classes = (AllowAny,)
    filter_backends = (LimitingHaystackAutocompleteFilter,)

    def get_queryset(self, index_models=[]):
        queryset = self.object_class()._clone()
        if "m" in self.request.GET:
            requested = self.request.GET.get("m").split(",")
            # Filter all requested index models and check if they require
            # authentication
            models = list(
                filter(lambda m: m._meta.label in requested, self.index_models)
            ) + list(
                filter(
                    lambda m: self.request.user.is_authenticated
                    and m._meta.label in requested,
                    self.authenticated_index_models,
                )
            )
            if models:
                return queryset.models(*models)
            else:
                # No index models were allowed, so return empty result.
                return queryset.none()

        # Only return public index models if none were requested.
        return queryset.models(*self.index_models)
