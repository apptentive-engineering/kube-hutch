#!/usr/bin/env python3

from kubernetes import client, config
from os import path, environ
from pathlib import Path
from yaml import dump



def resource_to_yaml(resource, target_path):
  """
  Writes a dictionary export of a kubernetes resource to a yaml file

  :param resource: kubernetes.client.models.* - a kubernetes resource
  :param target_path: str - a path to store the yaml file
  :return: str - path where generated yaml was stored
  """
  resource_path = path.join(target_path, resource.kind, resource.metadata.namespace)
  Path(resource_path).mkdir(parents=True, exist_ok=True)

  file_path = path.join(resource_path, "{}.yml".format(resource.metadata.name))
  with open(file_path, 'w') as file:
    dump(resource.to_dict(), file, default_flow_style=False)

  return file_path



if __name__ == '__main__':
  BASE_PATH = 'backup'

  config.load_kube_config(path.join(environ['HOME'], '.kube/config'))
  v1beta1 = client.ExtensionsV1beta1Api()

  print('Backing up DaemonSets:')
  resource_path = path.join(BASE_PATH, 'DaemonSets')
  for ds in v1beta1.list_daemon_set_for_all_namespaces().items:
    resource = v1beta1.read_namespaced_daemon_set(ds.metadata.name, ds.metadata.namespace)
    print("\t" + resource_to_yaml(resource, BASE_PATH))