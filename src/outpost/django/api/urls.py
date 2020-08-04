import django
from importlib import import_module

from django.apps import apps
from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter
from rest_framework.schemas import get_schema_view

from .schema import OpenAPIRenderer, SchemaGenerator

app_name = "api"

routers = {"v1": DefaultRouter()}

for app in sorted(apps.get_app_configs(), key=lambda app: app.label):
    try:
        module = import_module(f"{app.name}.endpoints")
        for version, router in routers.items():
            endpoints = getattr(module, version, [])
            for endpoint in sorted(endpoints, key=lambda e: e[0]):
                router.register(*endpoint)
    except Exception:
        pass

schema_view = get_schema_view(
    title="Medical University of Graz - API",
    urlconf="outpost.django.api.urls",
    generator_class=SchemaGenerator,
    renderer_classes=[OpenAPIRenderer],
)

urlpatterns = [url(r"^schema", schema_view, name="schema")] + [
    url(f"^{v}/", include((r.urls, v) if django.VERSION >= (2, 1) else r.urls, namespace=v)) for v, r in routers.items()
]
