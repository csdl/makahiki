# Copy the two import statements into the file that will use the PyDev remote debugger.
# This assumes you copied the org.python.pydev_* directory into makahiki/makahiki.
# Edit the path so that it matches the path to your org.python.pydev_* directory.
# EXAMPLE: import sys;sys.path.append(os.pardir + os.sep + r'<path-to-org.python.pydev>\org.python.pydev_2.7.5.2013052819\pysrc')
import os
import sys;sys.path.append(os.pardir + os.sep + r'org.python.pydev_2.7.5.2013052819\pysrc')
import pydevd

# An example of how to use pydevd.settrace() with the remote debugging server.
# Based on the example code from http://pydev.org/manual_adv_remote_debugger.html.
class TestDebugServer:
    """
    This is a test that runs pydevd.settrace(). Each occurrence of 
    pydevd.settrace() acts as a breakpoint if the remote debugging server is 
    running in Eclipse.
    Parameter 1: IP address of the machine where Eclipse and the remote 
        debugging server are running. In a VirtualBox host-only network, the 
        host machine has the first available address. If your virtual machine 
        has an IP address in the 192.168.56.0/24 block, the host machine will 
        have IP address 192.168.56.1.
    port: Port number. The default is 5678. This can be changed in Eclipse.
    stdoutToServer: Send stdout to the remote debugging server.
    stderrToServer: Send stderr to the remote debugging server.
    """
    def test(self):
        i = 10
        while i > 0:
            print 'setting trace'
            # When pydevd.settrace() executes, the debug server will display the execution state.
            pydevd.settrace('192.168.56.1', port=5678, stdoutToServer=True, stderrToServer=True)
            i = i - 1

def main():
    print "Running TestDebugServer.test() now."
    print "Make sure the debug server is running in Eclipse."
    TestA = TestDebugServer()
    TestA.test()
    print "Done."

if __name__ == '__main__':
    main()