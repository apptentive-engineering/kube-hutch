#!/usr/bin/env ruby

require 'active_support'
require 'active_support/core_ext/hash'
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

def filter(resource, blacklist)
  blacklist.each do |entry|
    case entry
    when Hash
      entry.each do |k, v|
        resource[k.to_sym] = filter(resource[k.to_sym], entry[k]) if resource.has_key?(k.to_sym)
      end
    when String
      resource.delete(entry.to_sym) if resource.has_key?(entry.to_sym)
    end
  end

  resource
end


k8 = kube_api

CONFIG_FILE = 'config.yaml'
BLACKLIST = YAML.load_file(CONFIG_FILE)['blacklist']

k8.get_replication_controllers.each do |rc|
  puts
  puts filter(rc.to_hash, BLACKLIST).deep_stringify_keys.to_yaml
end
