# Installation

1. Install library mysql connector

	sudo apt-get install python3-mysql.connector python3-pip python3-paramiko
	python3.5 -m pip install cffi

2. Create pyUpdater directory in /opt

3. Decompress tar.gz in /opt/pyUpdater directory

4. Create link in /usr/local/bin/ directory:

	ln -s /opt/pyUpdater/pyUpdater.py pyUpdater

6. Copy or rename example config file to:
   
    mv conf/pyUpdater.json.example conf/pyUpdater.json
   
   and customize configuration file

5. Launch test command:

	pyUpdater -t

# Info

-h, --help          print this help message
-u, --update        update code
-b, --backup        backup code
-r, --restore       restore code from backup
-d, --dump          dump database
-s, --restore-dump  restore database from dump

# TODO

1. Add option for specifying configuration file position
2. Change dump function to make optional remote backup