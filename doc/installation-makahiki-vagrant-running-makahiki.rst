.. _section-installation-makahiki-vagrant-running-makahiki-vagrant:

Running Makahiki on Vagrant
===========================

This article describes maintenance tasks for the Makahiki database, 
and describes the process for starting and stopping the Makahiki web 
server.

.. note:: In this article, a "``%``" prompt indicates that a command can be performed from 
   any working directory in the virtual machine. Directories 
   are specified otherwise.

Initialize Makahiki
-------------------

The provisioning script that was run when the virtual machine was started for 
the first time initialized the database. This section describes how to 
initialize the database again.

.. warning:: Running the initialize_instance.py script will:

     * Install and/or update all pip-installed packages required by Makahiki.
     * Reinitialize the database contents and perform any needed database migrations.
     * Initialize the system with data.
     * Set up static files.

   This script should be run only a single time in production scenarios, because 
   any configuration changes that an administrator makes will be lost if the 
   initialize_instance.py script is used again.

   The script initializes the Makahiki database and populates it with default 
   information and users.

If the server is running in your terminal, close it::

  (type control-c in the shell running the makahiki server process)

Change to the /vagrant/makahiki directory if you are not in it. 
(The ``%`` sign represents a command prompt and indicates that this can be done from 
any directory on the virtual machine)::

  % cd /vagrant/makahiki
  
Next, run the initialize_instance.py script::
  
  vagrant@precise32:/vagrant/makahiki$ ./scripts/initialize_instance.py --type default

You will need to answer ``Y`` to the question ``Do you wish to continue (Y/n)?``.

Example output of the initialize_instance.py script::

  vagrant@precise32:/vagrant/makahiki$ ./scripts/initialize_instance.py --type default
  installing requirements...
  WARNING: This command will reset the database. All existing data will be deleted. This process is irreversible.

  Do you wish to continue (Y/n)? Y
  resetting the db...
  DROP DATABASE
  DROP ROLE
  CREATE ROLE
  CREATE DATABASE
  syncing and migrating db...
  collecting static and media files...
  loading base data...
  loading fixture base_badges.json...
  loading fixture base_help.json...
  loading fixture base_notifications.json...
  loading fixture base_pages.json...
  loading fixture base_quests.json...
  loading fixture base_schedule.json...
  loading fixture base_settings.json...
  loading fixture smartgrid_library.json...
  setting up default data...
  set up 1 one-week rounds, starting from today.
  loading fixture default_challenge.json...
  loading fixture default_designer.json...
  loading fixture default_prizes.json...
  loading fixture default_smartgrid.json...
  loading fixture default_teams.json...
  0 test users deleted.
  4 test users created.
  event dates adjusted to round date.
  created initial resource usages for all teams.
  created test baselines for all teams.
  created goal settings for all teams.
  makahiki cache cleared.
  vagrant@precise32:/vagrant/makahiki$

If the script experiences errors while connecting to the database, see 
:ref:`section-installation-makahiki-vagrant-troubleshooting`.

Update the Makahiki Instance
----------------------------

Makahiki is designed to support post-installation updating of your configured 
system when bug fixes or system enhancements become available.

If the server is running in your terminal, close it::

  (type control-c in the shell running the makahiki server process)

Change to the vagrant directory if you are not in it.
(The ``%`` sign represents a command prompt and indicates that 
this can be done from any directory on the virtual machine)::

  % cd /vagrant

Download the updated source code into the Makahiki installation::

  vagrant@precise32:/vagrant$ git pull origin master

Change your directory to vagrant/makahiki::

  vagrant@precise32:/vagrant$ cd makahiki
  
Next, run the update_instance.py script::

  vagrant@precise32:/vagrant/makahiki$ ./scripts/update_instance.py

This updates the Makahiki instance based on any new files that have 
been added to the Git repository.

Example output of the update_instance.py script::

  vagrant@precise32:/vagrant/makahiki$ ./scripts/update_instance.py
  installing requirements...
  syncing and migrating db...
  collecting static and media files...
  vagrant@precise32:/vagrant/makahiki$

Start the Makahiki Server
-------------------------

This guide assumes you are in the directory /vagrant/makahiki on the 
virtual machine.

Makahiki's manage.py script provides two web servers: runserver and gunicorn.
runserver is better for development, and gunicorn is better for production use. 

It is important to bind the server to IP 0.0.0.0 (accepts incoming connections 
on any IP address) and port 8000 in order to work with the port forwarding 
settings in the Vagrantfile.

To start the server with manage.py::

  vagrant@precise32:/vagrant/makahiki$ ./manage.py runserver 0.0.0.0:8000

Example output of starting runserver::

  vagrant@precise32:/vagrant/makahiki$ ./manage.py runserver 0.0.0.0:8000
  Validating models...

  0 errors found
  Django version 1.4, using settings 'settings'
  Development server is running at http://0.0.0.0:8000/
  Quit the server with CONTROL-C.

To start the server with gunicorn::

  vagrant@precise32:/vagrant/makahiki$ ./manage.py run_gunicorn -b 0.0.0.0:8000

Example output of starting gunicorn::

  vagrant@precise32:/vagrant/makahiki$ ./manage.py run_gunicorn -b 0.0.0.0:8000
  Validating models...
  0 errors found
  
  Django version 1.4, using settings 'settings'
  Server is running
  Quit the server with CONTROL-C.
  2013-10-11 01:59:41 [1399] [INFO] Starting gunicorn 0.13.4
  2013-10-11 01:59:41 [1399] [INFO] Listening at: http://0.0.0.0:8000 (1399)
  2013-10-11 01:59:41 [1399] [INFO] Using worker: sync
  2013-10-11 01:59:41 [1408] [INFO] Booting worker with pid: 1408

View the site in your host machine's web browser at http://192.168.56.4:8000.

Log in with the username and password specified in makahiki_env.sh. The  
username is "admin" and the password is "admin" unless these settings were 
changed after installation. 

To stop either of the servers, type control-c in the virtual machine terminal.

Testing the Server Without a Web Browser
****************************************

If you cannot reach the web server from the host machine, you will need to 
use wget to test the server on the virtual machine::

  vagrant@precise32:/vagrant/makahiki$ ./manage.py runserver 0.0.0.0:8000 &
  Validating models...
  
  Development server is running at http://127.0.0.1:8000/
  Quit the server with CONTROL-C.
  vagrant@precise32:/vagrant/makahiki$ (press "Enter" here)
  vagrant@precise32:/vagrant/makahiki$ cd ~/
  vagrant@precise32:~$ mkdir test
  vagrant@precise32:~/test$ cd test
  vagrant@precise32:~/test$ wget http://127.0.0.1:8000
  --2013-08-09 11:19:25--  http://127.0.0.1:8000/
  Connecting to 127.0.0.1:8000... connected.
  HTTP request sent, awaiting response... 302 FOUND
  Location: http://127.0.0.1:8000/landing/ [following]
  [09/Aug/2013 11:19:26] "GET / HTTP/1.0" 302 0
  --2013-08-09 11:19:26--  http://127.0.0.1:8000/landing/
  Connecting to 127.0.0.1:8000... connected.
  HTTP request sent, awaiting response... 200 OK
  Length: unspecified [text/html]
  [09/Aug/2013 11:19:26] "GET /landing/ HTTP/1.0" 200 6181
  Saving to: “index.html"
  
      [ <=>                                   ] 6,181       --.-K/s   in 0s

  2013-08-09 11:19:26 (192 MB/s) - “index.html" saved [6181]

If your HTTP response is "200 OK," the server is running correctly. You can 
delete the "test" directory when you are done.

Because the server was started in the background with ``&``, you cannot stop 
it with control-c. You will need to find the PIDs of its processes first::

  % ps ax | grep manage.py
  21791 tty1     S     0:00 python ./manage.py runserver
  21798 tty1     Sl    0:52 /root/.virtualenvs/makahiki/bin/python ./manage.py ru
  nserver
  21893 tty1     S+    0:00 grep manage.py
  % kill -9 21791 21798
  % 
  [1]+  Killed                 ./manage.py runserver  (wd: ~/makahiki/makahiki)
  (wd now: <your-working-directory>)

The PID of a given process will be different each time it runs. ``kill -9 <PID>`` 
forces the OS to stop the process with the specified PID. Kill the ``python ./manage.py runserver`` 
and ``/root/.virtualenvs/makahiki/bin/python ./manage.py runserver`` processes 
to stop the server.




