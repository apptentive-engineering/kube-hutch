# kube-hutch
Minimal tool for retrieving and storing Kubernetes resource YAMLs

## Requirements
Written/tested against Python 3.6.2.

## Configuration

All configuration is expected to be found in the `config.yaml` file.

### Options

|       Key      | Type |                             Description                              |
|----------------|------|----------------------------------------------------------------------|
|api_resource_map| Hash |`resource-type`:`client-api-version` _key:value_ pairs                |
|   base_path    |String|Path where exported YAML files should be stored                       |
|   blacklist    | List |Nested list of hashes, denoting attributes that should not be exported|
|  kube_config   |String|Path to `.kube/config` file. Defaults to: `$HOME/.kube/config`        |

## Usage

```bash
./hutch.py
```
