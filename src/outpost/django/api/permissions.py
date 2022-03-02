from rest_framework.permissions import DjangoModelPermissions, DjangoObjectPermissions


class ExtendedDjangoModelPermissions(DjangoModelPermissions):

    perms_map = DjangoModelPermissions.perms_map | {
        "GET": ["%(app_label)s.view_%(model_name)s"],
    }


class ExtendedDjangoObjectPermissions(DjangoObjectPermissions):

    perms_map = DjangoObjectPermissions.perms_map | {
        "GET": ["%(app_label)s.view_%(model_name)s"],
    }
