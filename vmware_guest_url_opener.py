#!/usr/bin/python
#-----------------------------------------------------------
# Filename      : vmware_guest_url_opener.py
# Description   : A URL handler to open web links in a VMWare Fusion guest
# Created By    : Rich Smith
# Date Created  : 14-Feb-2014 18:49
#
# License       : BSD
#
# (c) Copyright 2014, Syndis all rights reserved.
#-----------------------------------------------------------
__author__ = "Rich Smith"
__version__ = "0.1"

import os
import re
import sys
import struct
import subprocess
import ConfigParser

from objc import signature
from AppKit import NSApplication
from PyObjCTools import AppHelper
from Foundation import NSAppleEventManager, NSObject, NSLog
from LaunchServices import LSSetDefaultHandlerForURLScheme
from LaunchServices import LSSetDefaultRoleHandlerForContentType



def RegisterHandle():
    """
    Register ourselves as the default Web handler
    """
    NSLog("Registering vmware_guest_url as default web URL handler.....")
    LSSetDefaultRoleHandlerForContentType("public.html" , 0x00000002, "is.syndis.vmware_guest_url_opener")
    LSSetDefaultRoleHandlerForContentType("public.xhtml", 0x00000002, "is.syndis.vmware_guest_url_opener")
    LSSetDefaultHandlerForURLScheme("http" , "is.syndis.vmware_guest_url_opener")
    LSSetDefaultHandlerForURLScheme("https", "is.syndis.vmware_guest_url_opener")
    NSLog("Registration complete.")


class VmRunOpenBrowser(object):
    """
    Open a URL in a given VM & Browser
    """
    def __init__(self, config = '~/.vmware_guest_url_opener.cfg'):
        """

        """
        self.config = ConfigParser.ConfigParser({"bin" : "/Applications/VMware Fusion.app/Contents/Library/vmrun"})
        try:
            self.config.read(os.path.expanduser(config))
        except:
            NSLog("[-] Could not read config file %s"%(config))
            raise

        try:
            self.bin           = self.config.get("config", "bin")
            self.user          = self.config.get("config", "user")
            self.password      = self.config.get("config", "password")
            self.vm_guest_path = self.config.get("config", "vmx_path")
        except:
            NSLog("[-] Could not read a required value from the configuration file")
            raise

        self.action        = "runScriptInGuest"
        self.intr_path     = "/usr/bin/python"


    def __call__(self, url):
        """
        Make the call to vmrun to kick off the web browser
        """
        ##Exec a python script in the guest
        self.py_script = "import webbrowser; webbrowser.open('%s')"%(url)

        ##Exec the vmrun command
        subprocess.check_output([self.bin, "-gu", self.user, "-gp", self.password, self.action, self.vm_guest_path, self.intr_path, self.py_script])


class AppDelegate(NSObject):

    def dirty_init(self, config = '~/.vmware_guest_url_opener.cfg'):
        """
        Read in config
        """
        self.config = ConfigParser.ConfigParser({"host_browser": "safari", "host_urls": ""})
        try:
            self.config.read(os.path.expanduser(config))
        except:
            NSLog("[-] Could not read config file %s"%(config))
            raise

        ##If the passed URL is in this list open it in the host not guest - regex's
        self.exception_list = self.config.get("config", "host_urls").split(";")
        self.host_browser   = self.config.get("config", "host_browser")

        self.browser_map    = {"chrome"  : "com.google.Chrome",
                               "firefox" : "org.mozilla.firefox",
                               "safari"  : "com.apple.safari"}
        self.host_browser   = self.browser_map[self.host_browser]


        self.vmr = VmRunOpenBrowser()


    def applicationWillFinishLaunching_(self, notification):

        ##Set up a Get URL (GURL) event handler
        man = NSAppleEventManager.sharedAppleEventManager()
        man.setEventHandler_andSelector_forEventClass_andEventID_(
            self,
            "openURL:withReplyEvent:",
            struct.unpack(">i", "GURL")[0],
            struct.unpack(">i", "GURL")[0])
        man.setEventHandler_andSelector_forEventClass_andEventID_(
            self,
            "openURL:withReplyEvent:",
            struct.unpack(">i", "WWW!")[0],
            struct.unpack(">i", "OURL")[0])


    @signature('v@:@@')
    def openURL_withReplyEvent_(self, event, replyEvent):

        keyDirectObject = struct.unpack(">i", "----")[0]
        url = (event.paramDescriptorForKeyword_(keyDirectObject)
               .stringValue().decode('utf8'))

        show_in_host = False
        for exception in self.exception_list :
            url_re = re.compile(exception)
            ret = url_re.search(url)
            if ret:
                show_in_host = True
                break

        if show_in_host:
            #NSLog("EXCEPTION MATCHED, opening in host: %s"%(url))
            ##Hardcode to open in a host broswer bypassing the default handler
            ret = subprocess.check_output(["open", "-b", self.host_browser, url])

        else:
            #NSLog("Opening in guest: %s"%(url))
            self.vmr(url)

        ##Kill ourselves so the proc doesn't continue to run for *
        AppHelper.stopEventLoop()


def main():
    ##Kick off an app with the event handlers to deal with the GURL Apple events
    app = NSApplication.sharedApplication()
    delegate = AppDelegate.alloc().init()
    delegate.dirty_init()
    app.setDelegate_(delegate)
    AppHelper.runEventLoop()


if __name__ == '__main__':

    try:
        if len(sys.argv) >1 and sys.argv[1] == "register":
            ##We need to set the default URL to bootstrap ourselves
            regHandler = RegisterHandle()
            regHandler()
        else:
            main()

    except Exception, err:
        NSLog("ERROR: %s"%(err))
        import traceback
        tb = traceback.format_exc()
        NSLog("TRACEBACK: %s"%tb)
        AppHelper.stopEventLoop()
        raise