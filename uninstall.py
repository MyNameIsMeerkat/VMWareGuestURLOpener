#-----------------------------------------------------------
# Filename      : uninstall.py.py
# Description   : Uninstall VMWareGuestURLOpener as the default handler
# Created By    : Rich Smith
# Date Created  : 15-Feb-2014 12:46
# Date Modified : 
# 
# License       : BSD
#
# (c) Copyright 2014, Syndis all rights reserved.
#-----------------------------------------------------------
__author__ = "Rich Smith"
__version__ = "0.1"

import os
import ConfigParser
from vmware_guest_url_opener import RegisterHandler

class Uninstall(object):
    """
    Remove VMWareGuestURLOpener
    """
    def __init__(self, config_file = "~/.vmware_guest_url_opener.cfg"):
        """
        """
        self.config      = ConfigParser.ConfigParser()
        self.config_src = os.path.expanduser(config_file)

    def __call__(self):
        """
        Pretty simple, read the config and restore the handlers as they were before VMWareGuestURLOpener was installed
        """
        raw_input("\n\n ** About to uninstall VMWareGuestURLOpener as the default, hit enter to continue ....")

        if not self.config.read(self.config_src):
            print "[-] Problem reading configuration file %s"%(self.config_src)
            return False


        try:
            orig_http_handler  = self.config.get("config", "http_handler")
            orig_https_handler = self.config.get("config", "https_handler")
        except ConfigParser.NoOptionError, err:
            print err
            print "Uninstallation cannot continue, please reset your default handler manually."
            return False

        ##Reset them as default handlers
        RegisterHandler(orig_http_handler, orig_https_handler)

        print "\nReset handlers to:\n\tHTTP: %s\n\tHTTPS: %s\n"%(orig_http_handler, orig_https_handler)

        ##Delete the config
        ret = raw_input("Do you want to delete the config file (%s)? (yes/NO) "%(self.config_src))
        if ret.lower() not in ["y", "yes"]:
            print "[!] Skipping removal of config file"
        else:
            try:
                os.unlink(self.config_src)
                print "[+] Config file deleted"
            except Exception, err:
                print "[-] Error removing config file '%s' - '%s'"%(self.config_src, err)

        print "\n**To complete the uninstallation you must MANUALLY delete the VMWareGuestURLOpener application package from wherever you copied it to after installation**\n]n"

        return True


if __name__ == "__main__":
    """
    Call main code
    """
    U =Uninstall()
    U()