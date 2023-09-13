from drf_spectacular.openapi import AutoSchema as BaseAutoSchema


class AutoSchema(BaseAutoSchema):
    method_mapping = BaseAutoSchema.method_mapping | {
        "discard": "discard",
    }
