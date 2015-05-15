.. _section-installation-makahiki-vagrant-configuration-memcached:

Configuring Memcached on Vagrant
================================

The process for configuring Memcached on the Ubuntu virtual machine in Vagrant 
is different from the process for configuring Memcached on a normal Ubuntu 
installation.

Check The Memcached Installation
--------------------------------

The provisioning script installed Memcached and libmemcached-0.53 on the 
system. If you plan to configure Memcached, you will need to test the 
Memcached installation.

In the virtual machine, switch to the /vagrant/makahiki directory and run some 
commands in the manage.py shell::

  vagrant@precise32:~$ sudo service memcached restart
  vagrant@precise32:~$ export LD_LIBRARY_PATH_OLD=$LD_LIBRARY_PATH
  vagrant@precise32:~$ export LD_LIBRARY_PATH=/usr/local/lib:/usr/lib:$LD_LIBRARY_PATH
  vagrant@precise32:~$ export MAKAHIKI_USE_MEMCACHED=True
  vagrant@precise32:~$ cd /vagrant/makahiki
  vagrant@precise32:/vagrant/makahiki$ ./manage.py shell
  Python 2.7.3 (default, Apr 10 2013, 05:46:21)
  [GCC 4.6.3] on linux2
  Type "help", "copyright", "credits" or "license" for more information.
  (InteractiveConsole)
  >>> from django.core.cache import cache
  >>> cache
  <django_pylibmc.memcached.PyLibMCCache object at 0x8c93c4c>
  >>> cache.set('test','Hello World')
  True
  >>> cache.get('test')
  'Hello World'
  >>> exit()
  vagrant@precise32:/vagrant/makahiki$ unset MAKAHIKI_USE_MEMCACHED
  vagrant@precise32:/vagrant/makahiki$ export LD_LIBRARY_PATH=$LD_LIBRARY_PATH_OLD
  vagrant@precise32:/vagrant/makahiki$ unset LD_LIBRARY_PATH_OLD
  vagrant@precise32:/vagrant/makahiki$ sudo service memcached stop
  Stopping memcached: memcached.

If running "manage.py shell" causes the error::

  django.core.cache.backends.base.InvalidCacheBackendError: Could not import pylibmc.

then the LD_LIBRARY_PATH may not be set correctly in makahiki_env.sh. This error 
occurs when MAKAHIKI_USE_MEMCACHED=True but LD_LIBRARY_PATH does not include 
the location of pylibmc.

If any of the following errors occur, then Memcached is not working:

  * cache prints a blank to the console, or cache is a 
    "django.core.cache.backends.dummy.DummyCache object."
  * cache.set returns False.
  * cache.get returns False or causes a segmentation fault.
  
If so, make sure environment variables are set and Memcached is running.

Configuring Memcached For The First Time
----------------------------------------

Memcached is a backend cache for the Makahiki web server. 
Configuring memcached is optional.

Run /vagrant/vagrant/makahiki_env_memcached_append.sh to add some code to 
the end of the /home/vagrant/makahiki_env.sh file::

  vagrant@precise32:~$ sh /vagrant/vagrant/makahiki_env_memcached_append.sh

If the file is the same as the one created by the bootstrap.sh script, lines 
will be appended automatically, with the result [Succeeded]. 

If the makahiki_env_memcached_append.sh script has been run already but no 
changes have been made, the script will do nothing and output the result 
[Already completed].

If you have made other changes to makahiki_env.sh between the time the virtual 
machine was created and now, the script will ask permission to append to the 
file instead of copying over it::

  WARNING! /home/vagrant/makahiki_env.sh file is different from expected file.
  Append settings anyway? (Result may contain duplicate lines.) [Y/n]

If you answer ``n`` the script's result will be [Cancelled].
Answer ``Y`` to add these lines to the end of makahiki_env.sh::

  export MAKAHIKI_USE_MEMCACHED=True
  # Don't add libmemcached paths more than once
  if [ ! $LIBMEMCACHED_PATHS_ADDED ];
      then
          export LD_LIBRARY_PATH=/usr/local/lib:/usr/lib:$LD_LIBRARY_PATH
          export LIBMEMCACHED_PATHS_ADDED=True
  fi

If the operation succeeds, the result will be [Succeeded].

Source /home/vagrant/.bashrc to apply changes::

  vagrant@precise32:~$ source /home/vagrant/.bashrc

On Vagrant, the memcached service should run automatically once installed by 
the provisioning script. If it does not run, start it manually::

  vagrant@precise32:~$ sudo service memcached start

On Ubuntu, the memcached service should run automatically at startup.

To test this, shut down the virtual machine, then restart it::

  vagrant@precise32:~$ sudo shutdown -h now
  -- output omitted --
  Connection to 127.0.0.1 closed by remote host.
  Connection to 127.0.0.1 closed.

  > vagrant up --no-provision
  -- output omitted --
  > vagrant ssh

.. warning:: Do not use ``sudo shutdown -r now`` in Vagrant. This will 
   restart the virtual machine without mounting the /vagrant shared folder.

After the restart, you should be able to test memcached without setting any 
environment variables:: 

  vagrant@precise32:~$ cd /vagrant/makahiki
  vagrant@precise32:/vagrant/makahiki$ ./manage.py shell
  Python 2.7.3 (default, Apr 10 2013, 05:46:21)
  [GCC 4.6.3] on linux2
  Type "help", "copyright", "credits" or "license" for more information.
  (InteractiveConsole)
  >>> from django.core.cache import cache
  >>> cache
  <django_pylibmc.memcached.PyLibMCCache object at 0x8c93c4c>
  >>> cache == None
  False
  >>> cache.set('test','Hello World')
  True
  >>> cache.get('test')
  'Hello World'
  >>> exit()

If this test works, then the memcached service is running and will be used 
by Makahiki.


Disabling Memcached
-------------------

To disable memcached, edit makahiki_env.sh to set 
``MAKAHIKI_USE_MEMCACHED=False`` and comment out LD_LIBRARY_PATH settings::

  export MAKAHIKI_USE_MEMCACHED=False
  # Don't add libmemcached paths more than once
  #if [ ! $LIBMEMCACHED_PATHS_ADDED ];
  #    then
  #        export LD_LIBRARY_PATH=/usr/local/lib:/usr/lib:$LD_LIBRARY_PATH
  #        export LIBMEMCACHED_PATHS_ADDED=True
  #fi

Then stop the memcached service, and stop it from running at startup::

  vagrant@precise32:~$ sudo service memcached stop
  vagrant@precise32:~$ sudo update-rc.d -f memcached disable

The memcached service will no longer be used by Makahiki, and will no longer 
run at startup.

To test this, shut down the virtual machine, then restart it::

  vagrant@precise32:~$ sudo shutdown -h now
  -- output omitted --
  Connection to 127.0.0.1 closed by remote host.
  Connection to 127.0.0.1 closed.

  > vagrant up --no-provision
  -- output omitted --
  > vagrant ssh

After starting the new SSH session, test memcached once again::

  vagrant@precise32:~$ cd /vagrant/makahiki
  vagrant@precise32:/vagrant/makahiki$ ./manage.py shell
  Python 2.7.3 (default, Apr 10 2013, 05:46:21)
  [GCC 4.6.3] on linux2
  Type "help", "copyright", "credits" or "license" for more information.
  (InteractiveConsole)
  >>> from django.core.cache import cache
  >>> cache
  <django.core.cache.backends.dummy.DummyCache object at 0x964b72c>
  >>> cache.set('test','Hello World') == None
  True
  >>> exit()
  vagrant@precise32:/vagrant/makahiki$

Cache should be a DummyCache, and ``cache.set('test','Hello World') == None`` 
should return True.

Enabling Memcached
------------------

Edit makahiki_env.sh to set ``MAKAHIKI_USE_MEMCACHED=True``, and uncomment the 
LD_LIBRARY_PATH settings::
   
  export MAKAHIKI_USE_MEMCACHED=True
  # Don't add libmemcached paths more than once
  if [ ! $LIBMEMCACHED_PATHS_ADDED ];
      then
          export LD_LIBRARY_PATH=/usr/local/lib:/usr/lib:$LD_LIBRARY_PATH
          export LIBMEMCACHED_PATHS_ADDED=True
  fi


Source ~/.bashrc to apply the changes::

  vagrant@precise32:~$ source ~/.bashrc

Start the memcached service, and set it to run at startup::

  % sudo service memcached start
  % sudo update-rc.d -f memcached enable




