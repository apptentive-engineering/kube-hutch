#!/usr/bin/env ruby

require 'kubeclient'
require 'yaml'


def kube_api(kube_config = ::File.join(ENV['HOME'], '.kube', 'config'))
  config = Kubeclient::Config.read(kube_config).context

  Kubeclient::Client.new(
    config.api_endpoint,
    config.api_version,
    {
      ssl_options: config.ssl_options,
      auth_options: config.auth_options
    }
  )
end


k8 = kube_api

k8.get_replication_controllers.each do |rc|
  puts
  puts rc.to_hash.to_yaml
end
