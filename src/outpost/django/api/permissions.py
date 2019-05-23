from rest_framework.permissions import DjangoModelPermissions, DjangoObjectPermissions


class ExtendedDjangoModelPermissions(DjangoModelPermissions):

    perms_map = dict(
        list(DjangoModelPermissions.perms_map.items())
        + [("GET", ["%(app_label)s.view_%(model_name)s"])]
    )


class ExtendedDjangoObjectPermissions(DjangoObjectPermissions):

    perms_map = dict(
        list(DjangoObjectPermissions.perms_map.items())
        + [("GET", ["%(app_label)s.view_%(model_name)s"])]
    )
