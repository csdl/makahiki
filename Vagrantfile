# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "precise32"
  config.vm.provision :shell, :path => "run_bootstrap.sh"
  # Configures this virtual machine to use a private (host-only) network in 
  # the 192.168.56.0/24 range.
  config.vm.network :private_network, ip: "192.168.56.4"
  config.vm.provider :virtualbox do |vb|
    vb.customize ["modifyvm", :id, "--memory", 1536]
  end
end