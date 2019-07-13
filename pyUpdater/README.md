# Installation

1. Install library mysql connector

	sudo apt-get install python3-mysql.connector python3-pip python3-paramiko
	python3.5 -m pip install cffi

2. Create pyUpdater directory in /opt

3. Decompress tar.gz in /opt/pyUpdater directory

4. Create link in /usr/local/bin/ directory:

	ln -s /opt/pyUpdater/pyUpdater.py pyUpdater

5. Launch test command:

	pyUpdater -t

