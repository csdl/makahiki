.. _section-installation-makahiki-vagrant-eclipse:

Using Eclipse to Develop With Makahiki on Vagrant
=================================================

Using Eclipse to develop software with Makahiki is optional. However, 
``.project`` and ``.pydevproject`` files are provided for the convenience 
of Eclipse users in the ``makahiki/makahiki`` directory.

This section assumes that the user has followed the instructions in 
:ref:`section-installation-makahiki-vagrant-quickstart` to configure the 
Vagrant virtual machine.

Eclipse is an Integrated Development Environment (IDE) that requires Java.
Eclipse is available for Windows, OS X, and Linux at http://eclipse.org.

You will not be able to run Django-based Python files on your host OS.
You will need to run them in Vagrant after editing them in Eclipse on your 
host OS.

Installing Eclipse Prequisites
------------------------------

Prequisites for the Eclipse installation are listed below:
  * Python 2.7.3 or later (but not Python 3): Required
  * Java JRE or JDK (Java 6 or newer): Required
  * Eclipse IDE (Eclipse 4.2 Juno or newer recommended): Required
  * PyDev Eclipse Add-on: Required
  * Configure Line Endings and Character Encodings: Required
  * Eclipse Add-ons: Web, XML, Java EE and OSGi Enterprise Development (Optional)
      * Eclipse Web Developer Tools (HTML/XHTML/CSS editors)
      * JavaScript Development Tools (JavaScript editor)
  * Eclipse Add-ons: Remote System Explorer (Optional)
      * Remote System Explorer End-User Runtime
      * Remote System Explorer User Actions
  * Set Hidden Files and Folders as Visible (Optional)

The following sections describe how to install or configure them.

Prerequisites: Python
*********************

Follow the instructions at `Python.org`_ to download and install a Python 
binary on your host OS. To develop software with Makahiki, you must install 
a version of Python that is 2.7.3 or higher (but not Python 3).

.. _Python.org: http://python.org

Prerequisites: Eclipse 
**********************

Eclipse is an Integrated Development Environment (IDE) available 
from `eclipse.org`_. 

Follow the `Eclipse.org installation instructions`_ to install Eclipse 
(and Java if necessary) on your host machine.

Eclipse requires that the Java JRE (Java 6 or later) be installed on the host 
machine. The full Java JDK (which includes the JRE) is useful for Java 
development, but it is **not** required for Makahiki development.

.. _eclipse.org: http://eclipse.org
.. _Eclipse.org installation instructions: http://wiki.eclipse.org/Eclipse/Installation 

Prerequisites: PyDev
********************

PyDev is an Eclipse add-on that is required for Python development. 
Follow the `Pydev.org installation instructions`_ to install PyDev for your Eclipse 
installation.

.. _Pydev.org installation instructions: http://pydev.org

Prerequisites: Configure Line Endings and Character Encodings 
*************************************************************

It is very important to set these preferences before editing any of the 
project files or creating new ones.

1. In Eclipse, go to **Window** --> **Preferences**.
2. Go to **Preferences** --> **General** --> **Workspace**. Click once on **Workspace**.
3. In **Workspace**: 
     * Under "Text File Encoding," select "Other," then select "UTF-8" from the dropdown menu. 
     * Under "New Text File Line Delimiter," select "Other," then select "Unix" from the dropdown menu.
     
4. Click "Apply" when finished.

Prequisites: Web Development Add-Ons 
************************************

The "Web, XML, Java EE and OSGi Enterprise Development" set of add-ons is 
optional. Makahiki uses Django and contains JavaScript, HTML, and CSS files, 
so general web development tools are useful.

1. Open Eclipse. In the **Help** menu, select "Install New Software."
2. For the "Work with:" dropdown menu, select the "releases" URL that matches 
   your Eclipse version. For Eclipse 4.2 Juno, for example, this 
   would be "Juno - http://download.eclipse.org/releases/juno."
3. In the list of packages that appears below, click on the 
   arrow to the left of "Web, XML, Java EE and OSGi Enterprise Development."
   to expand the category. 
   * The "Eclipse Web Developer Tools" provide HTML/XHTML/CSS editors.
   * The "JavaScript Development Tools" provide a JavaScript (.js) editor.
4. Check the boxes for the add-ons you want to install. 
5. Click "Next," then "Next." You may need to agree to one or more licenses.
6. Restart Eclipse when prompted. After the restart, any new editors or 
   features will be installed and ready for use.

Prequisites: Remote Systems Explorer
************************************

The Remote Systems Explorer addons are optional. They are only required if 
you plan to connect to the Vagrant virtual machine from within Eclipse.

1. Open Eclipse. In the **Help** menu, select "Install New Software."
2. For the "Work with:" dropdown menu, select the "releases" URL that matches 
   your Eclipse version. For Eclipse 4.2 Juno, for example, this 
   would be "Juno - http://download.eclipse.org/releases/juno."
3. Type "remote" in the search bar and wait for the search to finish. 
   Check the boxes for the add-ons "Remote System Explorer End-User Runtime" 
   and "Remote System Explorer User Actions."
4. Click "Next," then "Next." You may need to agree to one or more licenses.
5. Restart Eclipse when prompted. After the restart, any new editors or 
   features will be installed and ready for use.

Prerequisites: Set Hidden Files and Folders as Visible
******************************************************

This step is optional.

1. Open Eclipse. If you are not in the PyDev perspective,
   click on the "Open Perspective" button, and select PyDev.
2. In the "Package Explorer" sidebar, click on the white down-pointing arrow 
   In this menu, click "Customize View."
3. In the "Available Customizations" popup that appears, uncheck the checkbox 
   for ".*resources," then click "OK."
4. The hidden files and folders that start with a "." character (e.g., 
   ".project" and ".pydevproject") should now be visible in Eclipse.

Import Makahiki as an Eclipse Project
-------------------------------------

Your Vagrant virtual machine and its .vagrant folder should be located at 
the top level of the cloned makahiki repository, where the Vagrantfile is.

Importing the makahiki directory as an Eclipse project when the makahiki 
directory is also the Vagrant shared directory allows you to modify Makahiki 
source files on your host machine, then deploy the changes in your Vagrant 
virtual machine immediately.

1. Open Eclipse.
2. When prompted to select a workspace, click "Browse." In the file system's 
   browser (Windows Explorer, OS X Finder, etc.), select the directory that 
   you cloned the Makahiki repository into earlier, then click "OK."
   
   For example:
   
     * Makahiki was cloned into: C:/Users/Tester/Vagrant
     * Workspace directory should be: C:/Users/Tester/Vagrant. 

3. Eclipse will open. In the menu, click File --> Import.
     3a. Click the arrow to expand "General," then select 
         "Existing Projects Into Workspace." Click "Next."
     3b. Uncheck the "Copy Projects into Workspace" checkbox.
         Select the ``makahiki/makahiki`` directory as the root directory.
         
         For example:
        
           * Makahiki was cloned into: ``C:/Users/Tester/Vagrant``
           * Project root directory should be: ``C:/Users/Tester/Vagrant/makahiki/makahiki``
        
     3c. Check the checkbox for "makahiki" when it appears. Click "Finish."
4. Assuming that you installed PyDev, you will receive the warning:
   "It seems that the Python interpreter is not currently configured."
   Select "Auto config" if your Python interpreter is on your operating 
   system's PATH. Otherwise, use "Manual config" to select it manually. 
   These instructions assume you selected "Auto config."
5. If you selected "Auto config," you will get a "Selection needed" popup.
   The defaults are usually fine. Click "OK" to continue. 
6. You will be shown the "Interpreter - Python" menu.
   Click "Apply" to configure the Pythonpath for Eclipse.
   
   If you need to change these libraries later, go to 
   **Window** --> **Preferences** --> **PyDev** --> **Interpeter - Python**, 
   and select the "Libraries" tab.

Opening an SSH Session in Eclipse
----------------------------------

If you have installed the Remote System Explorer addons, you can start an SSH 
session to the Vagrant virtual machine from within Eclipse. The following steps 
involve the Remote System Explorer perspective.

In the Perspectives toolbar (upper-left-hand corner), click 
"Open Perspective." Select "Remote System Explorer."

If you want to view your project files, you can switch back to the PyDev 
perspective, or expand the "Local" --> "Local Files" directory tree in the 
Remote Systems tab to find the "makahiki" directory.

Start or Resume Vagrant in a Local Shell
****************************************

If you previously started your Vagrant virtual machine with ``vagrant up`` 
or ``vagrant resume``, you can skip this subsection.

1. In the "Remote System Explorer" tab, go to **Local** --> **Local Shells.**
   Right-click **Local Shells** and click "Launch Shell."
2. A "Remote Shell" tab will open. It runs the command shell on your host 
   machine, and commands are entered in the "Command" text field. 
   The current directory will be the directory you installed Eclipse into. 
   
   Switch to the top-level "makahiki" directory::
   
     > cd <path-to-makahiki>/makahiki
   
3. Check the virtual machine's status::
   
     > vagrant status
   
4. If your Vagrant virtual machine is shut down, start it::
   
     > vagrant up --no-provision
   
   If your Vagrant virtual machine is suspended instead, resume operation::
   
     > vagrant resume

Define and Start an SSH Session
*******************************

In the "Remote Systems" sidebar, click the button labeled "Define a connection to remote system."

1. In the "New Connection" popup, click "SSH Only" then click "Next."
2. Set the "Host name" to 127.0.0.1. Set the "Connection name" to anything you 
   like. Click "Finish."
3. The connection you defined will appear in the sidebar. Click the black arrow 
   to the left of it to expand it.
4. Right-click "SSH Shells" then click on "Properties."
5. Click "Subsystem" in the "Properties for Ssh shells" popup.
   Specify "Port" as "2222," and "User ID" as "vagrant." 
   When finished, click "OK."
6. Right-click "Ssh Terminals," then click "Connect." 
   Use the password "vagrant" when prompted.
7. If you see a warning similar to the below example, click "Yes" to continue::

     The authenticity of host 'LOCALHOST' can't be established. 
     RSA key fingerprint is e6:ad:1e:ee:15:53:7d:a6:ee:7c:aa:04:7a:ad:9a:9a.
     Are you sure you want to continue connecting?
     
8. If you see a popup similar to the below example, click "Yes" to continue::

     C:\Users\<username>\.ssh\known_hosts does not exist.
     Are you sure you want to create it?

9. In the Remote Systems sidebar, right-click "Ssh Terminals" and click 
   "Launch Terminal." This will open an SSH session terminal under 
   "Terminals."
   
   .. figure:: figs/vagrant/eclipse-remote-systems-explorer-ssh.png
      :width: 586 px
      :align: center

The SSH session can be used to run Makahiki scripts and the Makahiki web 
server, like a normal SSH session. Using "exit" or "logout" will close the 
session, but pressing Enter will launch a new session. Close the "Terminals" 
tab when you are done.

.. note:: As of Eclipse Juno, there is a bug in the Terminals display of 
   the Remote Systems Explorer. Pressing backspace will cause the terminal 
   prompt to disappear. Any text before your cursor position will also disappear. 
   The text remains typed in the virtual machine.

Enabling Makahiki Code Completion in Eclipse PyDev
--------------------------------------------------

Copying Makahiki Dependencies to the Shared Directory
*****************************************************

Assuming that the pip installation completed successfully when the 
provisioning script was run, the pip packages will be located in 
``/usr/local/lib/python2.7/dist-packages``.

Copy the dist-packages directory into the ``/vagrant/makahiki`` shared directory::

  vagrant@precise32:~$ cd /usr/local/lib/python2.7/dist-packages
  vagrant@precise32:/usr/local/lib/python2.7/dist-packages$ ls
  -- output omitted --
  vagrant@precise32:/usr/local/lib/python2.7/dist-packages$ cd ../
  vagrant@precise32:/usr/local/lib/python2.7$ cp -rL dist-packages /vagrant/makahiki/
  
On your host machine, the dist-packages directory will appear at 
``<path-to-makahiki>/makahiki/makahiki/dist-packages``, where ``<path-to-makahiki>`` is 
the file system's path to your makahiki installation.

Pythonpath and Code Completion Settings in Eclipse PyDev
********************************************************

Open Eclipse. Switch to or open the PyDev perspective if you are not in it.

1. In the PyDev perspective, click on 
   **Window** --> **Preferences** --> **PyDev** --> **Interpreter - Python**, 
   then select the "Libraries" tab.
2. Click on "New Folder."
3. In the "New Folder" window, click the white right-pointing arrow to expand 
   the directory tree. In the directory tree, browse to 
   ``<path-to-makahiki>/makahiki/makahiki/dist-packages``. 
   Click on the directory to highlight it, then click "OK."
4. In the main "Interpreter - Python" window, click "Apply" to rebuild 
   Eclipse's System Pythonpath.
5. In the PyDev perspective, click on 
   **Window** --> **Preferences** --> **PyDev** --> **Editor** --> **Code Completion**.
   These options may be useful:
   
     * Request completion on '.'?
     * Request completion on all letter chars and '_'?
   
6. To test the code completion, open any Python file. At the top of the file, 
   begin typing this line::
   
     from django.core.cache import File
   
   When the code completion popup opens, press Control+Space to switch  
   from "templates" to "default completions." "Default completions" 
   gives you a list of suggested package modules, while "templates" 
   gives you common Python keywords. Use Control+Space to cycle between 
   the two.
   
If imports are still marked as not found, you may need to refresh the project 
before changes to the Pythonpath take effect. Right-click the top-level
makahiki folder in Eclipse, and click "Refresh."

.. warning::

  * Code completion does not always mean that a Python script will run correctly or safely in Eclipse on the host machine (as opposed to the virtual machine).
  * Environment variables may not have the right values on the host OS.
  * Shell commands and system calls may fail if your host OS is different from the virtual machine OS.
  * If your host OS is Linux / Unix-based (especially Ubuntu or any distro 
    that is based on Debian) and has some of the same applications, 
    running any script in Eclipse that makes system calls may result in the 
    script's effects being applied to your host operating system. 

Remote Debugging in Eclipse PyDev
---------------------------------

The PyDev addon contains a Remote Debugger feature that allows programs 
started outside of Eclipse to be debugged from within Eclipse. This allows 
Python scripts on the virtual machine to be debugged in Eclipse on the host 
machine.

For more information about the remote debugger, refer to the 
`PyDev remote debugger documentation`_. 

.. _PyDev remote debugger documentation: http://www.pydev.org/manual_adv_remote_debugger.html.

.. warning::

   Using the Remote Debugger requires the process running the script on the 
   virtual machine to be able to communicate with PyDev on port 5678.

   Windows users, depending on their settings, may need to disable the Windows 
   Firewall completely for the Remote Debugger to work. Disabling the Windows 
   Firewall requires administrative privileges. It is a security risk and 
   should ideally be done on a machine not connected to any networks (or at 
   least any unsecured and/or public networks).

   Similarly, Linux and OS X users may need to change their firewall settings if 
   they want to use this feature. This usually requires administrative privileges 
   on the host machine.

Remote Debugger Demonstration
*****************************

Run the demonstration class to see the remote debugger in action:

1. On the host machine, look for the directory you installed Eclipse into 
   (the directory that contains the "eclipse" directory). In this directory, 
   navigate to ``eclipse/plugins/``.
2. Copy the directory with a name of the form 
   ``org.python.pydev_<version number X.X.X>.<nine digits representing build date>``
   (e.g., org.python.pydev_2.7.5.2013052819) to the 
   ``<path-to-makahiki>/makahiki/makahiki`` directory.
3. In Eclipse, open the Debug perspective.
4. In the top button menu bar (below the menu bar that contains "File"),
   search for a bug icon with a "P" next to it. The mouseover text for 
   the icon is "PyDev: Start the pydev server":
   
     .. figure:: figs/vagrant/eclipse-pydev-server-start-button.png
        :width: 186 px
        :align: center
   
   Click this. In the Debug tab, icons for the "Debug Server [Python Server]" 
   will appear. In the Console tab, the phrase "Debug Server at port: 5678" 
   will appear.
5. Switch to the PyDev perspective. Navigate to ``makahiki/makahiki/remote-debugger-demo``. 
6. Open pydevd_demo.py. This is an example file that uses the PyDev debugger. 
7. Look at the two import statements at the beginning of the file. These 
   statements must be added to any file in this project that uses the 
   remote debugger::
   
     import sys;sys.path.append(os.pardir + os.sep + r'org.python.pydev_2.7.5.2013052819\pysrc')
     import pydevd
   
   Check that the path to org.python.pydev_#.#.#.##########\pysrc matches the 
   relative path from pydevd_demo.py to the directory copied into 
   makahiki/vagrant in Step 2. Edit it if it does not. 
8. Look for the "pydevd.settrace()." Each occurrence of pydevd.settrace() acts 
   as a breakpoint when the remote debugger is used.
9. Switch back to the Debug perspective. Run pydevd_demo.py in Eclipse.
10. pydevd_demo.py will appear under a item called "MainThread." Note the 
    value for "i" that appears in the Variables tab. Step through the 
    program using the debugger; "i" will be decremented as the loop runs. 
    Output from the program will appear in the Console tab.
    
    .. figure:: figs/vagrant/eclipse-debug-server-demo.png
        :width: 600 px
        :align: center
    
    
11. Leave Eclipse open in the Debug perspective. Open a Command Prompt or 
    Terminal, and SSH into your Vagrant virtual machine::
    
      > vagrant ssh
    
12. In Vagrant, switch to ``/vagrant/vagrant`` and run pydevd_demo.py::
    
      vagrant@precise32:~$ cd /vagrant/vagrant
      vagrant@precise32:/vagrant/vagrant$ python pydevd_demo.py
    
13. You should see the same debugging information appear as when you ran the 
    program locally. If it does not work, you may see Errno 110::
    
      socket.error: [Errno 110] Connection timed out
    
    If you see Errno 110, check your firewall settings.
14. When you are finished, right-click the Debug Server and click 
    "Terminate and remove" to stop the server and remove it from the tab.
    
If this does not work, you may need to set the location of the file 
to be tested in pydevd_file_utils.py. 

1. Navigate to the ``org.python.pydev_<version>`` directory you copied into 
   ``makahiki/makahiki`` earlier, then go to the pysrc directory. Open the 
   pydevd_file_utils.py file.
2. Follow the instructions at the beginning of the file to edit the 
   ``PATHS_FROM_ECLIPSE_TO_PYTHON`` variable's value to match the location 
   of your file on the host machine and on the virtual machine.

Adding Remote Debugging Code to a Python File
---------------------------------------------

To add the remote debugging functionality in pydevd_demo.py to any Python file:

1. Edit the file so that it includes two import statements: one to import the 
   pysrc directory, and one to import ``pydevd``.
2. Add ``pydevd.settrace()`` wherever you would insert a breakpoint in 
   normal Eclipse debugging. It can have up to 4 parameters set:
   
     * The first parameter, the IP address, must match the .1 address of the host-only network configured in the Vagrantfile.
     * The port, 5678, is the remote debugger's default port. To edit this setting, go to **Windows** --> **Preferences** --> **PyDev** --> **Debug**.
         * Edit "Connect timeout for debugger (ms)" to change the timeout setting.
         * Edit "Port for remote debugger" to change the port. Click "Apply" when finished.
     * stdoutToServer sends standard output to the Eclipse debug server.
     * stderrToServer sends standard error output to the Eclipse debug server.
     
3. Start the Debug Server in Eclipse.
4. Run the Python file that will be debugged.
5. When you are done debugging, remove the import statements and the 
   calls to ``pydevd.settrace()``.

If you experience problems other than Errno 110, you may need to edit ``PATHS_FROM_ECLIPSE_TO_PYTHON`` 
in pydevd_file_utils.py. If this is the case, you will need to change the file paths every time 
you debug a different file.




