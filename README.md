# kube-hutch
Minimal tool for retrieving and storing Kubernetes resource YAMLs

## Requirements
Written/tested against Python 3.6.2.

## Configuration

All configuration is expected to be found in the `config.yaml` file.

### Options

|   Key   | Type |                             Description                             |
|---------|------|---------------------------------------------------------------------|
|base_path|String|Path where exported YAML files should be stored                      |
|blacklist| Hash |Nested hash of lists, denoting attributes that should not be exported|

## Usage

```bash
./hutch.py
```
