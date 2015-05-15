.. _section-configuration-system-administration-memcached:

Configure Memcached
===================

About Memcached
---------------

`Memcached`_ is a memory object caching daemon that stores objects in memory to 
reduce the load on a database. This section explains how to configure Makahiki to use memcached as 
the backend cache for its web server.

.. note:: Memcached is optional. However, it is recommended that Memcached be configured on production servers.

These instructions assume that you have followed the instructions in :ref:`section-installation-makahiki-local-unix` to 
configure a Linux installation of Makahiki. It is also assumed that you are using a Bourne-type shell, which 
is the default on Linux.

.. _Memcached: http://memcached.org

Environment Variables
---------------------

Open the $WORKON_HOME/makahiki/bin/postactivate file. Add these lines to the end::

  export MAKAHIKI_USE_MEMCACHED=True
  # Don't add libmemcached paths more than once
  if [ ! $LIBMEMCACHED_PATHS_ADDED ];
      then
          export LD_LIBRARY_PATH=/usr/local/lib:/usr/lib:$LD_LIBRARY_PATH
          export LIBMEMCACHED_PATHS_ADDED=True
  fi

Next, ``workon makahiki`` to apply the changes::

  % workon makahiki

Continue to the next section to start the memcached service.

Start the memcached Service
---------------------------

Next, the memcached service must be started if it is not running::

  % sudo service memcached start
  
On Ubuntu, the memcached service will automatically run at startup. 
In Red Hat Enterprise Linux or CentOS systems, however, the user must use chkconfig to enable the service to run at startup::

  % sudo chkconfig memcached on

Verify Memcached Settings
-------------------------
To test your Memcached settings, switch to the makahiki virtual environment::

  % workon makahiki
  
Then, change to the makahiki/makahiki directory and run the manage.py shell::

  % cd ~/makahiki/makahiki
  % ./manage.py shell

This will open a Python shell. 

In the shell, run the below commands to test whether Memcached is configured and running::

  Python 2.7.3 (default, Apr 10 2013, 05:46:21) 
  [GCC 4.6.3] on linux2
  Type "help", "copyright", "credits" or "license" for more information.
  (InteractiveConsole)
  >>> from django.core.cache import cache
  >>> cache
  <django_pylibmc.memcached.PyLibMCCache object at 0xa669c0c>
  >>> cache.set('test','Hello World')
  True
  >>> cache.get('test')
  'Hello World'
  >>> exit()

If your output matches the example output shown above, then Memcached has been successfully configured and started.
If your output does not match or you experience errors, continue to the next section.

Troubleshooting
---------------

If running ``manage.py shell`` causes the error ``django.core.cache.backends.base.InvalidCacheBackendError: Could not import pylibmc``, 
then the LD_LIBRARY_PATH environment variable may not be set correctly in $WORKON_HOME/makahiki/bin/postactivate. 
This error occurs when ``MAKAHIKI_USE_MEMCACHED=True`` but LD_LIBRARY_PATH does not include the location of pylibmc.

If the ``manage.py shell`` starts correctly but one of the following errors occurs when you run the test commands, 
then memcached is not correctly configured:

* cache is a ``DummyCache object``
* ``cache.set('test','Hello World')`` returns ``False``
* ``cache.get('test')`` causes a segmentation fault or exits the Python shell

Verify that your postactivate settings for MAKAHIKI_USE_MEMCACHED and LD_LIBRARY PATH match 
the settings added in these instructions.

If you are testing memcached on your local machine, verify that the makahiki/makahiki/settings.py file
specifies the backend cache for location 127.0.0.1 as ``django_pylibmc.memcached.PyLibMCCache``.
The settings.py file should include the following lines::

    else:
        CACHES = {'default':
                    {'BACKEND': 'django_pylibmc.memcached.PyLibMCCache',
                     'LOCATION': '127.0.0.1',
                     'BINARY': True,
         }}

Disabling Memcached
-------------------

In $WORKON_HOME/makahiki/bin/postactivate, set ``MAKAHIKI_USE_MEMCACHED=False`` and 
comment out memcached environment variable settings::

  export MAKAHIKI_USE_MEMCACHED=False
  # Don't add libmemcached paths more than once
  #if [ ! $LIBMEMCACHED_PATHS_ADDED ];
  #    then
  #        export LD_LIBRARY_PATH=/usr/local/lib:/usr/lib:$LD_LIBRARY_PATH
  #        export LIBMEMCACHED_PATHS_ADDED=True
  #fi

Then ``workon makahiki`` to apply changes::

  % workon makahiki
  
Finally, stop the makahiki service, and stop it from running at startup.

Ubuntu users::

  % sudo service memcached stop
  % sudo update-rc.d -f memcached disable

RHEL and CentOS users::

  % sudo service memcached stop
  % sudo chkconfig memcached off

The ``manage.py shell`` tests should fail now::

  % ./manage.py shell
  Python 2.7.3 (default, Apr 10 2013, 05:46:21) 
  [GCC 4.6.3] on linux2
  Type "help", "copyright", "credits" or "license" for more information.
  (InteractiveConsole)
  >>> from django.core.cache import cache
  >>> cache
  <django.core.cache.backends.dummy.DummyCache object at 0x9ef470c>
  >>> cache.set('test','Hello World') == None
  True
  >>> exit()

Re-enabling Memcached
---------------------

In $WORKON_HOME/makahiki/bin/postactivate, set ``MAKAHIKI_USE_MEMCACHED=True`` and 
uncomment the memcached environment variable settings::

  export MAKAHIKI_USE_MEMCACHED=True
  # Don't add libmemcached paths more than once
  if [ ! $LIBMEMCACHED_PATHS_ADDED ];
      then
          export LD_LIBRARY_PATH=/usr/local/lib:/usr/lib:$LD_LIBRARY_PATH
          export LIBMEMCACHED_PATHS_ADDED=True
  fi

Then ``workon makahiki`` to apply changes::

  % workon makahiki
  
Finally, start the makahiki service, and set it to run at startup.

Ubuntu users::

  % sudo service memcached start
  % sudo update-rc.d -f memcached enable

RHEL and CentOS users::

  % sudo service memcached start
  % sudo chkconfig memcached on
  
The ``manage.py shell`` tests should work correctly now.



