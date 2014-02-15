#-----------------------------------------------------------
# Filename      : install..py.py
# Description   : VMWareGuestURLOpener quick installation script
# Created By    : Rich Smith
# Date Created  : 15-Feb-2014 08:36
# Date Modified : 
# 
# License       : BSD
#
# (c) Copyright 2014, Syndis all rights reserved.
#-----------------------------------------------------------
__author__ = "Rich Smith"
__version__ = "0.1"

import os
import sys
import getpass
import ConfigParser
import distutils.core
from vmware_guest_url_opener import RegisterHandle

class Install(object):
    """
    Quicky installer to make setup easier
    """
    def __init__(self):
        """
        """
        self.config      = ConfigParser.RawConfigParser()
        self.config_dest = os.path.expanduser("~/.vmware_guest_url_opener.cfg")

        self.browser_choices = ["chrome", "firefox", "safari"]
        self.fusion_app      = "/Applications/VMware Fusion.app"
        self.vmrun_bin       = "Contents/Library/vmrun"


    def __call__(self):
        """
        Do installation / setup actions
        """
        print "\n** VMWare Guest URL Opener installation and setup **\n"

        #Check we are on OSX
        if sys.platform != 'darwin':
            print "[!] Sorry VMWareGuestURLOpener only runs on OS X with VMWare Fusion at the moment :-( "
            return False

        #Run the setup
        raw_input("Press enter to build the VMWareGuestURLOpener application package for your system (Lots of text will scroll by!) .....")
        dist = distutils.core.run_setup('setup.py', ['-q', 'py2app'], stop_after = "run")

        #Get config values
        raw_input("\n\nDone. Now we are going to get some information from you to setup your VMWareGuestURLOpener environment. hit Enter to continue  ")
        self.get_and_set_config()

        #Copy config to ~
        with open(self.config_dest, 'wb') as configfile:
            self.config.write(configfile)
        #chmod it to provide the pw a modicum of protection
        os.chmod(self.config_dest, 0600)

        #Register handler
        print "\nRegistering VMWareGuestURLOpener as the default URL handler...",
        RegisterHandle()
        print "done."

        print "\n\nInstallation Complete"
        print "\n** The VMWareGuestURLOpener .app can be found in the 'dist' subdirectory, please move this to wherever you would like it to be permanently **\n"


        return True


    def _get_user_input(self, msg, default = None, required = False, non_echo = False, choices = []):
        """
        Query user for input and check value supplied
        """
        if non_echo:
            ret = getpass.getpass(msg)
        else:
            ret = raw_input(msg)

        if not ret and default:
            ret = default

        elif not ret and required:
            print "[!] Please enter a non-empty value"
            return self._get_user_input(msg, default, required, non_echo, choices)

        elif choices and ret not in choices:
            print "[!] Please enter a choice from one of the following: %s"%(choices)
            return self._get_user_input(msg, default, required, non_echo, choices)

        return ret


    def get_and_set_config(self):
        """
        Query user for variables and create config file
        """
        ##Get values from the user
        vmx_path = self._get_user_input("\nWhat is the path to the .vmx file of the guest VM you want links to open in? ", required = True)
        vm_user  = self._get_user_input("What is the username of the guest VM? ", required = True)
        vm_pass  = self._get_user_input("What is the password of the guest VM user? ", non_echo = True)

        host_urls    = self._get_user_input("You can specify links to open in the host rather than the guest VM.\n\
These should be specified as a list of regular expressions to match against destination URLs seperated by ';'.\n\
(e.g. '[*.]google.com;[*.]github.com' (without quotes). Leave blank if you want all URL's to be opened in the guest: ")
        host_browser = self._get_user_input("What browser would you like to open any host links in? %s "%(self.browser_choices), required = True, choices = self.browser_choices)

        fusion_bin   = self._get_user_input("Where is your VMWare Fusion application installed? [%s] "%(self.fusion_app), default = self.fusion_app )


        ##Build config
        self.config.add_section("config")
        self.config.set("config", "user", vm_user)
        self.config.set("config", "password", vm_pass)
        self.config.set("config", "vmx_path", os.path.expanduser(vmx_path))
        self.config.set("config", "host_urls", host_urls)
        self.config.set("config", "host_browser", host_browser)
        self.config.set("config", "bin", os.path.join(os.path.expanduser(fusion_bin), self.vmrun_bin))


if __name__ == "__main__":
    """
    Call installation
    """
    I = Install()
    ret = I()