#!/usr/bin/env python3

from kubernetes import client as kube_client, config as kube_config
from os import path, environ
from pathlib import Path
from re import sub
from yaml import dump, load


def resource_to_yaml(resource, target_path):
  """
  Writes a dictionary export of a kubernetes resource to a yaml file

  :param resource: dict - result of a to_dict() call on a kubernetes resource
  :param target_path: str - a path to store the yaml file
  :return: str - path where generated yaml was stored
  """
  resource_path = path.join(target_path, resource['kind'], resource['metadata']['namespace'])
  Path(resource_path).mkdir(parents=True, exist_ok=True)

  file_path = path.join(resource_path, "{}.yml".format(resource['metadata']['name']))
  with open(file_path, 'w') as file:
    dump(resource, file, default_flow_style=False)

  return file_path


def cleanup_resource(resource, blacklist=None):
  """
  Transforms a dictionary export of a kubernetes resource by:
  - stripping all null attributes
  - converting all keys from snake_case to camelCase
  - stripping all attributes included in a blacklist

  :param resource: dict - result of a to_dict() call on a kubernetes resource
  :param blacklist: list - nested list of dicts & strings pulled from the hutch config yaml
  :return: dict - cleaned up resource
  """
  def remove_empty_from_dict(obj):
    """
    Strips all null attributes from a given dictionary

    :param obj: dict - dictionary to parse
    :return: dict - dictionary sripped of all null attributes
    """
    if type(obj) is dict:
      return {k: remove_empty_from_dict(v) for k, v in obj.items() if v and remove_empty_from_dict(v)}
    elif type(obj) is list:
      return [remove_empty_from_dict(v) for v in obj if v and remove_empty_from_dict(v)]
    else:
      return obj


  def keys_to_camel(d):
    """
    Convers all keys in a given dictionary from snake_case to camelCase

    :param d: dict - dictionary to parse
    :return: dict - converted dictionary
    """
    camelized = {}
    for k, v in d.items():
      export_value = v
      if type(v) is dict:
        export_value = keys_to_camel(v)
      elif type(v) is list:
        export_value = []
        for i in v:
          if type(i) is dict:
            export_value.append(keys_to_camel(i))
          else:
            export_value.append(i)

      camelized_key = sub(r'(?!^)_([a-zA-Z])', lambda x: x.group(1).upper(), k)
      camelized[camelized_key] = export_value

    return camelized


  def filter(rsc, bl):
    """
    Strips any key/values listed in the given blacklist from the given resource

    :param rsc: dict - result of a to_dict() call on a kubernetes resource
    :param bl: list - nested list of dicts & strings pulled from the hutch config yaml
    :return: dict - filtered resource
    """
    blacklist_keys = []
    for i in bl:
      if type(i) is dict:
        blacklist_keys.append(next(iter(i)))
      else:
        blacklist_keys.append(i)

    filtered = {}
    for k, v in rsc.items():
      if k in blacklist_keys:
        i = blacklist_keys.index(k)
        if type(bl[i]) is dict:
          filtered[k] = filter(v, bl[i][k])
      else:
        filtered[k] = v

    return filtered


  cleaned_resource = keys_to_camel(remove_empty_from_dict(resource))

  if blacklist is not None:
    cleaned_resource = filter(cleaned_resource, blacklist)

  return cleaned_resource


def get_resource_set(resource_type, config):
  """
  Retrieves a set of Kubernetes resources of a specific type

  :param resource_type: str - the type of resource to retrieve
  :param config: dict - runtime configuration settings
  """
  api_version = config['api_resource_map'][resource_type]
  connect = getattr(kube_client, api_version)
  client = connect()

  list_all = getattr(client, "list_{}_for_all_namespaces".format(resource_type))
  read_single = getattr(client, "read_namespaced_{}".format(resource_type))

  resources = []

  for resource_set in list_all().items:
    resource = read_single(resource_set.metadata.name, resource_set.metadata.namespace).to_dict()
    if 'blacklist' in config:
      resources.append(cleanup_resource(resource, config['blacklist']))
    else:
      resources.append(cleanup_resource(resource))

  return resources



if __name__ == '__main__':
  CONFIG_PATH = 'config.yaml'
  with open(CONFIG_PATH, 'r') as stream:
    CONFIG = load(stream)

  kube_config.load_kube_config(path.join(environ['HOME'], '.kube/config'))

  resource_types = ['daemon_set', 'deployment', 'job']
  resources = []
  for rsc_type in resource_types:
    print("Retrieving {}s...".format(rsc_type))
    resources += get_resource_set(rsc_type, CONFIG)

  print("\nBacked up:")
  for resource in resources:
    print("\t" + resource_to_yaml(resource, CONFIG['base_path']))
