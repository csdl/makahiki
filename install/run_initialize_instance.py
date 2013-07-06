import subprocess

def termination_string():
    """
    Gets the current system time and appends it to a termination notice.
    """
    end_time = "Script exiting at %s" % subprocess.check_output(["date"], stderr=subprocess.STDOUT)
    return end_time

def run(logfile):
    """
    Runs the makahiki/makahiki/scripts/initialize_instance.py --type default 
    script and logs the output to a file.
    """
    try:
        USER_HOME = subprocess.check_output(["echo $HOME"], stderr=subprocess.STDOUT, shell=True) 
        # Remove newline from expected "/home/<username>\n"
        USER_HOME = USER_HOME[:-1]
        USER_PROJECT_HOME = USER_HOME + "/makahiki"
        # cd to makahiki directory so pip can find the requirements.txt file
        os.chdir(USER_PROJECT_HOME)
        update_output = subprocess.check_output(["./makahiki/scripts/initialize_instance.py --type default"], stderr=subprocess.STDOUT, shell=True)
        logfile.write(update_output)
        print(update_output)
        # Clear the buffer.
        logfile.flush()
        os.fsync(logfile)
    except subprocess.CalledProcessError as cpe:
        logfile.write("CalledProcessError: ")
        print "CalledProcessError: "
        logfile.write(cpe.output)
        print cpe.output
        logfile.write("Warning: initialize_instance did not complete successfully.")
        print "Warning: initialize_instance did not complete successfully."
        end_time = termination_string()
        logfile.write(end_time)
        print end_time
        return logfile 