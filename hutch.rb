#!/usr/bin/env ruby

require 'kubeclient'


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
p k8.get_pods
