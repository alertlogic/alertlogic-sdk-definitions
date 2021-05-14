# Alert Logic APIs definitions

[![Build Status](https://travis-ci.com/alertlogic/alertlogic-sdk-definitions.svg?branch=master)](https://travis-ci.com/alertlogic/alertlogic-sdk-definitions)
[![PyPI version](https://badge.fury.io/py/alertlogic-sdk-definitions.svg)](https://badge.fury.io/py/alertlogic-sdk-definitions)

Repository contains static definitions of Alert Logic APIs, used for documentation generation, 
[SDK](https://github.com/alertlogic/alertlogic-sdk-python) and [CLI](https://github.com/alertlogic/alcli).

### Usage

#### Install 
`pip install alertlogic-sdk-definitions`

For the one who doesn't require python code, GitHub releases are produced 
containing an archive with OpenAPI definitions only, see
[here](https://github.com/alertlogic/alertlogic-sdk-definitions/releases)

#### Test
`python -m unittest`

#### Use

List available service definitions:
```
>>> import alsdkdefs
>>> alsdkdefs.list_services()
OrderedDict([('aecontent', ServiceDefinition(aecontent)), ('aefr', ServiceDefinition(aefr)), ('aepublish', ServiceDefinition(aepublish)), ('aerta', ServiceDefinition(aerta)), ('aetag', ServiceDefinition(aetag)), ('aetuner', ServiceDefinition(aetuner)), ('aims', ServiceDefinition(aims)), ('assets_query', ServiceDefinition(assets_query)), ('assets_write', ServiceDefinition(assets_write)), ('connectors', ServiceDefinition(connectors)), ('credentials', ServiceDefinition(credentials)), ('deployments', ServiceDefinition(deployments)), ('herald', ServiceDefinition(herald)), ('ingest', ServiceDefinition(ingest)), ('iris', ServiceDefinition(iris)), ('kalm', ServiceDefinition(kalm)), ('notify', ServiceDefinition(notify)), ('otis', ServiceDefinition(otis)), ('policies', ServiceDefinition(policies)), ('remediations', ServiceDefinition(remediations)), ('responder', ServiceDefinition(responder)), ('search', ServiceDefinition(search)), ('subscriptions', ServiceDefinition(subscriptions)), ('themis', ServiceDefinition(themis))])
```

Get path to a service definitions paths:
```
>>> import alsdkdefs
>>> alsdkdefs.get_service_defs("aerta")
['/usr/local/lib/python3.8/site-packages/alsdkdefs/apis/aerta/aerta.v1.yaml']
```

Get normalised service spec of a service(all refs resolved, 
                                 path parameters moved to the methods, 
                                 allOfs are merged if possible):
```
>>> import alsdkdefs
>>> alsdkdefs.load_service_spec("aerta")
```

Validate service spec: 
```
>>> import alsdkdefs
>>> service_spec = alsdkdefs.load_service_spec("aerta")
>>> alsdkdefs.validate(service_spec)
```

#### Quick validation of a definition

While YAML definition is developed apart from the current package and current repo,
it is required to validate it prior to push, please add this to your `Makefile` 
in order to achieve quick validation:

`curl -s https://raw.githubusercontent.com/alertlogic/alertlogic-sdk-definitions/master/scripts/validate_my_definition.sh | bash -s <path/to/definitions/directory>`

If no directory is specified, by default `doc/openapi/` directory will be used, if such behaviour is desired, use following line instead:

`curl -s https://raw.githubusercontent.com/alertlogic/alertlogic-sdk-definitions/master/scripts/validate_my_definition.sh | bash `

It is recommended to invoke it via curl, since validation of the definitions might be extended with time.
Script requires `python3` to be available in the system.

Validation checks:
* YAML of a definition is valid
* Definition passes OpenAPI 3 schema validation

### Development

Please submit a PR. Please note that API definitions are updated automatically and any changes to it will be overwritten, see:
[automatic update process](doc/automatic_releases.md)
