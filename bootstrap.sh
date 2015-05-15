#!/usr/bin/env bash
export BASH_BASHRC_COPY_RESULT="Unknown"
export PG_HBA_CONF_COPY_RESULT="Unknown"
export MAKAHIKI_ENV_SETUP_RESULT="Unknown"

echo "Makahiki Environment Setup Script for Ubuntu (x86)"
echo "--------------------------------------------------"
echo "Script started at $(date)"
echo "Copying bash.bashrc with locale settings (UTF-8) to /etc/bash.bashrc: started at $(date)"
# Begin bash.bashrc copying code:
MD5SUM_BASH_EXPECTED=$(md5sum "/vagrant/vagrant/config_examples/bash.bashrc.ubuntu.default")
MD5SUM_BASH_ACTUAL=$(md5sum "/etc/bash.bashrc")
MD5SUM_BASH_MAKAHIKI=$(md5sum "/vagrant/vagrant/config_examples/bash.bashrc.ubuntu.makahiki")

# Split string <checksum><2 spaces><filename> on spaces (awk default)
MD5_BASH_EXPECTED=$(echo "$MD5SUM_BASH_EXPECTED" | awk '{ print $1 }')
MD5_BASH_ACTUAL=$(echo "$MD5SUM_BASH_ACTUAL" | awk '{ print $1 }')
MD5_BASH_MAKAHIKI=$(echo "$MD5SUM_BASH_MAKAHIKI" | awk '{ print $1 }')

echo "Expected md5 checksum of default /etc/bash.bashrc: $MD5_BASH_EXPECTED"
echo "Actual md5 checksum of default /etc/bash.bashrc: $MD5_BASH_ACTUAL"

if [ $MD5_BASH_EXPECTED = $MD5_BASH_ACTUAL ]
    then
        echo "Checksums match. bash.bashrc will be overwritten with Makahiki settings."
        echo "sudo cp /vagrant/vagrant/config_examples/bash.bashrc.ubuntu.makahiki /etc/bash.bashrc"
        sudo cp /vagrant/vagrant/config_examples/bash.bashrc.ubuntu.makahiki /etc/bash.bashrc
        echo "bash.bashrc copy succeeded. [ OK ]"
        export BASH_BASHRC_COPY_RESULT="Succeeded"
    else
        if [ $MD5_BASH_MAKAHIKI = $MD5_BASH_ACTUAL ]
            then
                echo "bash.bashrc file already overwritten with makahiki settings. [ OK ]"
                export BASH_BASHRC_COPY_RESULT="Already completed" 
            else
                echo "WARNING! bash.bashrc default file is different from expected file."
                echo "File could not be safely overwritten with Makahiki defaults."
                echo "You will need to edit it manually."
                export BASH_BASHRC_COPY_RESULT="Failed"
        fi
fi
# End bash.bashrc copying code.
echo "Copying bash.bashrc with locale settings (UTF-8) to /etc/bash.bashrc: finished at $(date)"
echo "Configuring UTF-8 locale settings: started at $(date)"
echo "locale-gen en_US.UTF-8"
locale-gen en_US.UTF-8
echo "dpkg-reconfigure locales"
dpkg-reconfigure locales
echo "Configuring UTF-8 locale settings: finished at $(date)"
echo "Updating package list: started at $(date)"
echo "apt-get update"
apt-get update
echo "Updating package list: finished at $(date)"
# wget is usually already installed.
echo "Installing wget: started at $(date)"
echo "apt-get -y install wget"
apt-get install -y wget
echo "Installing wget: finished at $(date)"
echo "Installing git: started at $(date)"
echo "apt-get install -y git"
apt-get install -y git
echo "Installing git: finished at $(date)"
echo "Installing gcc: started at $(date)"
echo "apt-get install -y gcc"
apt-get install -y gcc
echo "Installing gcc: finished at $(date)"
echo "Installing python-setuptools: started at $(date)"
echo "apt-get install -y python-setuptools"
apt-get install -y python-setuptools
echo "Installing python-setuptools: finished at $(date)"
echo "Installing pip: started at $(date)"
echo "easy_install pip==1.4.1"
easy_install pip==1.4.1
echo "Installing pip: finished at $(date)"
echo "Installing python-imaging: started at $(date)"
echo "apt-get install -y python-imaging"
apt-get install -y python-imaging
echo "Installing python-imaging: finished at $(date)"
echo "Installing python-dev: started at $(date)"
echo "apt-get install -y python-dev"
apt-get install -y python-dev
echo "Installing python-dev: finished at $(date)"
echo "Installing libjpeg-dev: started at $(date)"
echo "apt-get install -y libjpeg-dev"
apt-get install -y libjpeg-dev
echo "Installing libjpeg-dev: finished at $(date)"
# Python Imaging Library shared library symlink setup
echo "Configuring Python Imaging Library shared libraries: started at $(date)"
if [ ! -f /usr/lib/libjpeg.so ]
    then
        if [ -f /usr/lib/i386-linux-gnu/libjpeg.so ]
            then
                echo "Found: /usr/lib/i386-linux-gnu/libjpeg.so"
                echo "Creating symlink: /usr/lib/libjpeg.so --> /usr/lib/i386-linux-gnu/libjpeg.so"
                echo "sudo ln -s /usr/lib/i386-linux-gnu/libjpeg.so /usr/lib/libjpeg.so"
                sudo ln -s /usr/lib/i386-linux-gnu/libjpeg.so /usr/lib/
            else
                echo "Could not find libjpeg.so in /usr/lib or /usr/lib/i386-linux-gnu/." 
                echo "Python Imaging Library packages may not have installed properly."
                echo "Script exiting at $(date)."
                exit 1
                fi
    else
        echo "Found: /usr/lib/libjpeg.so"
fi

if [ ! -f /usr/lib/libz.so ]
    then
        if [ -f /usr/lib/i386-linux-gnu/libz.so ]
            then
                echo "Found: /usr/lib/i386-linux-gnu/libz.so"
                echo "Creating symlink: /usr/lib/libz.so --> /usr/lib/i386-linux-gnu/libz.so"
                echo "sudo ln -s /usr/lib/i386-linux-gnu/libz.so /usr/lib/"
                sudo ln -s /usr/lib/i386-linux-gnu/libz.so /usr/lib/
            else
                echo "Could not find libz.so in /usr/lib or /usr/lib/i386-linux-gnu/."
                echo "Python Imaging Library packages may not have installed properly."
                echo "Script exiting at $(date)"
                exit 1
        fi
    else
        echo "Found: /usr/lib/libz.so"
fi
echo "Configuring Python Imaging Library shared libraries: finished at $(date)"
echo "Installing postgresql-9.1: started at $(date)"
echo "apt-get install -y postgresql-9.1"
apt-get install -y postgresql-9.1
echo "Installing postgresql-9.1: finished at $(date)"
echo "Installing libpq-dev: started at $(date)"
echo "apt-get install -y libpq-dev"
apt-get install -y libpq-dev
echo "Installing libpq-dev: finished at $(date)"
echo "Configuring PostgreSQL cluster \"main\" with locale en_US.UTF8: started at $(date)"
echo "pg_dropcluster 9.1 main --stop"
pg_dropcluster 9.1 main --stop
echo "pg_createcluster --locale en_US.UTF8 9.1 main"
pg_createcluster --locale en_US.UTF8 9.1 main
echo "Configuring PostgreSQL cluster \"main\" with locale en_US.UTF8: finished at $(date)"
# Begin pg_hba.conf copying code:
echo "Copying PostgreSQL 9.1 pg_hba.conf: started at $(date)"
MD5SUM_PGHBA_EXPECTED=$(md5sum "/vagrant/vagrant/config_examples/pg_hba.conf.ubuntu.default")
MD5SUM_PGHBA_ACTUAL=$(md5sum "/etc/postgresql/9.1/main/pg_hba.conf")
MD5SUM_PGHBA_MAKAHIKI=$(md5sum "/vagrant/vagrant/config_examples/pg_hba.conf.ubuntu.makahiki")

# Split string <checksum><2 spaces><filename> on spaces (awk default)
MD5_PGHBA_EXPECTED=$(echo "$MD5SUM_PGHBA_EXPECTED" | awk '{ print $1 }')
MD5_PGHBA_ACTUAL=$(echo "$MD5SUM_PGHBA_ACTUAL" | awk '{ print $1 }')
MD5_PGHBA_MAKAHIKI=$(echo "$MD5SUM_PGHBA_MAKAHIKI" | awk '{ print $1 }')

echo "Expected md5 checksum of default PostgreSQL 9.1 pg_hba.conf: $MD5_PGHBA_EXPECTED"
echo "Actual md5 checksum of default PostgreSQL 9.1 pg_hba.conf: $MD5_PGHBA_ACTUAL"

if [ $MD5_PGHBA_EXPECTED = $MD5_PGHBA_ACTUAL ]
    then
        echo "Checksums match. pg_hba.conf will be overwritten with Makahiki settings."
        echo "sudo cp /vagrant/vagrant/config_examples/pg_hba.conf.ubuntu.makahiki /etc/postgresql/9.1/main/pg_hba.conf"
        sudo cp /vagrant/vagrant/config_examples/pg_hba.conf.ubuntu.makahiki /etc/postgresql/9.1/main/pg_hba.conf
        echo "pg_hba.conf copy succeeded. [ OK ]"
        export PG_HBA_CONF_COPY_RESULT="Succeeded"
    else
        if [ $MD5_PGHBA_MAKAHIKI = $MD5_PGHBA_ACTUAL ]
            then
                echo "pg_hba.conf file already overwritten with makahiki settings. [ OK ]"
                export PG_HBA_CONF_COPY_RESULT="Already completed"
            else
                echo "WARNING! pg_hba.conf default file is different from expected file."
                echo "File could not be safely overwritten with Makahiki defaults."
                echo "You will need to edit it manually."
                export PG_HBA_CONF_COPY_RESULT="Failed"
        fi
fi
echo "/etc/init.d/postgresql restart"
/etc/init.d/postgresql restart
echo "Copying PostgreSQL 9.1 pg_hba.conf: finished at $(date)"
# End pg_hba.conf copying code.
echo "Installing memcached: started at $(date)"
echo "apt-get install -y memcached"
apt-get install -y memcached
echo "Installing memcached: finished at $(date)"
# Begin libmemcached-0.53 installation
echo "Installing libmemcached-0.53: started at $(date)"
if [ ! -f /usr/local/lib/libmemcached.so ]
    then
        echo "apt-get install -y build-essential"
        apt-get install -y build-essential
        echo "apt-get install -y g++"
        apt-get install -y g++
        echo "apt-get install -y libcloog-ppl-dev"
        apt-get install -y libcloog-ppl-dev
        echo "apt-get install -y libcloog-ppl0"
        apt-get install -y libcloog-ppl0
        # make creates symlinks, so it must occur in a non-shared folder.
        echo "mkdir /home/vagrant/makahiki-temp-downloads"
        mkdir /home/vagrant/makahiki-temp-downloads
        echo "cd /home/vagrant/makahiki-temp-downloads"
        cd /home/vagrant/makahiki-temp-downloads
        echo "wget http://launchpad.net/libmemcached/1.0/0.53/+download/libmemcached-0.53.tar.gz"
        wget http://launchpad.net/libmemcached/1.0/0.53/+download/libmemcached-0.53.tar.gz
        echo "tar xzvf libmemcached-0.53.tar.gz"
        tar xzvf libmemcached-0.53.tar.gz
        echo "cd libmemcached-0.53"
        cd libmemcached-0.53
        echo "./configure"
        ./configure
        echo "make"
        make
        echo "make install"
        make install
        if [ -f /usr/local/lib/libmemcached.so ]
            then
                print "libmemcached-0.53 built and installed successfully."
            else
                print "libmemcached-0.53 installation failed."
        fi
        echo "Cleaning up..."
        echo "cd /home/vagrant"
        cd /home/vagrant
        echo "rm -rf makahiki-temp-downloads"
        rm -rf makahiki-temp-downloads
    else
        echo "libmemcached-0.53 was already installed."
fi
echo "Installing libmemcached-0.53: finished at $(date)"
# End of libmemcached-0.53 installation
echo "Installing virtualenvwrapper: started at $(date)"
echo "pip install virtualenvwrapper"
pip install virtualenvwrapper
echo "Installing virtualenvwrapper: finished at $(date)"
echo "Copying configuration into /home/vagrant/makahiki_env.sh: started at $(date)"
if [ ! -f /home/vagrant/makahiki_env.sh ]
    then
        echo "cp /vagrant/vagrant/config_examples/makahiki_env.sh /home/vagrant/makahiki_env.sh"
        cp /vagrant/vagrant/config_examples/makahiki_env.sh /home/vagrant/makahiki_env.sh
        echo "chown vagrant:vagrant /home/vagrant/makahiki_env.sh"
        chown vagrant:vagrant /home/vagrant/makahiki_env.sh
        MAKAHIKI_ENV_SETUP_RESULT="Succeeded"
    else
        echo "/home/vagrant/makahiki_environment.sh already exists. [ OK ]"
        MAKAHIKI_ENV_SETUP_RESULT="Already completed."
fi
echo "Copying configuration into /home/vagrant/makahiki_env.sh: finished at $(date)"
# Begin .bashrc appending code:
echo "Appending Makahiki settings to /home/vagrant/.bashrc: started at $(date)"
MD5SUM_HOME_BASHRC_EXPECTED=$(md5sum "/vagrant/vagrant/config_examples/home.bashrc.ubuntu.default")
MD5SUM_HOME_BASHRC_ACTUAL=$(md5sum "/home/vagrant/.bashrc")
MD5SUM_HOME_BASHRC_MAKAHIKI=$(md5sum "/vagrant/vagrant/config_examples/home.bashrc.ubuntu.makahiki")

# Split string <checksum><2 spaces><filename> on spaces (awk default)
MD5_HOME_BASHRC_EXPECTED=$(echo "$MD5SUM_HOME_BASHRC_EXPECTED" | awk '{ print $1 }')
MD5_HOME_BASHRC_ACTUAL=$(echo "$MD5SUM_HOME_BASHRC_ACTUAL" | awk '{ print $1 }')
MD5_HOME_BASHRC_MAKAHIKI=$(echo "$MD5SUM_HOME_BASHRC_MAKAHIKI" | awk '{ print $1 }')

echo "Expected md5 checksum of default /home/vagrant/.bashrc: $MD5_HOME_BASHRC_EXPECTED"
echo "Actual md5 checksum of default /home/vagrant/.bashrc: $MD5_HOME_BASHRC_ACTUAL"

if [ $MD5_HOME_BASHRC_EXPECTED = $MD5_HOME_BASHRC_ACTUAL ]
    then
        echo "Checksums match. /home/vagrant/.bashrc will have Makahiki settings appended."
        echo "# Makahiki environment settings" >> /home/vagrant/.bashrc
        echo "source /home/vagrant/makahiki_env.sh" >> /home/vagrant/.bashrc
        echo "/home/vagrant/.bashrc append succeeded. [ OK ]"
        export HOME_BASHRC_RESULT="Succeeded"
    else
        if [ $MD5_HOME_BASHRC_MAKAHIKI = $MD5_HOME_BASHRC_ACTUAL ]
            then
                echo "/home/vagrant/.bashrc file already overwritten with makahiki settings. [ OK ]"
                export HOME_BASHRC_RESULT="Already completed"
            else
                echo "WARNING! /home/vagrant/.bashrc default file is different from expected file."
                echo "File could not be safely overwritten with Makahiki defaults."
                echo "You will need to edit it manually."
                export HOME_BASHRC_RESULT="Failed"
        fi
fi
echo "Appending Makahiki settings to /home/vagrant/.bashrc: finished at $(date)"
# End .bashrc appending code.
echo "pip install: started at $(date)"
echo "cd /vagrant"
cd /vagrant
echo "pip install -r requirements.txt"
pip install -r requirements.txt
echo "pip install: finished at $(date)"
echo "Initializing Makahiki database with default MAKAHIKI_DATABASE_URL"
echo "and MAKAHIKI_ADMIN_INFO: started at $(date)"
export MAKAHIKI_DATABASE_URL=postgres://makahiki:makahiki@localhost:5432/makahiki
export MAKAHIKI_ADMIN_INFO=admin:admin
echo "cd /vagrant/makahiki"
cd /vagrant/makahiki
echo "echo \"Y\" | ./scripts/initialize_instance.py --type default"
# This assumes that the initialize_instance.py script only requires one Y/n response.
echo "Y" | python ./scripts/initialize_instance.py --type default
echo "Initializing Makahiki database: finished at $(date)"
echo "-------------------------------------------------------------------------------"
echo "Configuration setup results:"
echo "-------------------------------------------------------------------------------"
echo "1. Copying locale settings to /etc/bash.bashrc: [$BASH_BASHRC_COPY_RESULT]"
echo "2. Copying settings to pg_hba.conf: [$PG_HBA_CONF_COPY_RESULT]"
echo "3. Creating /home/vagrant/makahiki_env.sh: [$MAKAHIKI_ENV_SETUP_RESULT]"
echo "4. Appending to /home/vagrant/.bashrc: [$HOME_BASHRC_RESULT]"
echo "-------------------------------------------------------------------------------"
echo "Script completed at $(date)"
exit 0
