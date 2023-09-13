from functools import partial

from django.contrib.auth.models import Permission
from rest_framework.metadata import SimpleMetadata
from rest_framework.test import APIRequestFactory


class ExtendedMetadata(SimpleMetadata):
    def determine_metadata(self, request, view):
        metadata = super().determine_metadata(request, view)
        if hasattr(view, "get_queryset"):
            model = view.get_queryset().model
            permissions = Permission.objects.filter(
                content_type__app_label=model._meta.app_label,
                content_type__model=model._meta.model_name,
            )
            metadata.update({"permissions": {p.codename: p.name for p in permissions}})
        return metadata


def build_mock_request(method, path, view, original_request, **kwargs):
    """ build a mocked request and use original request as reference if available """
    request = getattr(
        APIRequestFactory(),
        method.lower(),
        partial(APIRequestFactory().generic, method=method.lower()),
    )(path=path)
    request = view.initialize_request(request)
    if original_request:
        request.user = original_request.user
        request.auth = original_request.auth
        # ignore headers related to authorization as it has been handled above.
        # also ignore ACCEPT as the MIME type refers to SpectacularAPIView and the
        # version (if available) has already been processed by SpectacularAPIView.
        for name, value in original_request.META.items():
            if not name.startswith("HTTP_"):
                continue
            if name in ["HTTP_ACCEPT", "HTTP_COOKIE", "HTTP_AUTHORIZATION"]:
                continue
            request.META[name] = value
    return request
