#!/usr/bin/env python3

from kubernetes import client, config
from os import path, environ
from pprint import pprint

if __name__ == '__main__':
  config.load_kube_config(path.join(environ['HOME'], '.kube/config'))
  v1beta1 = client.ExtensionsV1beta1Api()

  print('Viewing DaemonSets:')
  for ds in v1beta1.list_daemon_set_for_all_namespaces().items:
    resource = v1beta1.read_namespaced_daemon_set(ds.metadata.name, ds.metadata.namespace).to_dict()
    pprint(resource)
