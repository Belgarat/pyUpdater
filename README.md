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
> **Description**: Update the code (directory is seated in configuration file). 
An backup of the directory is make before update.
The procedure preserve the "whitelist" files setted in the configuration file 
(comma separator for multiple file)
* -b, --backup        backup code
> **Description**:
* -r, --restore       restore code from backup
> **Description**:
* -d, --dump          dump database
> **Description**: permit to dump an specified database set on the configuration file. 
After dump the file is automatic put on an remote server. 
The file is an tar.gz, part of the name is the number of day of week.
* -s, --restore-dump  restore database from dump
> **Description**:
* -c, --config        specified another config file
> **Description**: permit to specified another configuration file.
Absolute path is necessary. The file it must be an valid json format.  

# TODO

1. Change dump function to make optional remote backup