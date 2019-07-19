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

* -h, --help          print this help message
> **Description**:
* -u, --update        update code
> **Description**: Update the code (directory is stored in configuration file). 
A backup of the directory is made before update.
The procedure preserves the "whitelist" files set in the configuration file 
(comma separator for multiple file)
* -b, --backup        backup code
> **Description**:
* -r, --restore       restore code from backup
> **Description**:
* -d, --dump          dump database
> **Description**: permit to dump a specified database set on the configuration file. 
After dump the file is automatically put on an remote server. 
The file is a tar.gz, part of the name is the number of the day of the week.
* -s, --restore-dump  restore database from last local dump
> **Description**:
* -c, --config        specify another config file
> **Description**: permit to specify another configuration file.
Absolute path is necessary. The file must be in a valid json format.  

# TODO

1. Change dump function to make optional remote backup
