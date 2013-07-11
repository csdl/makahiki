import subprocess
import re
import os
import shlex
import datetime

def rpm_check(packagename):
    """
    Uses "rpm -qa <packagename>" to check if a package is installed.
    It does not check the version. Returns True if it is installed, and 
    False if it is not.
    """
    rpm_regex = re.compile("(%s)(.)+(\.)(.)+" % packagename)
    result = False
    rpm_qa = subprocess.check_output(shlex.split("rpm -qa %s" % packagename), stderr=subprocess.STDOUT)
    if rpm_regex.match(rpm_qa):
        result = True
    return result

def python_package_check(packagename, expected_response):
    """
    Checks if <python-packagename> is installed as a site package 
    using <packagename> --version. Returns True if it is, and 
    False if it is not. The <packagename> may need to be a 
    filepath if it refers to a package that is installed under 
    an altinstall.
    
    It assumes that the version is represented by <packagename> 
    followed by at least two integer sequences separated 
    by a single period (e.g., "foo 11.11.11").
    
    Parameters:
    1. packagename: A string representing a Python package name.
       If the package is part of an altinstall, use its name 
       under the altinstall (e.g., a Python 2.7.3 altinstall 
       would check for "pip-2.7").
    2. expected_response: Allows for a package's --version command 
       to output a name different than <packagename>.
    """
    compare_result = False
    try:
        output = subprocess.check_output(shlex.split("%s --version" % packagename), stderr=subprocess.STDOUT)
        lines = output.split("\n")
        # Expects versions to have at least two parts (e.g., 3.0).
        version_string = re.compile("(%s )(\d)+(\.(\d)+)+(.)*" % expected_response)
        line0_result = version_string.match(lines[0])
        if not line0_result:
            compare_result = False
        else:
            compare_result = True
    except OSError as ose:
        # Assume not installed
        compare_result = False
    return compare_result

def postgresql91_repocheck():
    """
    Checks if the pgdg-redhat91-9.1-5.noarch.rpm repo (pgdg91) is installed.
    Returns True if it is listed by yum repolist, and False if it not.
    """
    result = subprocess.check_output(shlex.split("yum repolist | grep pgdg91"), stderr=subprocess.STDOUT)
    lines = result.split("\n")
    repo_shortname = re.compile("(pgdg91)(.)*")
    repo_match = False
    for line in lines:
        linematch = repo_shortname.match(line)
        if linematch:
            repo_match = True
            break
    return repo_match

def virtualenvwrapper_check(packagepath):
    """
    Checks if virtualenvwrapper is installed in the system. Returns True if 
    virtualenvwrapper is installed, and False if it is not.
    
    Parameters:
    1. packagepath: The path to the virtualenvwrapper package. For a Python 2.6.6 default install,
       for example, the package might be in /usr/bin/virtualenv.
    """
    compare_result = False
    try:
        output = subprocess.check_output(shlex.split("%s --version" % packagepath), stderr=subprocess.STDOUT)
        lines = output.split("\n")
        # Expects versions to have at least two parts (e.g., 3.0).
        version_string = re.compile("(\d)+(\.(\d)+)+")
        line0_result = version_string.match(lines[0])
        if not line0_result:
            compare_result = False
        else:
            compare_result = True
    except OSError as ose:
        # Assume not installed
        compare_result = False
    return compare_result

def termination_string():
    """
    Gets the current system time and appends it to a termination notice.
    """
    now = datetime.datetime.now()
    time = now.strftime("%Y-%m-%d %H:%M:%S")
    end_time = "Script exiting at %s\n" % time
    return end_time

def yum_install(packagename, logfile):
    """
    Installs <packagename> with "yum install -y <packagename>" and then 
    checks whether or not the package installed correctly. Output is logged to 
    the logfile.
    
    Parameters:
        1. packagename: A string with the name of the package to be installed.
        2. logfile: The file to write output to.
    Returns a tuple, result:
    result[0] is True if the installation succeeded and False if it did not.
    result[1] is a reference to the logfile passed in as parameter 2.
    """
    success = False
    logfile.write("%s will be installed.\n" % packagename)
    print ("%s will be installed.\n" % packagename)
    logfile.write("yum install -y %s\n" % packagename)
    print "yum install -y %s\n" % packagename
    try:
        install_output = subprocess.check_output(["yum", "install", "-y", packagename], stderr=subprocess.STDOUT)
        logfile.write(install_output + "\n")
        print install_output + "\n"
        is_installed = rpm_check(packagename)
        if is_installed:
            logfile.write("%s installed successfully.\n" % packagename)
            print "%s installed successfully.\n" % packagename
            # Flush the buffer and force a write to disk after each successful installation
            logfile.flush()
            os.fsync(logfile)
            success = True
        else:
            logfile.write("Package %s failed to install.\n" % packagename)
            print "Package %s failed to install.\n" % packagename
            end_time = termination_string()
            logfile.write(end_time)
            print end_time
            success = False
    except subprocess.CalledProcessError as cpe:
        # Print and log the error message
        logfile.write("CalledProcessError: ")
        print "CalledProcessError: "
        logfile.write(cpe.output)
        print cpe.output
        closing = "\nPackage %s failed to install.\n" % packagename
        logfile.write(closing)
        print closing
        end_time = termination_string()
        logfile.write(end_time)
        print end_time
        success = False
    except OSError as ose:
        logfile.write("OSError: ")
        print "OSError: "
        oserror_output = " errno: %s\n filename: %s\n strerror: %s\n" % (ose.errno, ose.filename, ose.strerror) 
        logfile.write(oserror_output)
        print oserror_output
        closing = "\nPackage %s failed to install.\n" % command
        logfile.write(closing)
        print closing
        end_time = termination_string()
        logfile.write(end_time)
        print end_time
        success = False
    return [success, logfile] 

def run(arch, logfile):
    """
    Installs and configures some Makahiki dependencies by issuing 
    system commands. Writes its output to a logfile while printing 
    it to the console.
    
    The target OS is Red Hat Enterprise Linux (RHEL). x64 RHEL is supported.
    """
    # Write first line to file
    firstline = "Makahiki installation script for Red Hat Enterprise Linux %s" % arch
    logfile.write(firstline)
    print firstline
    
    now = datetime.datetime.now()
    time = now.strftime("%Y-%m-%d %H:%M:%S")
    start_time = "Script started at %s\n" % time
    logfile.write(start_time)
    print start_time
    
    # Confirm that the user wants to continue.
    logfile.write("This script will add PostgreSQL's pgdg91 repository to the system.\n")
    print "This script will add PostgreSQL's pgdg91 repository to the system.\n"
    dependencies_list = "This script will install these packages and their dependencies:\n\
         git,\n\
         gcc,\n\
         python-setuptools (Python 2.6),\n\
         python-setuptools (Python 2.7),\n\
         pip (Python 2.6),\n\
         pip (Python 2.7),\n\
         python-imaging,\n\
         python-devel,\n\
         libjpeg-devel,\n\
         postgresql91-server,\n\
         postgresql91-contribs,\n\
         postgresql91-devel\n\
         memcached,\n\
         libmemcached-devel,\n\
         virtualenvwrapper (Python 2.6)\n"
    logfile.write(dependencies_list)
    print dependencies_list
    logfile.write("This script will also append to the current user's .bashrc file.\n")
    print ("This script will also append to the current user's .bashrc file.\n")
    value = raw_input("Do you wish to continue (Y/n)? ")
    while value != "Y" and value != "n":
        logfile.write("Invalid option %s\n" % value)
        print "Invalid option %s\n" % value
        value = raw_input("Do you wish to continue (Y/n)? ")
    if value == "n":
        logfile.write("Do you wish to continue (Y/n)? %s\n" % value)
        logfile.write("Operation cancelled.")
        print "Operation cancelled.\n"
        return logfile
    elif value =="Y":
        logfile.write("Do you wish to continue (Y/n)? %s\n" % value)
        logfile.write("Starting dependency installation for RHEL %s.\nChecking for dependencies...\n" % arch)
        print "Starting dependency installation for RHEL %s.\nChecking for dependencies...\n" % arch
    
    # Boolean variables for each dependency
    # The assumption is that none of the Python 2.7 tools have been 
    # installed before.
    git_installed = rpm_check("git")
    gcc_installed = rpm_check("gcc")
    python_setuptools26 = python_package_check("/usr/bin/easy_install", "distribute")
    python_setuptools27 = python_package_check("/usr/local/bin/easy_install-2.7", "setuptools")
    pip_installed26 = python_package_check("/usr/bin/pip", "pip")
    pip_installed27 = python_package_check("/usr/local/bin/pip-2.7", "pip")
    python_imaging_installed = rpm_check("python-imaging")
    python_devel_installed = rpm_check("python-devel")
    libjpeg_devel_installed = rpm_check("libjpeg-turbo-devel")
    postgresql91_repo = postgresql91_repocheck()
    postgresql91_server_installed = rpm_check("postgresql91-server")
    postgresql91_contrib_installed = rpm_check("postgresql91-contrib")
    postgresql91devel_installed = rpm_check("postgresql91-devel")
    memcached_installed = rpm_check("memcached")
    libmemcached_installed = rpm_check("libmemcached-devel")
    virtualenvwrapper26_installed = virtualenvwrapper_check("/usr/bin/virtualenv")
    
    # git
    if git_installed:
        logfile.write("git is already installed.\n")
        print "git is already installed.\n" 
    else:
        result = yum_install("git", logfile)
        success = result[0]
        logfile = result[1]
        if not success:
            return logfile
            
    # gcc
    if gcc_installed:
        logfile.write("gcc is already installed.\n")
        print "gcc is already installed.\n" 
    else:
        result = yum_install("gcc", logfile)
        success = result[0]
        logfile = result[1]
        if not success:
            return logfile
    
    # python-setuptools for the default Python 2.6.6
    if python_setuptools26:
        logfile.write("python-setuptools is already installed for Python 2.6.6\n")
        print "python-setuptools is already installed for Python 2.6.6\n" 
    else:
        logfile.write("python-setuptools will be installed for Python 2.6.6\n")
        print ("python-setuptools will be installed for Python 2.6.6\n")
        logfile.write("yum install -y python-setuptools\n")
        print "yum install -y python-setuptools\n"
        python_setuptools_output = subprocess.check_output(["yum", "install", "-y", "python-setuptools"], stderr=subprocess.STDOUT)
        logfile.write(python_setuptools_output)
        print python_setuptools_output
        python_setuptools26 = python_package_check("/usr/bin/easy_install", "distribute")
        if python_setuptools26:
            logfile.write("python-setuptools for Python 2.6.6 installed successfully.\n")
            print "python-setuptools for Python 2.6.6 installed successfully.\n"
            # Flush the buffer and force a write to disk after each successful installation
            logfile.flush()
            os.fsync(logfile)
        else:
            logfile.write("python-setuptools for Python 2.6.6 failed to install.\n")
            print "python-setuptools for Python 2.6.6 failed to install.\n"
            end_time = termination_string()
            logfile.write(end_time)
            print end_time
            return logfile 
    
    # python-setuptools, a.k.a. easy_install, for Python 2.7.3
    if python_setuptools27:
        logfile.write("python-setuptools is already installed for Python 2.7.3\n")
        print "python-setuptools is already installed for Python 2.7.3\n" 
    else:
        logfile.write("python-setuptools will be installed for Python 2.7.3\n")
        print ("python-setuptools will be installed for Python 2.7.3\n")
        logfile.write("python-setuptools (setuptools-0.8) will be downloaded.\n")
        print "python-setuptools (setuptools-0.8) will be downloaded.\n"
        
        # Switch to downloads directory
        download_dir = os.path.normpath(os.path.dirname(os.path.realpath(__file__)) + os.sep + os.pardir + os.sep + "download")
        logfile.write("Switching to downloads directory: %s" % download_dir)
        print "Switching to downloads directory: %s" % download_dir
        os.chdir(download_dir)
        logfile.write("Operation succeeded.\n")
        print "Operation succeeded.\n"
        
        # wget setuptools
        wget_command = "wget https://pypi.python.org/packages/source/s/setuptools/setuptools-0.8.tar.gz --no-check-certificate"
        logfile.write(wget_command + "\n")
        print wget_command + "\n"
        wget_output = subprocess.check_output(shlex.split(wget_command), stderr=subprocess.STDOUT)
        logfile.write(wget_output + "\n")
        print wget_output + "\n"
        
        # Extract setuptools
        logfile.write("Extracting setuptools.\n")
        print "Extracting setuptools.\n"
        tar_command = "tar xf setuptools-0.8.tar.gz"
        logfile.write(tar_command + "\n")
        print tar_command + "\n"
        tar_output = subprocess.check_output(shlex.split(tar_command), stderr=subprocess.STDOUT)
        logfile.write(tar_output + "\n")
        print tar_output + "\n"
        
        # Take ownership of extracted directory
        extracted_dir = os.getcwd() + os.sep + "setuptools-0.8"
        logfile.write("Changing ownership of %s to current user\n" % extracted_dir)
        print "Changing ownership of %s to current user\n" % extracted_dir
        uname = os.getuid()
        os.chown(extracted_dir, uname, -1)
        logfile.write("Operation succeeded.\n")
        print ("Operation succeeded.\n")
        
        # Change to extracted directory
        logfile.write("Switching to %s\n" % extracted_dir)
        print "Switching to %s\n" % extracted_dir
        os.chdir(extracted_dir)
        logfile.write("Working directory is now %s" % os.getcwd())
        print "Working directory is now %s" % os.getcwd()
        logfile.write("Operation succeeded\n.")
        print ("Operation succeeded\n.")
        
        # Install setuptools for Python 2.7
        setuptools27_command = "/usr/local/bin/python2.7 setup.py install"
        logfile.write(setuptools27_command + "\n")
        print setuptools27_command + "\n"
        setuptools27_output = subprocess.check_output(shlex.split(setuptools27_command), stderr=subprocess.STDOUT)
        logfile.write(setuptools27_output + "\n")
        print setuptools27_output + "\n"
        
        python_setuptools27 = python_package_check("/usr/local/bin/easy_install-2.7", "setuptools")
        if python_setuptools27:
            logfile.write("python-setuptools for Python 2.7.3 installed successfully.\n")
            print "python-setuptools for Python 2.7.3 installed successfully.\n"
            # Flush the buffer and force a write to disk after each successful installation
            logfile.flush()
            os.fsync(logfile)
        else:
            logfile.write("python-setuptools for Python 2.7.3 failed to install.\n")
            print "python-setuptools for Python 2.7.3 failed to install.\n"
            end_time = termination_string()
            logfile.write(end_time)
            print end_time
            return logfile 
        
    # pip for Python 2.6
    if pip_installed26:
        logfile.write("pip is already installed for Python 2.6.6.\n")
        print "pip is already installed for Python 2.6.6.\n" 
    else:
        logfile.write("pip will be installed for Python 2.6.6.\n")
        print ("pip will be installed for Python 2.6.6.\n")
        pip26_command = "/usr/bin/easy_install pip"
        logfile.write(pip26_command + "\n")
        print pip26_command + "\n"
        pip26_output = subprocess.check_output(shlex.split(pip26_command), stderr=subprocess.STDOUT)
        logfile.write(pip26_output +"\n")
        print pip26_output + "\n"
        pip_installed26 = python_package_check("/usr/bin/pip", "pip")
        if pip_installed26:
            logfile.write("pip for Python 2.6.6 installed successfully.\n")
            print "pip for Python 2.6.6 installed successfully.\n"
            # Flush the buffer and force a write to disk after each successful installation
            logfile.flush()
            os.fsync(logfile)
        else:
            logfile.write("pip for Python 2.6.6 failed to install.\n")
            print "pip for Python 2.6.6 failed to install.\n"
            end_time = termination_string()
            logfile.write(end_time)
            print end_time
            return logfile 
        
    # pip for Python 2.7   
    if pip_installed27:
        logfile.write("pip is already installed for Python 2.7.3.\n")
        print "pip is already installed for Python 2.7.3.\n" 
    else:
        logfile.write("pip will be installed for Python 2.7.3\n")
        print ("pip will be installed for Python 2.7.3\n")
        pip27_command = "/usr/local/bin/easy_install-2.7 pip" 
        logfile.write(pip27_command + "\n")
        print pip27_command + "\n"
        pip27_output = subprocess.check_output(shlex.split(pip27_command), stderr=subprocess.STDOUT)
        logfile.write(pip27_output + "\n")
        print pip27_output + "\n"
        pip_installed27 = python_package_check("/usr/local/bin/pip-2.7", "pip")
        if pip_installed27:
            logfile.write("pip for Python 2.7.3 installed successfully.\n")
            print "pip for Python 2.7.3 installed successfully.\n"
            # Flush the buffer and force a write to disk after each successful installation
            logfile.flush()
            os.fsync(logfile)
        else:
            logfile.write("pip for Python 2.7.3 failed to install.\n")
            print "pip for Python 2.7.3 failed to install.\n"
            end_time = termination_string()
            logfile.write(end_time)
            print end_time
            return logfile 

    logfile.write("Beginning installation of Python Imaging Library components python-imaging, python-devel, and libjpeg-devel.\n")
    print "Beginning installation of Python Imaging Library components python-imaging, python-devel, and libjpeg-devel.\n"
        
    # python-imaging    
    if python_imaging_installed:
        logfile.write("python-imaging is already installed.\n")
        print "python-imaging is already installed.\n" 
    else:
        result = yum_install("python-imaging", logfile)
        success = result[0]
        logfile = result[1]
        if not success:
            return logfile

    # postgresql91-server
    if python_devel_installed:
        logfile.write("python-devel is already installed.\n")
        print "python-devel is already installed.\n" 
    else:
        result = yum_install("python-devel", logfile)
        success = result[0]
        logfile = result[1]
        if not success:
            return logfile
        
    # libjpeg-devel
    if libjpeg_devel_installed:
        logfile.write("libjpeg-devel (libjpeg-turbo-devel) is already installed.\n")
        print "libjpeg-devel (libjpeg-turbo-devel) is already installed.\n" 
    else:
        result = yum_install("libjpeg-turbo-devel", logfile)
        success = result[0]
        logfile = result[1]
        if not success:
            return logfile

    # Check locations of shared libraries
    logfile.write("Checking for Python Imaging Library shared libraries.\n")
    print "Checking for Python Imaging Library shared libraries.\n"
    # libjpeg.so
    try:
        libjpeg_stat = os.stat("/usr/lib64/libjpeg.so")
        if libjpeg_stat:
            output1 = "Found libjpeg.so at /usr/lib64/libjpeg.so\n"
            logfile.write(output1)
            print output1
    except OSError as libjpeg_error:
        error1 = "Error: Could not find libjpeg.so in /usr/lib64 .\n"
        error2 = "Python Imaging Library-related packages may not have installed properly.\n"
        logfile.write(error1)
        logfile.write(error2)
        print error1
        print error2
        end_time = termination_string()
        logfile.write(end_time)
        print end_time
        return logfile
    # libz.so
    try:
        libjpeg_stat = os.stat("/usr/lib64/libz.so")
        if libjpeg_stat:
            output1 = "Found libz.so at /usr/lib64/libz.so\n"
            logfile.write(output1)
            print output1
    except OSError as libjpeg_error:
        error1 = "Error: Could not find libz.so in /usr/lib64 .\n"
        error2 = "Python Imaging Library-related packages may not have installed properly.\n"
        logfile.write(error1)
        logfile.write(error2)
        print error1
        print error2
        end_time = termination_string()
        logfile.write(end_time)
        print end_time
        return logfile 
    
    logfile.write("Installation of Python Imaging Library components is complete.\n")
    print "Installation of Python Imaging Library components is complete.\n"
    
    if postgresql91_repo:
        repo_string = "The repository at http://yum.postgresql.org/9.1/redhat/rhel-6-x86_64/pgdg-redhat91-9.1-5.noarch rpm is already installed.\n"
        logfile.write(repo_string)
        print repo_string
    else:
        # Install Postgresql RPM
        logfile.write("Adding the PostgreSQL 9.1 repo pgdg91...\n")
        print "Adding the PostgreSQL 9.1 repo pgdg91...\n"
        pg_repo_command = "rpm -i http://yum.postgresql.org/9.1/redhat/rhel-6-x86_64/pgdg-redhat91-9.1-5.noarch.rpm"
        logfile.write(pg_repo_command + "\n")
        print pg_repo_command + "\n"
        rpm_output = subprocess.check_output(shlex.split(pg_repo_command), stderr=subprocess.STDOUT)
        logfile.write(rpm_output + "\n")
        print rpm_output + "\n"
        rpm_installed = postgresql91_repocheck()
        if rpm_installed:
            logfile.write("pgdg91 repo installed successfully.\n")
            print "pgdg91 repo installed successfully.\n"
            # Flush the buffer and force a write to disk after each successful installation
            logfile.flush()
            os.fsync(logfile)
        else:
            logfile.write("PostgreSQL 9.1 repo failed to install.\n")
            print "PostgreSQL 9.1 repo failed to install.\n"
            end_time = termination_string()
            logfile.write(end_time)
            print end_time
            return logfile 
    
    # postgresql91-server
    if postgresql91_server_installed:
        logfile.write("postgresql91-server is already installed.\n")
        print "postgresql91-server is already installed.\n"
    else:
        result = yum_install("postgresql91-server", logfile)
        success = result[0]
        logfile = result[1]
        if not success:
            return logfile
    
    # postgresql-91-contrib
    if postgresql91_contrib_installed:
        logfile.write("postgresql91-contrib is already installed.\n")
        print "postgresql91-contrib is already installed.\n"   
    else:
        result = yum_install("postgresql91-contrib", logfile)
        success = result[0]
        logfile = result[1]
        if not success:
            return logfile
    
    # postgresql91-devel
    if postgresql91devel_installed:
        logfile.write("postgresql91-devel is already installed.\n")
        print "postgresql91-devel is already installed.\n"   
    else:
        result = yum_install("postgresql91-devel", logfile)
        success = result[0]
        logfile = result[1]
        if not success:
            return logfile
        
    # memcached
    if memcached_installed:
        logfile.write("memcached is already installed.\n")
        print "memcached is already installed.\n"   
    else:
        result = yum_install("memcached", logfile)
        success = result[0]
        logfile = result[1]
        if not success:
            return logfile
        
    # libmemcached-devel
    if libmemcached_installed:
        logfile.write("libmemcached-devel is already installed.\n")
        print "libmemcached-devel is already installed.\n"   
    else:
        result = yum_install("libmemcached-devel", logfile)
        success = result[0]
        logfile = result[1]
        if not success:
            return logfile 
        
    # virtualenvwrapper for Python 2.6
    if virtualenvwrapper26_installed:
        logfile.write("virtualenvwrapper is already installed for Python 2.6.6\n")
        print "virtualenvwrapper is already installed for Python 2.6.6.\n" 
    else:
        logfile.write("virtualenvwrapper will be installed for Python 2.6.6.\n")
        print ("virtualenvwrapper will be installed for Python 2.6.6.\n")
        virtualenv26_command = "/usr/bin/pip install virtualenvwrapper"
        logfile.write(virtualenv26_command + "\n")
        print virtualenv26_command + "\n"
        virtualenv26_output = subprocess.check_output(shlex.split(virtualenv26_command), stderr=subprocess.STDOUT)
        logfile.write(virtualenv26_output +"\n")
        print virtualenv26_output + "\n"
        virtualenv_installed26 = virtualenvwrapper_check("/usr/bin/virtualenv")
        if pip_installed26:
            logfile.write("virtualenvwrapper for Python 2.6.6 installed successfully.\n")
            print "virtualenvwrapper for Python 2.6.6 installed successfully.\n"
            # Flush the buffer and force a write to disk after each successful installation
            logfile.flush()
            os.fsync(logfile)
        else:
            logfile.write("virtualenvwrapper for Python 2.6.6 failed to install.\n")
            print "virtualenvwrapper for Python 2.6.6 failed to install.\n"
            end_time = termination_string()
            logfile.write(end_time)
            print end_time
            return logfile
    
    # bashrc
    USER_HOME = subprocess.check_output(["echo $HOME"], stderr=subprocess.STDOUT, shell=True) 
    # Remove newline from expected "/home/<username>\n"
    USER_HOME = USER_HOME[:-1]
    MAKAHIKI_HOME = USER_HOME + os.sep + "makahiki"
    message = "Appending these lines to user's ~./bashrc file:"
    bashrc_line1 = "# Virtualenvwrapper settings for makahiki"
    bashrc_line2 = "export WORKON_HOME=%s/.virtualenvs" % USER_HOME
    # Specify PROJECT_HOME as "/home/<username>/makahiki"
    bashrc_line3 = "export PROJECT_HOME=%s" % MAKAHIKI_HOME
    # Add location of pg_config to the PATH
    bashrc_line4 = "export PATH=/usr/pgsql-9.1/bin:$PATH"
    # Force all virtualenvs for this user to use Python 2.7.3
    bashrc_line5 = "export VIRTUALENVWRAPPER_PYTHON=/usr/local/bin/python2.7"
    # Set virtualenvwrapper location to the default Python 2.6.6's virtualenv
    bashrc_line6 = "export VIRTUALENVWRAPPER_VIRTUALENV=/usr/bin/virtualenv"
    # Restrict virtualenvs to the Python 2.7.3 site-packages directory
    bashrc_line7 = "export VIRTUALENVWRAPPER_VIRTUALENV_ARGS='--no-site-packages'"
    # Source the virtualenvwrapper.sh file (this line must come last)
    bashrc_line8 = "source /usr/bin/virtualenvwrapper.sh"
    
    print bashrc_line1
    print bashrc_line2
    print bashrc_line3
    print bashrc_line4
    print bashrc_line5
    print bashrc_line6
    print bashrc_line7
    print bashrc_line8
    
    # Append to ~/.bashrc
    bashrc = open(USER_HOME + os.sep + ".bashrc", 'a')
    bashrc.write(bashrc_line1 + "\n")
    bashrc.write(bashrc_line2 + "\n")
    bashrc.write(bashrc_line3 + "\n")
    bashrc.write(bashrc_line4 + "\n")
    bashrc.write(bashrc_line5 + "\n")
    bashrc.write(bashrc_line6 + "\n")
    bashrc.write(bashrc_line7 + "\n")
    bashrc.write(bashrc_line8 + "\n")
    bashrc.close()
    # Done appending to file
    logfile.write("Done appending to ~/.bashrc file.\n")
    print "Done appending to ~/.bashrc file.\n"
    
    logfile.write("RHEL x64 installation script completed successfully.\n")
    print "RHEL x64 installation script completed successfully.\n"
    end_time = termination_string()
    logfile.write(end_time)
    print end_time
    return logfile
