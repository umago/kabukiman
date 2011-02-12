Kabukiman
=========

Kabukiman is a simple dictionary application which allows you to create
your own modules and extend its functionality quite easily.

Modules that come by default:
    * Google Translate
    * Babylon (alpha)

Requirements
------------

    * python2.6
    * python-gtk
    * python-xlib

Install 
-------
    
### Using distutils

    # python setup.py install

### Creating deb package

    $ python setup.py install --deb
    # dpkg -i dist/kabukiman_<version>-<arch>.deb

Usage
-----

Select a text in any window and press CTRL + SHIFT + X  or press F8, type
the text and hit enter, kabukiman will search that text into actives modules.

All shortcuts can be configured in the preferences dialog (CTRL + P).

[More information][2]

Creating a module
-----------------

Please check this [page][2].

License
-------

Kabukiman is distributed under the terms of the GNU General Public License, version 2.
See the [COPYING][4] file for more information.

Contributor list
----------------

Lucas Alvares Gomes (aka umago) <lucasagomes@gmail.com>

Contributing
------------

1. Fork it
2. Create a branch (`git checkout -b <branch name>`)
3. Commit your changes (`git commit -am "Added ..."`)
4. Push to the branch (`git push origin <branch name>`)
5. Create an [Issue][1] with a link to your branch

Please take a look at [TODO][3] file to see bugs and not-implemented-yet 
features.

[1]: http://github.com/umago/kabukiman/issues
[2]: http://umago.info/kabukiman
[3]: https://github.com/umago/kabukiman/blob/master/TODO
[4]: https://github.com/umago/kabukiman/blob/master/COPYING

