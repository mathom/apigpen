# apigpen

`apigpen` is a tool to import and export your [AWS API Gateway](https://aws.amazon.com/api-gateway) projects
for version control, manipulation, or other similar tasks.

It currently does not import/export API keys, custom domains, or client certificates.

## Installation

`pip install git+git://github.com/mathom/apigpen.git`

## Usage

You can list your REST APIs with the `--list` flag:
```
$ apigpen --list
12345abcde my-great-api
fghij67890 another-one
```

When you want to export, pass the API name or ID to the `--export` flag:
```
$ apigpen --export my-great-api > myapi.yaml
```

Note: You can add `--json` if you prefer JSON over YAML output.

Importing works similarly, except you are providing a new name for the imported API:
```
$ apigpen --import a-copied-api < myapi.yaml
```

## FAQ

### Why not use the official importer/exporter?

The official tools/swagger don't currently support all of the API Gateway features.
For example, it currently doesn't support the `text/html` content type on integration responses.
