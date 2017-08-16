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

def hashify(resource)
  hashed_resource = resource.to_hash
  hashed_resource[:apiVersion] = 'v1'
  hashed_resource[:kind] = resource.class.to_s.split('::').last

  hashed_resource.deep_stringify_keys
end

def filter(resource, blacklist)
  blacklist.each do |entry|
    case entry
    when Hash
      entry.each do |k, v|
        resource[k] = filter(resource[k], entry[k]) if resource.has_key?(k)
      end
    when String
      resource.delete(entry) if resource.has_key?(entry)
    end
  end

  resource
end


if __FILE__ == $0
  k8 = kube_api

  CONFIG_FILE = 'config.yaml'
  BLACKLIST = YAML.load_file(CONFIG_FILE)['blacklist']

  k8.get_replication_controllers.each do |rc|
    puts
    puts filter(hashify(rc), BLACKLIST).to_yaml
  end
end
