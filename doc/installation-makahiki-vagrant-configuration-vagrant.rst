.. _section-installation-makahiki-vagrant-configuration-vagrant:

Configuring Vagrant Settings
============================

This section contains instructions for changing Vagrant settings related to 
the virtual machine used by Makahiki. 

See the `Vagrant documentation`_ for more information.

.. _Vagrant documentation: http://docs.vagrantup.com/v2/

Throughout this guide, a ``>`` indicates that a command is performed on the 
host OS. A ``%`` indicates that a command is performed on the virtual machine, 
and that the working directory in which the command is run does not matter.

Vagrant Commands
----------------

Some basic Vagrant commands are listed below:

  * ``vagrant up``: Start the virtual machine. If the virtual machine defined in the Vagrantfile does not exist, it will be created and the provisioning script will be run.
  
    * ``vagrant up --provision``: Start the virtual machine and force it to run the provisioning script.
  
  * ``vagrant reload``: Restart the virtual machine. Equivalent to ``vagrant halt`` followed by ``vagrant up``.
  
    * ``vagrant reload --provision``: Restart the virtual machine and force it to run the provisioning script.
  
  * ``vagrant suspend``: Freeze the current state of the virtual machine.
  * ``vagrant resume``: Reactivate a machine that has been suspended.
  * ``vagrant halt``: Attempt to shut down the virtual machine gracefully.
  
    * ``vagrant halt --force``: Force a shutdown. This is equivalent to pulling the plug.
     
  * ``vagrant status``: Show the status of the virtual machine.
  * ``vagrant destroy``: Deletes a virtual machine. The Vagrantfile is not deleted.

.. warning:: The descriptions above apply only to Vagrant 1.3.0 and later.
   On Vagrant versions before 1.3.0, the ``vagrant up`` and ``vagrant reload`` commands worked as follows:
   
   * ``vagrant up``: Start the virtual machine and run the provisioning script. If the virtual machine defined in the Vagrantfile does not exist, it will be created. 
   
     * ``vagrant up --no-provision``: Start the machine without provisioning it.
     
   * ``vagrant reload``: Restart the virtual machine and run the provisioning script. Equivalent to ``vagrant halt`` followed by ``vagrant up``.
   
     * ``vagrant reload --no-provision``: Restart the virtual machine without provisioning it.

.. note:: As of Vagrant 1.4.3, you may see the following warning when 
   running Vagrant commands::
   
     DL is deprecated, please use Fiddle
	 
   This is a known issue with Vagrant and will likely be fixed in a future release.
   The commands will still work correctly. See `Vagrant issue 2656`_.

You can only run commands for a given Vagrant virtual machine if your working 
directory is the directory that contains the virtual machine's Vagrantfile.

Vagrant virtual machines are linked to the directory which contains their Vagrantfile. 
If the same Vagrantfile is copied into another directory, the ``vagrant up`` command 
will create a new virtual machine.

.. _Vagrant issue 2656: http://github.com/mitchellh/vagrant/issues/2656

Re-Provisioning Vagrant
-----------------------

When the Vagrant virtual machine was created, a provisioning script was run.

.. warning:: Running the provisioning script **erases all databases** in the 
   PostgreSQL installation on the system, including the Makahiki database.

If you want to run the provisioning script again, you can do this in two ways.

Re-provision the Virtual Machine at Startup
*******************************************

In the makahiki/vagrant directory, start the virtual machine with "vagrant up --provision."
This will run the provisioning script designated in the Vagrantfile::

  > vagrant up --provision 

.. note: In Vagrant versions before 1.3.0, run this command instead::

   > vagrant up

.. note:: This error may occur during provisioning::

            dpkg-preconfigure: unable to re-open stdin: No such file or directory
          
          This does not affect the provisioning script and can be ignored.

Re-provision a Virtual Machine That is Already Running
******************************************************

Use the ``vagrant provision`` command in the host machine::

  > vagrant provision

Configure the RAM of the Virtual Machine
----------------------------------------

The default settings in the Vagrantfile for Makahiki allow the virtual machine 
to use up to 1536 MB (1.5 GB) of RAM. To change this, you will need to edit the 
Vagrantfile while the virtual machine is shut down.

In the virtual machine, if the web server is running, stop it by pressing 
Control-C in the SSH terminal. Then shut down the virtual machine to end the 
SSH session::

  % sudo shutdown -h now

To change the RAM allocated to the Virtualbox VM, edit the ``vb.customize`` 
line in the Vagrantfile by changing the number after the ``--memory`` flag::

    config.vm.provider :virtualbox do |vb|
      vb.customize ["modifyvm", :id, "--memory", 1536]
    end

After saving your changes, restart the VM and start the SSH session::

  > vagrant up --no-provision
  > vagrant ssh
 
.. note:: 
   As of Vagrant 1.3.0, the ``--no-provision`` option is redundant because Vagrant 
   no longer automatically runs the provisioning script when ``vagrant up`` is run. 
   It is only necessary if your Vagrant version is older than 1.3.0. 
   See the `Vagrant changelog`_ for more information.

.. _Vagrant changelog: https://github.com/mitchellh/vagrant/blob/master/CHANGELOG.md#130-september-5-2013

In the SSH session, switch to /vagrant/makahiki and start the server::

  vagrant@precise32:~$ cd /vagrant/makahiki 

To start the server with manage.py::

  vagrant@precise32:/vagrant/makahiki$ ./manage.py runserver 0.0.0.0:8000

To start the server with gunicorn::

  vagrant@precise32:/vagrant/makahiki$ ./manage.py run_gunicorn -b 0.0.0.0:8000

Configure Networking on the Virtual Machine
-------------------------------------------

By default, the Vagrantfile specifies the IP address 192.168.56.4 for the 
virtual machine's eth1 interface. This is part of a host-only network. It 
assumes the host machine has the first usable address in the 192.168.56.0/24 
subnet, 192.168.56.1.

If the Makahiki site is unreachable from the host machine after the web 
server is started, the 192.168.56.0/24 network may not be correct.

To fix this, check the IP addresses assigned to VirtualBox's networking 
interfaces.

  1. Open VirtualBox.
  2. Go to **File** --> **Preferences** to launch the **VirtualBox - Settings** window.
  3. In the left sidebar, click **Network**.
  4. Click on **VirtualBox Host-Only Ethernet Adapter** once to select it, and click the screwdriver icon (the icon which, when moused over, shows "Edit host-only network.")
  5. The **Host-only Network Details** window should show the following::
  
       IPv4 Address: 192.168.56.1
       IPv4 Network Mask: 255.255.255.0
     
     If the settings are different, you will need to change the settings 
     in the Vagrantfile to match. Continue to the next step.
  6. Open the Vagrantfile in a text editor. Look for the line::

       config.vm.network :private_network, ip: "192.168.56.4"

  7. Change the address in quotes after the ``ip:`` field to something 
     in the address range specified in **Host-only Network Details.**
     For example, if the "IPv4 Address" is 192.168.56.1 and the 
     "IPv4 Network Mask" is 255.255.255.0, the range of usable addresses is 
     192.168.56.1 - 192.168.56.254. VirtualBox reserves the first usable 
     address, 192.168.56.1, for the host machine. An explanation of IPv4 
     network addresses is beyond the scope of this guide.

  8. Switch to the directory holding the Vagrantfile. Then, reload the virtual 
     machine configuration::
     
       > cd <directory-containing-Vagrantfile>
       > vagrant reload --no-provision
       
     .. note:: 
        As of Vagrant 1.3.0, the ``--no-provision`` option is redundant because Vagrant 
        no longer automatically runs the provisioning script when ``vagrant reload`` is run. 
        It is only necessary if your Vagrant version is older than 1.3.0. 
        See the `Vagrant changelog`_ for more information.

        .. _Vagrant changelog: https://github.com/mitchellh/vagrant/blob/master/CHANGELOG.md#130-september-5-2013
  
  9. SSH into the virtual machine and check the network interfaces::
     
       > vagrant ssh
       Welcome to Ubuntu 12.04 LTS (GNU/Linux 3.2.0-23-generic-pae i686)
       
       * Documentation:  https://help.ubuntu.com/
       Welcome to your Vagrant-built virtual machine.
       Last login: Thu Aug  8 07:55:06 2013 from 10.0.2.2
       vagrant@precise32:~$ ifconfig
       eth0      Link encap:Ethernet  HWaddr 08:00:27:12:96:98
                 inet addr:10.0.2.15  Bcast:10.0.2.255  Mask:255.255.255.0
                 inet6 addr: fe80::a00:27ff:fe12:9698/64 Scope:Link
       -- output omitted -- 
       eth1      Link encap:Ethernet  HWaddr 08:00:27:fd:05:73
                 inet addr:192.168.56.4  Bcast:192.168.56.255  Mask:255.255.255.0
                 inet6 addr: fe80::a00:27ff:fefd:573/64 Scope:Link
       -- output omitted --
       lo        Link encap:Local Loopback
                 inet addr:127.0.0.1  Mask:255.0.0.0
                 inet6 addr: ::1/128 Scope:Host
       -- output omitted --
       vagrant@precise32:~$
     
     The eth0 interface is used for port forwarding.
     The eth1 interface should match the IP address you just configured.
     The lo interface is the loopback interface.
   
  10. Ping the host machine's "VirtualBox Host Adapter Network Address" from the virtual machine. Press Control-C (^C) to stop::

        vagrant@precise32:~$ ping 192.168.56.1
        PING 192.168.56.1 (192.168.56.1) 56(84) bytes of data.
        64 bytes from 192.168.56.1: icmp_req=1 ttl=128 time=1.49 ms
        64 bytes from 192.168.56.1: icmp_req=2 ttl=128 time=0.710 ms
        64 bytes from 192.168.56.1: icmp_req=3 ttl=128 time=0.609 ms
        64 bytes from 192.168.56.1: icmp_req=4 ttl=128 time=0.685 ms
        ^C
        --- 192.168.56.1 ping statistics ---
        4 packets transmitted, 4 received, 0% packet loss, time 3000ms
        rtt min/avg/max/mdev = 0.609/0.874/1.493/0.359 ms
        vagrant@precise32:~$
        
      If the ping succeeds, then networking is correctly configured.
      
  11. Add the new IP address to ALLOWED_HOSTS in settings.py::
  
        if MACHINE_IS_VAGRANT:
            ALLOWED_HOSTS = ['192.168.56.4']
            
      Change the IP address for ALLOWED_HOSTS to match the new IP address that you configured.
      For example, if the new address were 192.168.56.8, you would change the ALLOWED_HOSTS line 
      to ``ALLOWED_HOSTS = ['192.168.56.8']``.

From now on, you should use the IP address configured in the Vagrantfile 
to access the site when the webserver is running.

For more documentation of VirtualBox host-only networking, see `Chapter 06`_ of the VirtualBox manual.

.. _Chapter 06: http://www.virtualbox.org/manual/ch06.html
