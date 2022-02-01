import os
from os.path import join as pjoin
import glob
import collections
from collections import OrderedDict
import jsonschema
from urllib.parse import urlparse, urlsplit, urlunsplit
from urllib.request import urlopen, url2pathname
import yaml
import yaml.resolver
from functools import reduce, lru_cache
import requests
import json
import re
from jsonmerge import merge

try:
    import alsdkdefs_dev
    DEV_SDK_DEFS = True
except ImportError:
    DEV_SDK_DEFS = False

OPENAPI_SCHEMA_URL = 'https://raw.githubusercontent.com/OAI/OpenAPI-Specification/master/schemas/v3.0/schema.json'
OPENAPI_SCHEMA_FILE = 'openapi_schema.json'
URI_SCHEMES = ['file', 'http', 'https']


class ServiceDefinition:
    def __init__(self, name, filespath):
        self.service_name = name
        self.filespath = filespath

    def __str__(self):
        return self.service_name

    def __repr__(self):
        return f"ServiceDefinition({self.service_name})"

    def __gt__(self, other):
        return self.get_service_name() > other.get_service_name()

    def __eq__(self, other):
        return other.get_service_name() == self.get_service_name()

    def __lt__(self, other):
        return self.get_service_name() < other.get_service_name()

    def get_service_name(self):
        return self.service_name

    def get_files_path(self):
        return self.filespath


class AlertLogicOpenApiValidationException(Exception):
    pass


class OpenAPIKeyWord:
    OPENAPI = "openapi"
    INFO = "info"
    TITLE = "title"

    SERVERS = "servers"
    URL = "url"
    SUMMARY = "summary"
    DESCRIPTION = "description"
    VARIABLES = "variables"
    REF = "$ref"
    REQUEST_BODY_NAME = "x-alertlogic-request-body-name"
    RESPONSES = "responses"
    PATHS = "paths"
    OPERATION_ID = "operationId"
    PARAMETERS = "parameters"
    REQUEST_BODY = "requestBody"
    IN = "in"
    PATH = "path"
    QUERY = "query"
    HEADER = "header"
    COOKIE = "cookie"
    BODY = "body"
    NAME = "name"
    REQUIRED = "required"
    SCHEMA = "schema"
    TYPE = "type"
    STRING = "string"
    OBJECT = "object"
    ITEMS = "items"
    ALL_OF = "allOf"
    ONE_OF = "oneOf"
    ANY_OF = "anyOf"
    BOOLEAN = "boolean"
    INTEGER = "integer"
    ARRAY = "array"
    NUMBER = "number"
    FORMAT = "format"
    ENUM = "enum"
    SECURITY = "security"
    COMPONENTS = "components"
    SCHEMAS = "schemas"
    PROPERTIES = "properties"
    CONTENT = "content"
    DEFAULT = "default"
    ENCODING = "encoding"
    EXPLODE = "explode"
    STYLE = "style"
    PARAMETER_STYLE_MATRIX = "matrix"
    PARAMETER_STYLE_LABEL = "label"
    PARAMETER_STYLE_FORM = "form"
    PARAMETER_STYLE_SIMPLE = "simple"
    PARAMETER_STYLE_SPACE_DELIMITED = "spaceDelimited"
    PARAMETER_STYLE_PIPE_DELIMITED = "pipeDelimited"
    PARAMETER_STYLE_DEEP_OBJECT = "deepObject"
    DATA = "data"
    CONTENT_TYPE_PARAM = "content-type"
    CONTENT_TYPE_JSON = "application/json"
    CONTENT_TYPE_TEXT = "text/plain"
    CONTENT_TYPE_PYTHON_PARAM = "content_type"

    RESPONSE = "response"
    EXCEPTIONS = "exceptions"
    JSON_CONTENT_TYPES = ["application/json", "alertlogic.com/json"]

    SIMPLE_DATA_TYPES = [STRING, BOOLEAN, INTEGER, NUMBER]
    DATA_TYPES = [STRING, OBJECT, ARRAY, BOOLEAN, INTEGER, NUMBER]
    INDIRECT_TYPES = [ANY_OF, ONE_OF]

    # Alert Logic specific extensions
    X_ALERTLOGIC_SCHEMA = "x-alertlogic-schema"
    X_ALERTLOGIC_SESSION_ENDPOINT = "x-alertlogic-session-endpoint"


#
# Dictionaries don't preserve the order. However, we want to guarantee
# that loaded yaml files are in the exact same order to, at least
# produce the documentation that matches spec's order
#
class _YamlOrderedLoader(yaml.SafeLoader):
    pass


_YamlOrderedLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    lambda loader, node: collections.OrderedDict(loader.construct_pairs(node))
)


def get_apis_dir():
    """Get absolute apis directory path on the fs"""
    return f"{pjoin(os.path.dirname(__file__), 'apis')}"


def get_openapi_schema_dir():
    return f"{pjoin(os.path.dirname(__file__), 'schema')}"


def load_service_spec(service_name, apis_dir=None, version=None):
    """Loads a version of service from library apis directory, if version is not specified, latest is loaded"""
    services = list_services(apis_dir)
    servicedef = services.get(service_name)
    if not servicedef:
        raise FileNotFoundError(f'Service {service_name} definition files has not been found')
    service_api_dir = servicedef.get_files_path()
    if not version:
        # Find the latest version of the service api spes
        version = 0
        search_pattern = pjoin(service_api_dir, f"{service_name}.v*.yaml")
        for file in glob.glob(search_pattern):
            file_name = os.path.basename(file)
            new_version = int(file_name.split(".")[1][1:])
            version = version > new_version and version or new_version
    else:
        version = version[:1] != "v" and version or version[1:]
    service_spec_file_path = f"{pjoin(service_api_dir, service_name)}.v{version}.yaml"
    return load_spec(service_spec_file_path)


def load_spec(uri_or_path):
    """Loads spec out of RFC3986 URI, resolves refs, normalizes"""
    uri_or_path = normalize_uri(uri_or_path)
    return normalize_spec(uri_or_path, get_spec(uri_or_path))


def normalize_spec(uri_or_path, spec):
    """Resolves refs, normalizes"""
    uri_or_path = normalize_uri(uri_or_path)
    return __normalize_spec(__resolve_refs(__base_uri(uri_or_path), spec))


def get_spec(uri):
    """Loads spec out of RFC3986 URI, yaml's Reader detects encoding automatically"""
    with urlopen(uri) as stream:
        try:
            return yaml.load(stream, _YamlOrderedLoader)
        except:
            return json.loads(stream.read())


@lru_cache()
def list_services(apis_dir=None):
    """Lists services definitions available"""
    base_dir = apis_dir or get_apis_dir()
    dev_services = []
    if DEV_SDK_DEFS:
        dev_dirs = alsdkdefs_dev.get_apis_dir()
        dev_services = [ServiceDefinition(s, pjoin(dev_dirs, s)) for s in next(os.walk(dev_dirs))[1]]
    pub_services = [ServiceDefinition(s, pjoin(base_dir, s)) for s in next(os.walk(base_dir))[1]]
    services_search = OrderedDict(sorted([(str(servicedef), servicedef) for servicedef in pub_services + dev_services]))
    return services_search


def get_service_defs(service_name):
    """Lists a service's definitions available"""
    service = list_services()[service_name]
    return glob.glob(pjoin(service.get_files_path(), f"{service_name}.v*.yaml"))


@lru_cache()
def get_openapi_schema():
    try:
        r = requests.get(OPENAPI_SCHEMA_URL)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        # Use local copy of the Open API Schema
        openapi_schema_file = pjoin(get_openapi_schema_dir(), OPENAPI_SCHEMA_FILE)
        with open(openapi_schema_file) as data:
            return json.load(data)


def validate(spec, uri=None, schema=get_openapi_schema()):
    """Validates input spec by trying to resolve all refs, normalize, validate against the
     OpenAPI schema and then to suit AL SDK standards"""

    def _get_path_methods(path_obj):
        return filter(lambda op: op in
                                 ['get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace'], path_obj)

    def validate_operation_ids(spec):
        for path, path_obj in spec[OpenAPIKeyWord.PATHS].items():
            methods = _get_path_methods(path_obj)
            for method in methods:
                operationid = path_obj[method].get(OpenAPIKeyWord.OPERATION_ID, None)
                pattern = '^[A-Za-z][a-z0-9_]*$'
                base_msg = f"Path {path} method {method} operation {operationid}"
                if not operationid:
                    raise AlertLogicOpenApiValidationException(f"{base_msg}: Missing operationId")
                if not re.match(pattern, operationid):
                    raise AlertLogicOpenApiValidationException(f"{base_msg}: OperationId does not match {pattern}")

    def validate_path_parameters(spec):
        for path, path_obj in spec[OpenAPIKeyWord.PATHS].items():
            def get_params_of_type(params_obj, tp):
                return map(lambda p: p['name'], filter(lambda p: p['in'] == tp, params_obj))

            methods = _get_path_methods(path_obj)
            path_param_vars = re.findall('{(.*?)}', path)
            path_methods_parameters = __list_flatten(
                map(lambda m: get_params_of_type(path_obj[m].get(OpenAPIKeyWord.PARAMETERS, []), 'path'), methods))
            for path_param_var in path_param_vars:
                base_msg = f"Path {path} parameter {path_param_var}"
                if path_param_var not in path_methods_parameters:
                    raise AlertLogicOpenApiValidationException(f"{base_msg}: Parameter defined in the path is missing"
                                                               f" from parameters section")

    def al_specific_validations(spec):
        checks = [validate_operation_ids(spec), validate_path_parameters(spec)]
        all(checks)

    obj = normalize_spec(uri, spec)
    jsonschema.validate(obj, schema)
    return al_specific_validations(spec)


def make_file_uri(path):
    return make_uri('file', '', path, '', '')


def make_uri(scheme, netloc, url, query, fragment):
    return urlunsplit((scheme, netloc, url, query, fragment))


def normalize_uri(uri_or_path):
    parsed = urlparse(uri_or_path)
    if parsed.scheme not in URI_SCHEMES:
        return make_file_uri(uri_or_path)
    else:
        return uri_or_path

# Private functions


def __base_uri(uri):
    (scheme, netloc, path, query, fragment) = urlsplit(uri)
    path = os.path.dirname(url2pathname(path)) + '/'
    return urlunsplit((scheme, netloc, path, query, fragment))


def __list_flatten(l):
    return [item for sublist in l for item in sublist]


def __resolve_refs(file_base_uri, spec):
    def spec_ref_handler(uri):
        return __resolve_refs(uri, get_spec(uri))

    handlers = {'': spec_ref_handler, 'file': spec_ref_handler, 'http': spec_ref_handler, 'https': spec_ref_handler}
    resolver = jsonschema.RefResolver(file_base_uri, spec, handlers=handlers)

    def _do_resolve(node):
        if isinstance(node, collections.abc.Mapping) and OpenAPIKeyWord.REF in node:
            with resolver.resolving(node[OpenAPIKeyWord.REF]) as resolved:
                return resolved
        elif isinstance(node, collections.abc.Mapping):
            for k, v in node.items():
                node[k] = _do_resolve(v)
            __normalize_node(node)
        elif isinstance(node, (list, tuple)):
            for i in range(len(node)):
                node[i] = _do_resolve(node[i])

        return node

    return _do_resolve(spec)


def __normalize_spec(spec):
    for path in spec[OpenAPIKeyWord.PATHS].values():
        parameters = path.pop(OpenAPIKeyWord.PARAMETERS, [])
        for method in path.values():
            method.setdefault(OpenAPIKeyWord.PARAMETERS, [])
            method[OpenAPIKeyWord.PARAMETERS].extend(parameters)
    return spec


def __normalize_node(node):
    if OpenAPIKeyWord.ALL_OF in node:
        __update_dict_no_replace(
            node,
            dict(reduce(merge, node.pop(OpenAPIKeyWord.ALL_OF)))
        )


def __update_dict_no_replace(target, source):
    for key in source.keys():
        if key not in target:
            target[key] = source[key]
