.. _section-installation-makahiki-local-unix:

Local installation on Unix
==========================

These instructions also assume that you are using a Bourne-type shell (such as bash),
which is the default on Mac OS X and Linux. Using a C-shell variant
(like tcsh), is possible but not recommended.

Hardware requirements
---------------------

Our estimated hardware requirements for **production** use are:
  * CPU:  modern dual or quad core
  * RAM: 8 GB
  * Disk space: 10 GB

For **development** only, a modern dual core CPU with 4 GB should be ok, although the more the better.

Install Python
--------------

Install `Python`_ 2.7.3 or higher (but not Python 3).

To check that python is installed and has the correct version::

  % python --version
    Python 2.7.3

Red Hat Enterprise Linux: Compile and Install Python 2.7.3
**********************************************************

As of Red Hat Enterprise Linux (RHEL 6) and CentOS 6, Python 2.6.6 is the default.
For Makahiki, Python 2.7.3 will be installed by compiling Python from scratch and
performing an altinstall.

Install wget::

  % sudo yum install wget

Next, install the packages needed to build and compile C::

  % sudo yum groupinstall -y "Development tools"
  % sudo yum install -y zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel

This will take a while.

Next, download and extract the Python 2.7.3 source code::

  % wget http://python.org/ftp/python/2.7.3/Python-2.7.3.tar.bz2
  % tar xf Python-2.7.3.tar.bz2

Have the current user take ownership of the extracted directory (replace <username> with your username)::

  % chown -R <username> Python-2.7.3

Change into the extracted directory::

  % cd Python-2.7.3

Configure the path to the altinstall::

  % ./configure --prefix=/usr/local

This sets the location of the altinstall to "/usr/local/bin/python2.7."

To finish the installation, make and install Python to the directory that you configured in the previous step::

  % make
  % sudo make altinstall

To run Python scripts using the Python 2.7.3 altinstall, you will need to use "python2.7"
instead of "python." Check the Python version::

  % python2.7 --version
  Python 2.7.3

Next, check that you can use the Python 2.7.3 shell, then exit::

  % python2.7
  Python 2.7.3 (default, Feb 26 2014, 11:02:10)
  [GCC 4.4.7 20120313 (Red Hat 4.4.7-4)] on linux2
  Type "help", "copyright", "credits" or "license" for more information.
  >>> exit()

You have now verified that the altinstall is working.

Install C Compiler
------------------

If you are using Mac OS X, install
`Apple Developer Tools`_ (i.e. Xcode 4). This is required in order to
build certain libraries (PIL, etc.) that require GCC (which is bundled with
Xcode). Xcode can either be found in your OS X installation DVD, or in the Mac
App Store.

If on Linux, in most cases, you will find the C/C++ compiler is already installed in your environment.

To check that C compiler is installed::

  % gcc --version

To install gcc on Ubuntu::

  % sudo apt-get install gcc

To install gcc on RHEL and CentOS::

  % sudo yum install gcc

Install Git
-----------

Find a package for your operating system at the `GitHub install
wiki`_. We recommend following the GitHub setup instructions at https://help.github.com/articles/set-up-git.

To check that Git is installed::

  % git --version


Install Pip
-----------

The process to install pip is different for each operating system.

Ubuntu
******

If you do not have easy_install, download and install it from the
`setuptools website`_ using ``sudo apt-get install python-setuptools``::

  % sudo apt-get install python-setuptools

If easy_install is installed on your system, install pip by typing::

  % easy_install pip==1.4.1

Depending on your system configuration, you may
have to type ``sudo easy_install pip==1.4.1``.

Check that pip 1.4.1 is installed::

  % pip --version

Red Hat Enterprise Linux (RHEL) and CentOS
******************************************

Install setuptools and pip for the original Python 2.6.6 installation::

  % sudo yum install python-setuptools
  % sudo easy_install pip==1.4.1

For Python 2.7.3, download and extract setuptools-0.8::

  % wget https://pypi.python.org/packages/source/s/setuptools/setuptools-0.8.tar.gz --no-check-certificate
  % tar xf setuptools-0.8.tar.gz

Change ownership of the extracted directory by replacing <username> with your username::

  % chown -R <username> setuptools-0.8

Change your working directory to the extracted directory and install::

  % cd setuptools-0.8
  % sudo /usr/local/bin/python2.7 setup.py install

Check that the installation was successful::

  % /usr/local/bin/easy_install-2.7 --version
  setuptools 0.8

You will install pip into the virtual environment later.

Install Virtual Environment Wrapper
-----------------------------------

`Virtualenvwrapper`_ allows you to install libraries separately from your global Python path.

Ubuntu
******
Follow the `virtualenvwrapper installation instructions`_ through the Quick Start section to install virtualenv and virtualenvwrapper. Once they are installed, create a virtual environment for makahiki as follows::

  % mkvirtualenv makahiki

To check that virtual environment wrapper is installed::

  % workon makahiki

RHEL and CentOS
***************

Install virtualenvwrapper for Python 2.6.6::

  % sudo /usr/bin/pip install virtualenvwrapper

Add these lines to the end of the ~/.bashrc file::

  # Virtualenvwrapper settings for makahiki
  export WORKON_HOME=$HOME/.virtualenvs
  export PROJECT_HOME=$HOME/makahiki
  export LD_LIBRARY_PATH=/usr/local/lib:/usr/lib
  export VIRTUALENVWRAPPER_VIRTUALENV=/usr/bin/virtualenv
  export VIRTUALENVWRAPPER_VIRTUALENV_ARGS='--no-site-packages'
  source /usr/bin/virtualenvwrapper.sh

Then source this file to apply changes::

  % source ~/.bashrc

Create a virtual environment that uses Python 2.7.3::

  % mkvirtualenv makahiki -p /usr/local/bin/python2.7

Creating a virtual environment should switch you to the virtual environment.
The terminal prompt will be preceded by the name of the virtual environment.
On RHEL, this looks like::

  (makahiki)[robot@computer makahiki]$

If creating the virtual environment did not switch you to the virtual
environment, use "workon makahiki" to switch to it::

  % workon makahiki

Check your Python version in the virtualenv::

  % python --version
  Python 2.7.3

.. note:: Any commands run with root privileges (``sudo python``) will use the default
   Python 2.6.6, not Python 2.7.3.

Next, uninstall the pip version in the virtual environment, and install pip==1.4.1 instead::

  % pip uninstall pip
  % easy_install pip==1.4.1

Install Python Imaging Library
------------------------------

Makahiki requires the `Python Imaging Library`_ (PIL).

Mac OS X
********

We have found `Homebrew`_ to be the most reliable way to install PIL.
Once Homebrew is installed, install PIL by typing::

  % brew install pil

Ubuntu
******

In Ubuntu, install PIL by typing::

  % sudo apt-get install -y python-imaging python-dev libjpeg-dev

Make sure you have both libjpeg (for JPEG) and zlib (for PNG) in the /usr/lib directory. If not, you can make the symbolic link there.

To make the symbolic links in a 32-bit Ubuntu OS::

  % sudo ln -s /usr/lib/i386-linux-gnu/libjpeg.so /usr/lib/libjpeg.so
  % sudo ln -s /usr/lib/i386-linux-gnu/libz.so /usr/lib/libz.so

To make the symbolic links in a 64-bit Ubuntu OS::

  % sudo ln -s /usr/lib/x86_64-linux-gnu/libjpeg.so /usr/lib/libjpeg.so
  % sudo ln -s /usr/lib/x86_64-linux-gnu/libz.so /usr/lib/libz.so

RHEL and CentOS
***************

In RHEL and CentOS, install PIL by typing::

  % sudo yum install -y python-imaging python-devel libjpeg-devel zlib-devel

Make sure you have both libjpeg (for JPEG) and zlib (for PNG) in the /usr/lib directory. If not, you can make the symbolic link there.

A 32-bit RHEL or CentOS OS should have symbolic links for libz.so and libjpeg.so in /usr/lib
created during installation.

If you have a 64-bit RHEL or CentOS OS, you will need to create the symbolic links manually::

  % sudo ln -s /usr/lib64/libjpeg.so /usr/lib/libjpeg.so
  % sudo ln -s /usr/lib64/libz.so /usr/lib/libz.so

Install PostgreSQL
------------------

Makahiki uses `PostgreSQL`_ as its standard backend database. We recommend version 9.1.3.

Mac OS X
********
Note that on Mac OS X, the installer will need to make changes in the
``sysctl`` settings and a reboot before installation can proceed.

Ubuntu
******

On Ubuntu, install the latest version of PostgreSQL 9.1, and install libpq-dev::

  % sudo apt-get install -y postgresql-9.1 libpq-dev

RHEL and CentOS
***************

On RHEL and CentOS, install the pgdg91 repository, then install the latest version of
Postgresql 9.1 and related packages.

.. note::
   Ignore the following warning when running ``sudo rpm -i``::

     warning: /var/tmp/rpm-tmp.Mgcm3P: Header V4 DSA/SHA1 Signature, key ID 442df0f8:NOKEY

On i386 (32-bit) systems::

  % sudo rpm -i http://yum.postgresql.org/9.1/redhat/rhel-6-i386/pgdg-redhat91-9.1-5.noarch.rpm
  % sudo yum install -y postgresql91-server postgresql91-contrib postgresql91-devel

On x86_64 (64-bit) systems::

  % sudo rpm -i http://yum.postgresql.org/9.1/redhat/rhel-6-x86_64/pgdg-redhat91-9.1-5.noarch.rpm
  % sudo yum install -y postgresql91-server postgresql91-contrib postgresql91-devel

Next, whether you are on an i386 or x86_64 system, initialize the database and start the server::

  % sudo service postgresql-9.1 initdb
  % sudo chkconfig postgresql-9.1 on

After Installation
******************

Once installed, use "which" to check that your PostgreSQL installation's bin/ directory is on
$PATH so that ``pg_config`` and ``psql`` are defined::

  % which pg_config
  % which psql

RHEL and CentOS users will see errors here. If you are a RHEL or CentOS user, you will
add the bin/ directory to the PATH in a later step.

Next, you will need to configure authentication for the "postgres" database user.

During development, a simple way to configure authentication is to make the postgres user
"trusted" locally.  This means that local processes such as Makahiki can connect to the
database server as the user postgres without authentication. To configure this way, edit
the pg_hba.conf file and change::

  local all postgres ident

to::

  local all postgres trust

The first line might be: "local all postgres peer". Change it to "local all postgres trust".

If you update the pg_hba.conf file you will have to restart the postgres server.

Ubuntu
******

The pg_hba.conf file is located in /etc/postgresql/9.1/main/pg_hba.conf and
must be opened with ``sudo``. Edit it to match the examples below::

  # Database administrative login by Unix domain socket
  local   all             postgres                                trust

  # TYPE  DATABASE        USER            ADDRESS                 METHOD

  # "local" is for Unix domain socket connections only
  local   all             all                                     trust
  # IPv4 local connections:
  host    all             all             127.0.0.1/32            md5
  # IPv6 local connections:
  host    all             all             ::1/128                 md5

Restart the server after updating pg_hba.conf::

  % /etc/init.d/postgresql restart

or::

  % sudo /etc/init.d/postgresql restart

RHEL and CentOS
***************

The pg_hba.conf file is located in /var/lib/pgsql/9.1/data/pg_hba.conf and
must be opened with ``sudo``. Edit it to match the examples below::

  # TYPE  DATABASE        USER            ADDRESS                 METHOD
  # "local" is for Unix domain socket connections only
  local   all             all                                     trust
  # IPv4 local connections:
  host    all             all             127.0.0.1/32            md5
  # IPv6 local connections:
  host    all             all             ::1/128                 md5

Restart the server after updating pg_hba.conf::

  % sudo service postgresql-9.1 restart

All Platforms
*************

Alternatively, you can create a .pgpass file containing the credentials for the user postgres. See
the PostgreSQL documentation for more information on the .pgpass file.

To check that PostgresSQL is installed and configured with "trusted" locally::

  % psql -U postgres

It should not prompt you for a password.

This will open the postgres command prompt. Use the command ``\q`` to exit.

Install Memcache
----------------

Makahiki can optionally use `Memcache`_ to improve performance, especially in the
production environment.  To avoid the need for alternative configuration files, we require
local installations to install Memcache and an associated library even if developers aren't
intending to use it.

Mac OS X
********
On Mac OS X, if you have installed `Homebrew`_, you can install these by typing::

  % brew install memcached
  % brew install libmemcached

Linux
*****
Linux users will need to download and build libmemcached from source. Start by installing memcached.

Ubuntu users::

  % sudo apt-get install -y memcached

RHEL and CentOS users::

  % sudo yum install -y memcached

Next, install packages needed to build libmemcached-0.53 from source.

Ubuntu users::

  % sudo apt-get install -y build-essential g++ libcloog-ppl-dev libcloog-ppl0

RHEL and CentOS users: If you have been following this guide, you should already have
performed a groupinstall of all packages in "Development tools."

If you did not, use the below command to do it now::

  % sudo yum groupinstall -y "Development tools"

Next, for Ubuntu, RHEL, and CentOS, download the source code and extract the archive::

  % wget http://launchpad.net/libmemcached/1.0/0.53/+download/libmemcached-0.53.tar.gz
  % tar xzvf libmemcached-0.53.tar.gz

.. warning:: Do not download and extract the source code in a directory that is synchronized with a Windows
   file system. This will cause the libmemcached-0.53 installation process to fail to create hard
   links and symbolic links during installation.


Switch into the extracted directory, then configure, make, and make install::

  % cd libmemcached-0.53
  % ./configure
  % make
  % sudo make install

Finally, check the location of the libmemcached.so library::

  % stat /usr/local/lib/libmemcached.so

If libmemcached.so is found successfully, then the installation is complete.

.. _Python: http://www.python.org/download/
.. _Python Imaging Library: http://www.pythonware.com/products/pil/
.. _Homebrew: http://mxcl.github.com/homebrew/
.. _GitHub install wiki: http://help.github.com/git-installation-redirect
.. _setuptools website: http://pypi.python.org/pypi/setuptools
.. _Virtualenvwrapper: http://www.doughellmann.com/docs/virtualenvwrapper/
.. _virtualenvwrapper installation instructions: http://www.doughellmann.com/docs/virtualenvwrapper/install.html#basic-installation
.. _PostgreSQL: http://www.postgresql.org/
.. _Apple Developer Tools: https://developer.apple.com/technologies/mac/
.. _Memcache: http://memcached.org
.. _Heroku's memcache installation instructions: http://devcenter.heroku.com/articles/memcache#local_memcache_setup

Download the Makahiki source
----------------------------

You can download the source by cloning or forking the `Makahiki Git repository`_::

  % git clone git://github.com/csdl/makahiki.git

This will create the new folder and download the code from the repository.

.. _Makahiki Git repository: https://github.com/csdl/makahiki/

Workon makahiki
---------------

The remaining steps require you to be in the makahiki/ directory and to have
activated that virtual environment::

  % cd makahiki/
  % workon makahiki

If you start a new shell in the midst of this process, you must be sure to invoke ``workon makahiki``
and of course cd to the appropriate directory before continuing.

Install required packages
-------------------------

RHEL and CentOS
***************

RHEL and CentOS users will need to add the PostgreSQL libraries to the PATH before
installing packages with "pip"::

  % export PATH=/usr/pgsql-9.1/bin:$PATH
  % which pg_config
  /usr/pgsql-9.1/bin/pg_config
  % which psql
  /usr/pgsql-9.1/bin/psql

Continue to "All Platforms."

All Platforms
*************

You can install the required Python package for Makahiki by::

  % pip install -r requirements.txt

Don't worry that this command generates lots and lots of output.

Setup environment variables
---------------------------

At a minimum, Makahiki requires two environment variables: MAKAHIKI_DATABASE_URL and
MAKAHIKI_ADMIN_INFO.

The following lines show example settings for these two environment variables, preceded by
a comment line describing their syntax::

  # Syntax: postgres://<db_user>:<db_password>@<db_host>:<db_port>/<db_name>
  export MAKAHIKI_DATABASE_URL=postgres://makahiki:makahiki@localhost:5432/makahiki

  # Syntax:  <admin_name>:<admin_password>
  export MAKAHIKI_ADMIN_INFO=admin:admin

You will want to either add these variables to a login script so they are
always available, or you can edit the ``postactivate`` file (in Unix, found in
``$WORKON_HOME/makahiki/bin``) so that they are defined whenever you
``workon makahiki``.

After you edit and save ``postactivate``, you will need to ``workon makahiki``
for your changes to take effect.

Note that you will want to provide a stronger password for the makahiki
admin account if this server is publicly accessible.

Makahiki also utilizes a variety of other environment variables. For complete
documentation, see :ref:`section-environment-variables`.

Initialize Makahiki
-------------------

Next, invoke the initialize_instance script, passing it an argument to specify what kind
of initial data to load. You need to be in the makahiki/makahiki directory. In most cases,
you will want to load the default dataset, as shown next::

  % cd makahiki
  % ./scripts/initialize_instance.py --type default

This command will:
  * Install and/or update all Python packages required by Makahiki;
  * Reinitialize the database contents and perform any needed database migrations.
  * Initialize the system with data.
  * Set up static files.

.. warning:: initialize_instance will wipe out all challenge configuration modifications!

   The initialize_instance script should be run only a single time in production
   scenarios, because any subsequent configuration modifications will be lost if initialize_instance is
   invoked again.   Use update_instance (discussed below) to update source code without
   losing subsequent configuration actions.

You will have to answer 'Y' to the question "Do you wish to continue (Y/n)?"

Start the server
----------------

Finally, you can start the Makahiki server using either::

  % ./manage.py run_gunicorn

or::

  % ./manage.py runserver

The first alternative (run_gunicorn) runs a more efficient web server, while the second (runserver) invokes a server
that is better for development (for example, :ref:`section-theme-development`).

Verify that Makahiki is running
-------------------------------

Open a browser and go to http://localhost:8000 to see the landing page, which should look
something like this:

.. figure:: figs/guided-tour/guided-tour-landing.png
   :width: 600 px
   :align: center


(Optional) Enable SSL
---------------------

In order to use SSL for your application, you may want to install a web server that supports SSL.
Apache and Nginx are good alternatives. We describe the steps to configure SSL for Nginx to use
with Makahiki.

1. Stop the gunicorn or manage.py processes.

2. Install Nginx. In CentOS, run::

    % yum install nginx

3. Edit /etc/nginx/conf.d/default.conf (location of the config file might be different)::

    server {
        listen       80;
        return 301 https://<server-host-name>:443/;
    }
    server {
        listen       443;
        server_name  <server-host-name>;

        ssl                  on;
        ssl_certificate      <location to site-cert.pem>;
        ssl_certificate_key  <location to site-key.pem>;

        ssl_session_timeout  5m;

        ssl_protocols  SSLv2 SSLv3 TLSv1;
        ssl_ciphers  HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers   on;

        location / {
                proxy_pass_header Server;
                proxy_set_header Host $http_host;
                proxy_redirect off;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Scheme $scheme;
                proxy_connect_timeout 10;
                proxy_read_timeout 10;
                proxy_pass http://<server-host-name>:8000/;
        }
     }

4. restart Nginx::

    % nginx -s stop
    % nginx

5. start the gunicorn server at port 8000

Configure your Makahiki instance
--------------------------------

Now that you have a running Makahiki instance, it is time to configure it for your
challenge, as documented in :ref:`section-site-configuration`.

Updating your Makahiki instance
-------------------------------

Makahiki is designed to support post-installation updating of your configured system when bug fixes or
system enhancements become available.   Updating an installed Makahiki instance is quite
simple, and consists of the following steps.

1. Bring down the running server in the shell process running Makahiki::

   % (type control-c in the shell running the makahiki server process)

2. In that shell or a new shell, go to your Makahiki installation directory, and ensure
   the Makahiki virtual environment is set up::

   % cd makahiki
   % workon makahiki

3. Download the updated source code into your Makahiki installation::

   % git pull origin master

4. Run the update_instance script to update your local configuration::

   % ./scripts/update_instance.py

5. Finally, restart your server, using either::

     % ./manage.py run_gunicorn

   or::

     % ./manage.py runserver
