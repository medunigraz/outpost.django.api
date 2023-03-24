from django.contrib.auth.models import Permission
from guardian.ctypes import get_content_type
from guardian.models import (
    GroupObjectPermission,
    UserObjectPermission,
)
from rest_framework.permissions import (
    DjangoModelPermissions,
    DjangoObjectPermissions,
)


class ExtendedDjangoModelPermissions(DjangoModelPermissions):

    perms_map = DjangoModelPermissions.perms_map | {
        "GET": ["%(app_label)s.view_%(model_name)s"],
    }


class ExtendedDjangoObjectPermissions(DjangoObjectPermissions):

    perms_map = DjangoObjectPermissions.perms_map | {
        "GET": ["%(app_label)s.view_%(model_name)s"],
    }

    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        queryset = self._queryset(view)
        model_cls = queryset.model
        if super().has_permission(request, view):
            return True
        perms = self.get_required_object_permissions(request.method, model_cls)
        if not perms:
            return True
        ct = get_content_type(model_cls)
        for n in perms:
            _, codename = n.split(".")
            p = Permission.objects.get(content_type=ct, codename=codename)
            if UserObjectPermission.objects.filter(
                user=request.user, content_type=ct, permission=p
            ).exists():
                return True
            if GroupObjectPermission.objects.filter(
                group__in=request.user.groups.all(), content_type=ct, permission=p
            ).exists():
                return True
        return False
