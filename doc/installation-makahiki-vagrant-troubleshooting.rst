.. _section-installation-makahiki-vagrant-troubleshooting:

Troubleshooting Makahiki on Vagrant
===================================

This section contains troubleshooting and configuration instructions for a Makahiki installation 
on Vagrant. Throughout this guide, a ``%`` prompt represents the virtual machine command prompt.

If you were linked here from :ref:`section-installation-makahiki-vagrant-quickstart`, you should 
jump to the section specific to your problem.

  * If **Copying locale settings to /etc/bash.bashrc** failed, go to :ref:`troubleshooting-bash-bashrc-and-utf-8-encodings`.
  * If **Copying settings to pg_hba.conf** failed, go to :ref:`troubleshooting-postgresql`.
  * If **Creating /home/vagrant/makahiki_env.sh** failed, go to :ref:`troubleshooting-makahiki-env-sh`.
  * If **Appending to /home/vagrant/.bashrc** failed, go to :ref:`troubleshooting-bashrc`.

.. about-nano:

About nano
----------

These instructions assume the use of the nano text editor, which 
is installed by default on the ``precise32`` virtual machine configured in 
:ref:`section-installation-makahiki-vagrant-quickstart`.

Read the `nano documentation`_ if you are unfamiliar with nano.
The basic controls are as follows:

  * Arrow keys: Move cursor
  * Control-G (^G) Open Help / Control-X (^X): Exit Help
  * Control-O (^O): Save
  * Control-X (^X): Close
  * Control-W (^W): Search
  * Control-Y (^Y): Page Up
  * Control-V (^V): Page Down
  * Control-K (^K): Cuts entire current line.
  * Control-U (^U): Pastes last line that was cut.
  * Control-C (^C): Shows the current position of the cursor at bottom of screen

If you close a document without saving changes, you will be prompted::

  Save modified buffer (ANSWERING "No" WILL DESTROY CHANGES) ?

Y saves, N closes without saving, and ^C is cancel.

When you save a document (e.g., one called test.txt), you will be prompted::

  File Name to Write: test.txt

Press Enter to continue, or type to edit the file name.

.. _nano documentation: http://www.nano-editor.org/docs.php

.. _troubleshooting-bash-bashrc-and-utf-8-encodings:

Troubleshooting bash.bashrc and UTF-8 Encodings
-----------------------------------------------

.. warning:: This troubleshooting process erases all databases in the PostgreSQL installation.

You need to change the system and postgresql database encodings if one of the 
following applies:

  * You experience a DatabaseError when the initialize_instance.py script runs, with the message ``character 0x##### of encoding "UTF8" has no equivalent in "LATIN1".``
  * The ``locale`` command returns a non-UTF-8 encoding setting::
  
      % locale
      LANG=en_US.LATIN1
      LANGUAGE=en_US.LATIN1
      ...
      LC_ALL=en_US.LATIN1

If either of these apply, continue.

Open /etc/bash.bashrc with sudo::

  % sudo nano /etc/bash.bashrc

Add these lines to the end of the file::

  # UTF-8 locale settings for Makahiki
  export LANGUAGE=en_US.UTF-8
  export LANG=en_US.UTF-8
  export LC_ALL=en_US.UTF-8

After you are done editing the file, run these commands::

  % sudo locale-gen en_US.UTF-8
  % sudo dpkg-reconfigure locales
  % sudo pg_dropcluster 9.1 main --stop
  % sudo pg_createcluster --locale en_US.UTF8 9.1 main
  % sudo cp /vagrant/vagrant/config_examples/pg_hba.conf.ubuntu.makahiki /etc/postgresql/9.1/main/pg_hba.conf
  % sudo /etc/init.d/postgresql restart

.. _troubleshooting-postgresql:

Troubleshooting PostgreSQL
--------------------------

Check PostgreSQL Local Connections
**********************************

Begin by verifying the PostgreSQL server authentication settings.
At the prompt, type ``psql -U postgres``. If it succeeds, type \q to quit::

  % psql -U postgres
  psql (9.1.9)
  Type "help" for help.

  postgres=#\q

If this fails, you will need to edit pg_hba.conf.

Edit pg_hba.conf
****************

If you cannot connect to the database with ``psql -U postgres``,  
check that the pg_hba.conf file has the correct settings applied.

On Ubuntu 12.04 LTS, pg_hba.conf is at /etc/postgresql/9.1/main/pg_hba.conf.
Open it in the nano text editor with sudo (root) privileges::

  % sudo nano /etc/postgresql/9.1/main/pg_hba.conf

Edit the file to match the examples below::

  # Database administrative login by Unix domain socket
  local   all             postgres                                trust
  
  # TYPE  DATABASE        USER            ADDRESS                 METHOD
  
  # "local" is for Unix domain socket connections only
  local   all             all                                     trust
  # IPv4 local connections:
  host    all             all             127.0.0.1/32            md5
  # IPv6 local connections:
  host    all             all             ::1/128                 md5

After you have edited the pg_hba.conf file, restart the Postgresql service::

  % sudo /etc/init.d/postgresql restart

.. _troubleshooting-makahiki-env-sh:

Troubleshooting makahiki_env.sh
-------------------------------

makahiki_env.sh sets values for Makahiki environment variables 
``MAKAHIKI_DATABASE_URL`` and ``MAKAHIKI_ADMIN_INFO``. Check that these 
values have been set::

  vagrant@precise32:/vagrant$ echo $MAKAHIKI_DATABASE_URL
  postgres://makahiki:makahiki@localhost:5432/makahiki
  vagrant@precise32:/vagrant$ echo $MAKAHIKI_ADMIN_INFO
  admin:admin

If "echo" returns nothing, source home/vagrant/.bashrc (~/.bashrc) and 
check again::

  vagrant@precise32:/vagrant$ source ~/.bashrc

If MAKAHIKI_DATABASE_URL and MAKAHIKI_ADMIN_INFO are still not set, you need 
to add them to /home/vagrant/makahiki_env.sh.

Create this file if it does not exist::

  vagrant@precise32:~$ touch makahiki_env.sh

Open the file in the nano text editor::

  vagrant@precise32:~$ nano makahiki_env.sh

The file should contain the lines shown below::

  # Makahiki environment variables
  # Syntax: postgres://<db_user>:<db_password>@<db_host>:<db_port>/<db_name>
  export MAKAHIKI_DATABASE_URL=postgres://makahiki:makahiki@localhost:5432/makahiki
  # Syntax: <admin_name>:<admin_password>
  export MAKAHIKI_ADMIN_INFO=admin:admin

These settings are only used to initialize the Makahiki database. If you change 
the username or password in the Makahiki user interface, these settings will 
no longer apply.

.. note:: The username:password combination of admin:admin is meant for use in 
   development. In a production server, the value of MAKAHIKI_ADMIN_INFO would be 
   changed to a more secure value.

When you are done editing makahiki_env.sh, source the .bashrc file. This will 
source the makahiki_env.sh file, which will set the environment variables::

  vagrant@precise32:/vagrant$ source ~/.bashrc
  vagrant@precise32:/vagrant$ echo $MAKAHIKI_DATABASE_URL
  postgres://makahiki:makahiki@localhost:5432/makahiki
  vagrant@precise32:/vagrant$ echo $MAKAHIKI_ADMIN_INFO
  admin:admin

If this fails, continue to the next section.

.. _troubleshooting-bashrc:

Troubleshooting .bashrc
-----------------------

The provisioning script normally appends this line to the "vagrant" user's .bashrc file::

  % source /home/vagrant/makahiki_env.sh

Open /home/vagrant/.bashrc in the nano editor::

  % nano ~/.bashrc

Add the line ``source /home/vagrant/makahiki_env.sh`` to the end of the file 
if it is not there. Save the file and source it for changes to take effect::

  % source ~/.bashrc




