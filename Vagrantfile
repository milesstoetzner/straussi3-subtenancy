# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure("2") do |config|
  # The most common configuration options are documented and commented below.
  # For a complete reference, please see the online documentation at
  # https://docs.vagrantup.com.

  # Every Vagrant development environment requires a box. You can search for
  # boxes at https://vagrantcloud.com/search.
  config.vm.box = "debian/contrib-stretch64"

  # Disable automatic box update checking. If you disable this, then
  # boxes will only be checked for updates when the user runs
  # `vagrant box outdated`. This is not recommended.
  # config.vm.box_check_update = false

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine. In the example below,
  # accessing "localhost:8080" will access port 80 on the guest machine.
  # NOTE: This will enable public access to the opened port
  config.vm.network "forwarded_port", guest: 443, host: 443
  config.vm.network "forwarded_port", guest: 80, host: 80

  # TODO: disable port
  config.vm.network "forwarded_port", guest: 8000, host: 8000

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine and only allow access
  # via 127.0.0.1 to disable public access
  # config.vm.network "forwarded_port", guest: 80, host: 8080, host_ip: "127.0.0.1"

  # Create a private network, which allows host-only access to the machine
  # using a specific IP.
  # config.vm.network "private_network", ip: "192.168.33.10"

  # Create a public network, which generally matched to bridged network.
  # Bridged networks make the machine appear as another physical device on
  # your network.
  # config.vm.network "public_network"

  # Share an additional folder to the guest VM. The first argument is
  # the path on the host to the actual folder. The second argument is
  # the path on the guest to mount the folder. And the optional third
  # argument is a set of non-required options.
  # config.vm.synced_folder "../data", "/vagrant_data"
  config.vm.synced_folder "./", "/var/www/ferienmiete"

  # Provider-specific configuration so you can fine-tune various
  # backing providers for Vagrant. These expose provider-specific options.
  # Example for VirtualBox:
  #
  # config.vm.provider "virtualbox" do |vb|
  #   # Display the VirtualBox GUI when booting the machine
  #   vb.gui = true
  #
  #   # Customize the amount of memory on the VM:
  #   vb.memory = "1024"
  # end
  #
  # View the documentation for the provider you are using for more
  # information on available options.

  # Enable provisioning with a shell script. Additional provisioners such as
  # Puppet, Chef, Ansible, Salt, and Docker are also available. Please see the
  # documentation for more information about their specific syntax and use.
  config.vm.provision "shell", inline: <<-SHELL

    apt-get update
    apt-get install -y python3 vim python3-pip nginx virtualenvwrapper virtualenv python3-virtualenv python3-venv bash-completion

    pip3 install uwsgi

    # virtual environment
    sudo mkdir -p /var/www/ferienmiete
    sudo chown www-data:www-data /var/www/ferienmiete
    cd /var/www/ferienmiete/
    # source bin/activate

    # install requirements
    pip3 install -r requirements.txt
    # deactivate

    # start nginx
    sudo systemctl stop nginx
    sudo mkdir -p /etc/letsencrypt/live/str3.ext.selfnet.de/

    sudo ln -s /var/www/ferienmiete/config/certificate.pem /etc/letsencrypt/live/str3.ext.selfnet.de/fullchain.pem
    sudo ln -s /var/www/ferienmiete/config/key.pem /etc/letsencrypt/live/str3.ext.selfnet.de/privkey.pem

    sudo ln -s /var/www/ferienmiete/config/options-ssl-nginx.conf /etc/letsencrypt/
    sudo ln -s /var/www/ferienmiete/config/ssl-dhparams.pem /etc/letsencrypt/

    sudo ln -sf /var/www/ferienmiete/config/ferienmiete.conf /etc/nginx/sites-available/ferienmiete.conf
    sudo ln -sf /etc/nginx/sites-available/ferienmiete.conf /etc/nginx/sites-enabled/ferienmiete.conf
    sudo rm -f /etc/nginx/sites-enabled/default

    sudo systemctl enable nginx
    sudo systemctl restart nginx

    # start uwsgi service
    # systemctl stop uwsgi.service
    # systemctl disable uwsgi.service
    sudo mkdir -p /etc/uwsgi/sites/
    sudo mkdir -p /var/run/uwsgi
    sudo chown www-data:www-data /var/run/uwsgi
    sudo ln -sf /var/www/ferienmiete/config/ferienmiete.ini /etc/uwsgi/sites/ferienmiete.ini
    sudo ln -sf /var/www/ferienmiete/config/uwsgi.service /etc/systemd/system/uwsgi.service
    sudo systemctl daemon-reload
    sudo systemctl enable uwsgi.service
    sudo systemctl restart uwsgi.service

    # for killing uwsgi: sudo pkill -f uwsgi -9

    # selber rumfummeln -> sudo -u www-data bash
    # sudo -u www-data pyvenv /var/www/ferienmiete

    ## venv deaktivieren
    # deactivate

  SHELL
end
