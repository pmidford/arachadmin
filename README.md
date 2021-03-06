## Arachadmin

This is a web2py tool for managing information going into arachnolingua via a MySQL database.  OwlBuilder (https://github.com/pmidford/owlbuilder) is
accompanying tool to generate owl/rdf from the database.

## Copyright and License

All original code (not part of web2py) is copyright 2013-2015 Peter E. Midford

> This program is available under the terms of the 'MIT' license, a copy of which is included in this repository.

## Installation

1. Install prerequisites.  On MacOS, I recommend using homebrew (http://brew.sh/), and consider installing the latest python 2.7.x (web2py doesn't support python3 at this time).  Also install pip from http://www.pip-installer.org/en/latest/.

   Currently the only prerequisite for arachadmin is lxml.  On ubuntu, you might be able to just use 'apt-get install -y python-pip'; otherwise use: TBD

2. Install MySQL.

3. Configure MySQL.

4. Download and install web2py.  The current version of arachadmin runs with version 2.5.1.

5. Get the current backend dump from figshare.

6. Load the dump.  'catting' into a mysql client (e.g. cat arachadmin.sql | mysql -u <user> --password arachadmin) seems to work, but your mileage may vary.

7. Configure arachadmin



## Contact:
   Peter E. Midford
   peter.midford@gmail.com
