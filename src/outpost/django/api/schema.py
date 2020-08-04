import rest_framework
from collections import defaultdict
from urllib.parse import urlparse

from rest_framework.renderers import OpenAPIRenderer as BaseOpenAPIRenderer

if tuple(map(int, rest_framework.VERSION.split("."))) < (3, 11):
    from rest_framework.schemas.generators import SchemaGenerator as BaseSchemaGenerator
else:
    from rest_framework.schemas.generators import BaseSchemaGenerator


class SchemaGenerator(BaseSchemaGenerator):
    @property
    def default_mapping(self):
        mapping = defaultdict(lambda: "custom")
        for k, v in BaseSchemaGenerator.default_mapping.items():
            mapping[k] = v
        return mapping


class OpenAPIRenderer(BaseOpenAPIRenderer):
    def get_paths(self, document):
        paths = {}

        tag = None
        for name, link in document.links.items():
            path = urlparse(link.url).path
            method = link.action.lower()
            paths.setdefault(path, {})
            paths[path][method] = self.get_operation(link, name, tag=tag)

        for tag, section in document.data.items():
            if not section.links:
                sub_paths = self.get_paths(section)
                paths.update(sub_paths)
                continue

            for name, link in section.links.items():
                path = urlparse(link.url).path
                method = link.action.lower()
                paths.setdefault(path, {})
                paths[path][method] = self.get_operation(link, name, tag=tag)

        return paths
