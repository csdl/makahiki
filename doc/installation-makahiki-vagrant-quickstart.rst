.. _section-installation-makahiki-vagrant-quickstart:

Quick Start Guide: Makahiki on Vagrant 
======================================

If you have not already installed VirtualBox and Vagrant and downloaded the Makahiki source code, 
complete :ref:`section-installation-makahiki-vagrant-environment-setup` before completing this section.

.. note::
   In this article, a "``>``" indicates a command prompt on the host OS. Commands appearing after a 
   "``>``" should work on Windows, OS X, and Linux unless otherwise stated.
   
.. note::
   The "``makahiki>``" prompt indicates that the working directory is in the 
   "Makahiki directory" on the host machine. The file path preceding "makahiki"
   (e.g., "``C:\Users\username\Vagrant\makahiki>``") will be different depending 
   on the location of the directory in the file system of the host OS.

If a Command Prompt (Windows) or Terminal (OS X and Linux) shell is not open on 
your host machine, open one.

Set up Makahiki in the Virtual Machine
--------------------------------------

In your Command Prompt or Terminal, switch your working directory to the
"makahiki" directory that was created in :ref:`section-installation-makahiki-vagrant-environment-setup`::

  > cd <path-to-makahiki>/makahiki
  
Replace ``<path-to-makahiki>`` with the file system path to the "makahiki" directory. On Windows, if 
your "makahiki" directory is located at ``C:\Users\username\Vagrant\makahiki``, you would use the command 
``cd C:\Users\username\Vagrant\makahiki`` here. On Linux, if your "makahiki" directory is at 
``/home/username/vagrant/makahiki``, you would use the command ``cd /home/username/vagrant/makahiki`` here.

A Windows example:

  .. figure:: figs/vagrant/windows-command-prompt-vagrant-switch.png
      :width: 580 px
      :align: center

The "makahiki" directory was created when you cloned the Git repository in 
:ref:`section-installation-makahiki-vagrant-environment-setup`. It contains the Vagrantfile which defines the settings 
of the Vagrant virtual machine. It also contains all of Makahiki's source code.

Use the ``vagrant up`` command to start the virtual machine for the first time::

  makahiki> vagrant up
  
.. warning:: Windows users may see multiple warnings while ``vagrant up`` is running for the first time.

     * **A Windows Firewall warning about vboxheadless.exe**: This application should be allowed.
     * **VirtualBox is attempting to make changes to the system**: This should be allowed. It is needed for Vagrant / VirtualBox host-only networking to work.
      
.. warning:: If your Vagrant version is less than 1.3.0, you are starting your 
   virtual machine for the first time, and you do not want to lose 
   your configuration, start Vagrant with ``--no-provision``::
   
     makahiki> vagrant up --no-provision

   In Vagrant versions prior to 1.3.0, each time Vagrant is started with 
   ``vagrant up``, it will run the ``run_bootstrap.sh`` provisioning script 
   specified in the Vagrantfile. This runs another script, bootstrap.sh, which:
   
     * Sets the system locale to en_US.UTF-8
     * Drops the PostgreSQL cluster data directory, **erasing all data in all databases**
     * Re-initializes the cluster data directory
     * Re-initializes the Makahiki database
   
The run_bootstrap.sh script logs the output of bootstrap.sh to a file in makahiki/vagrant/logs.
This file will be called "ubuntu_x86_<timestamp>.log," where **timestamp** is a 
string in the format yy-mm-dd-HH-MM-SS (year, month, day, hour, minute, second).

When the script finishes running, look at the last few lines of output::

  -------------------------------------------------------------------------------
  Configuration setup results:
  -------------------------------------------------------------------------------
  1. Copying locale settings to /etc/bash.bashrc: [Succeeded]
  2. Copying settings to pg_hba.conf: [Succeeded]
  3. Creating /home/vagrant/makahiki_env.sh: [Succeeded]
  4. Appending to /home/vagrant/.bashrc: [Succeeded]
  -------------------------------------------------------------------------------
  
If the value for a task is "Succeeded" or "Already completed," continue to the 
next step. If the value for a task is "Failed," go to :ref:`section-installation-makahiki-vagrant-troubleshooting`.

Connect to the Vagrant Virtual Machine
--------------------------------------

Start an SSH session with the Ubuntu virtual machine::

  makahiki> vagrant ssh

An Ubuntu command prompt will be displayed:: 

  vagrant@precise32:~$

Start the Server
----------------

.. note:: The /vagrant directory that contains /vagrant/makahiki is a special directory 
   that is synchronized with the "makahiki" directory (folder) on your host OS. 
   
     * Any file added to ``/vagrant`` on the virtual machine will be added to ``makahiki`` on the host machine. 
     * Any file added to ``makahiki`` on the host machine will be added to ``/vagrant`` on the virtual machine.

To start one of the two web servers that Makahiki provides, switch to the 
/vagrant/makahiki directory::

  vagrant@precise32:~$ cd /vagrant/makahiki
  
The two servers are runserver, which is better for development, and gunicorn, 
which is better for production use.
  
To start the runserver server::

  vagrant@precise32:/vagrant/makahiki$ ./manage.py runserver 0.0.0.0:8000
  
Example output of starting runserver::

  vagrant@precise32:/vagrant/makahiki$ ./manage.py runserver 0.0.0.0:8000
  Validating models...

  0 errors found
  Django version 1.4, using settings 'settings'
  Development server is running at http://0.0.0.0:8000/
  Quit the server with CONTROL-C.

To start the gunicorn server::

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

Verify that Makahiki Is Running
-------------------------------

Open a browser on the host machine and go to http://192.168.56.4:8000 to see 
the landing page, which should look similar to this:

  .. figure:: figs/vagrant/kukui-cup-demo-landing.png
      :width: 600 px
      :align: center

In the virtual machine, stop either server with control-c when you are finished::

  vagrant@precise32:/vagrant/makahiki$ (type control-c in the shell running the makahiki server process)

If the site is not reachable from your host machine, or your host machine is headless 
and has no GUI, refer to :ref:`section-installation-makahiki-vagrant-running-makahiki-vagrant` 
and follow the section on **Testing the Server Without a Web Browser**.

Makahiki Maintenance Tasks
--------------------------

The basic installation of Makahiki is now complete.

To learn how to reset or update the Makahiki database, continue to 
:ref:`section-installation-makahiki-vagrant-running-makahiki-vagrant`.

Exit Your SSH Session
---------------------

When you are finished working with the Vagrant virtual machine,
end your SSH session by typing ``exit`` in the SSH terminal::

     vagrant@precise32:/vagrant/makahiki$ exit 

On your host OS, you will be returned to the terminal that started the SSH session.
