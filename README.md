#VMWare Guest URL Opener

This is URL handler that is able to delegate and open URL's in a VMWare Fusion guest OS on OS X. It should work against
most guest OS's and open the link in whatever is set as the default browser for the guest.

There is also an option to provide a list of regular expressions to open in the host OS rather than the guest.


##Installation and setup

The initial setup is quite straight forward, in the `vmware_guest_url_opener` directory run the following to build the app:

```
python setup.py py2app
```

This will build an OS X application bundle and dump it in the `dist` subdirectory. Place the resulting binary wherever you would like.


Next you need to setup the configuration file, it is quite straight forward and needs the following variables:

* `vmx_path` - This is the path to the `.vmx` file of the VM guest in which you want links to open
* `user` - This is the username of a user running in the guest VM in which links will open
* `password` - This is the password of the user, not too desirable but VMWare gives us little choice in this
* `bin` - This is the path to the `vmrun` binary, if you have VMWare installed in `/Applications` you can leave it at the default value in the example config

The next two variables determine the behaviour of the URL handler:

* `host_urls` - A list of regular expressions separated by `;` against which URL's will be tested, if the URL's match then the URL will not be opened in the guest but in the host
* `host_browser` - The is the browser that any URL matching the `host_url` list will be opened in on the host. Supported values are: `chrome`, `safari` and `firefox`

Once you have setup the config file you need to copy it to `~/.vmware_guest_url.cfg` - **remember to set appropriate permissions on it as it has a password in it**


The final step is to set this application as the default URL handler for applications so that it intercepts future URLs,
to do this just do:

```
python vmware_guest_url_opener.py register
```

##Todo
Create a nice installation script
Create an uninstallation script

##References

