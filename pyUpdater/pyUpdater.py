#!/usr/bin/python3.7
# -*- coding: utf-8 -*-
#
#  pyUpdater.py
#  
#  Copyright 2019 marco brunet <viacart@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#
import os
import shutil
import tempfile as td
import json
import logging
import requests
import sys, getopt
import mysql.connector
from mysql.connector import Error
import subprocess
import time
import glob
from transfer import Transfer as Tr

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
class uPath:
    HOME = os.path.join(os.path.expanduser('~'), '/.config')
    SYSCONF = os.path.join('/etc/pyUpdater')
    CUSTOMCONF = os.path.join('/opt/pyUpdater/conf')
    LOCALCONF = os.path.join('./conf')

class pyUpdater:
    def __init__(self, verbose=False):
        self.classname = "pyUpdater"
        self.version = "0.1"
        self.configdir = "/opt/pyUpdater"
        self.configfile = "conf/pyUpdater.json"
        self.configCustomFile = ""
        self.verbose = verbose
        self.loadConfig()
        logging.basicConfig(filename=self.config['logfile'], level=self.config['loglevel'], format=self.config['logformat'])
        self.preservefile = self.config['whitelist'].split(';')
        self.createTmpDir()

        # INIT transfer module
        self.tr = Tr()
        self.init_transfer()

    def loadConfig(self):
        print(self.configCustomFile)
        if(self.configCustomFile == ""):
            with open(self.configdir + '/' + self.configfile, 'r') as f:
                self.config = json.load(f)
        else:
            with open(self.configCustomFile, 'r') as f:
                self.config = json.load(f)

    def setConfigFile(self, path):
        self.configCustomFile = path
        self.loadConfig()

    def init_transfer(self):
        self.tr.server = self.config['transfer']['server']
        self.tr.username = self.config['transfer']['username']
        self.tr.password = self.config['transfer']['password']
    
    def createTmpDir(self):
        self.tmpdir = td.mkdtemp()
        self.log("Create temporary directory: " + self.tmpdir)
    
    def extractUpdate(self):
        self.log("Extract update!")
        archive_name = os.path.join(self.tmpdir, self.config['updatefile'])
        shutil.unpack_archive(archive_name,self.config['dstdir'])
        
    def backup(self):
        archive_name = os.path.join(self.config['backupdir'], 'backup')
        shutil.make_archive(archive_name, 'gztar', self.config['dstdir'])
        self.log("Create backup file: " + archive_name + ".tar.gz")
    
    def restore(self):
        archive_name = os.path.join(self.config['backupdir'], 'backup') + '.tar.gz'
        shutil.unpack_archive(archive_name,self.config['dstdir'])
        self.log("Restored file in " + archive_name + ".tar.gz to " + self.config['dstdir'])
    
    def update(self):
        if self.checkupdate():
            self.log("New update present. Start updating ...")
            self.backup_whitelist()
            self.remove_old_file()
            self.extractUpdate()
            self.restore_whitelist()
        else:
            self.log("New version not found!")
            quit(0)

    def dump(self):
        self.log("Dump database")
        self.dump_database()
        self.tr.send(self.config['backupdir'] + self.dumpname, "/tmp" + self.dumpname)

    def restoredump(self):
        self.log("Restore database from dump")
        self.restore_database()
        # todo: remote copy
            
    def checkupdate(self):
        self.log("Start update procedure.")
        url = self.config['updateserver'] + "/" + self.config['updatefile']
        r = requests.get(url)
        if r.status_code != 200:
            self.log("Update not present. Error code: " + r.status_code.__str__())
            return False
        else:
            with open(os.path.join(self.tmpdir, self.config['updatefile']), 'wb') as f:  
                f.write(r.content)
        return True
    
    def backup_whitelist(self):
        for f in self.preservefile:
            self.log("Save file: " + os.path.join(self.config['dstdir'], f))
            shutil.copy2(os.path.join(self.config['dstdir'], f), self.tmpdir + '/')

    def restore_whitelist(self):
        for f in self.preservefile:
            self.log("Restore file: " + os.path.join(self.config['dstdir'], f))        
            filename = os.path.basename(self.tmpdir + '/' + f)
            shutil.copy2(self.tmpdir + '/' + filename, os.path.join(self.config['dstdir'], f))
    
    def remove_old_file(self):
        for r, d, f in os.walk(self.config['dstdir']):
            for file in f:
                os.remove(os.path.join(r, file))
    
    def dump_database(self):
        try:
            timestamp = str(int(time.time()))
            self.dumpname = "/dump_" + self.config['db_name'] + "_" + timestamp + ".sql.gz"
            p = subprocess.Popen("mysqldump -h " + self.config['db_host'] + " -u " + self.config['db_user'] + " -p" + self.config['db_pass'] + " " + self.config['db_name'] + " | gzip > " + self.config['backupdir'] + self.dumpname, shell=True)
            # Wait for completion
            p.communicate()
            # Check for errors
            if(p.returncode != 0):
                raise "Backup return code: " + p.returncode
            self.log("Backup done for " + self.config['db_name'] )
        except:
            self.log("Backup failed for " + self.config['db_name'] )
    
    def restore_database(self):
        try:
            # trovare ultimo dump sotto la directory dei backup
            list_of_files = glob.glob(self.config['backupdir'] + '/*.sql.gz')
            latest_file = max(list_of_files, key=os.path.getctime)
            if latest_file != '':
                p = subprocess.Popen("zcat  " + latest_file + " | mysql -h " + self.config['db_host'] + " -u " + self.config['db_user'] + " -p" + self.config['db_pass'] + " " + self.config['db_name'], shell=True)
                # Wait for completion
                p.communicate()
                # Check for errors
                if p.returncode != 0:
                    raise "Restore return code: " + p.returncode
                self.log("Restore done for " + latest_file )
            # no dump found
            else:
                self.log("No dumps found in " + self.config['backupdir'] + ". Cannot restore anything, sorry.")
        except:
            self.log("Restore failed for " + latest_file)

    def log(self, msg, level='debug'):
        if self.verbose:
            print(msg)
        logging.debug(msg)
        
    def test(self):
        # check if destination directory exist and is writeable
        print("")
        print("-------------------# CHECK FILESYSTEM #-------------------")
        if os.path.exists(self.config['dstdir']):
            print(bcolors.OKBLUE + '[ok]' + bcolors.ENDC, self.config['dstdir'] + ' exist.')
            if os.access(self.config['dstdir'], os.W_OK):
                print(bcolors.OKBLUE + '[ok]' + bcolors.ENDC, self.config['dstdir'] + ' is writeable.')
            else:
                print(bcolors.FAIL + '[fail]' + bcolors.ENDC, self.config['dstdir'] + ' is not writeable.')
        else:
            print(bcolors.FAIL + '[fail]' + bcolors.ENDC, self.config['dstdir'] + ' not exist. Create this folder.')
        
        # check if backup directory exist and is writeable
        if os.path.exists(self.config['backupdir']):
            print(bcolors.OKBLUE + '[ok]' + bcolors.ENDC, self.config['backupdir'] + ' exist.')
            if os.access(self.config['backupdir'], os.W_OK):
                print(bcolors.OKBLUE + '[ok]' + bcolors.ENDC, self.config['backupdir'] + ' is writeable.')
            else:
                print(bcolors.FAIL + '[fail]' + bcolors.ENDC, self.config['backupdir'] + ' is not writeable.')
        else:
            print(bcolors.FAIL + '[fail]' + bcolors.ENDC, self.config['backupdir'] + ' not exist. Create this folder.')

        # check if config file exists and readable
        if os.path.exists(self.configdir + '/' + self.configfile):
            print(bcolors.OKBLUE + '[ok]' + bcolors.ENDC, self.configdir + '/' + self.configfile + ' exist.')
            if os.access(self.configdir + '/' + self.configfile, os.R_OK):
                print(bcolors.OKBLUE + '[ok]' + bcolors.ENDC, self.configdir + '/' + self.configfile + ' is readable.')
            else:
                print(bcolors.FAIL + '[fail]' + bcolors.ENDC, self.configdir + '/' + self.configfile +
                      ' is not readable.')
        else:
            print(bcolors.FAIL + '[fail]' + bcolors.ENDC, self.configdir + '/' + self.configfile +
                  ' not exist. Create this folder.')

        print("----------------------# END #-----------------------------")
        print("")
        print("")
        print("---------------------# DB CHECK #-------------------------")
        # check database connection
        try:
            connection = mysql.connector.connect(host=self.config['db_host'],
                                                 database=self.config['db_name'],
                                                 user=self.config['db_user'],
                                                 password=self.config['db_pass'])
            if connection.is_connected():
                db_info = connection.get_server_info()
                print(bcolors.OKBLUE + '[ok]' + bcolors.ENDC +
                      " connected to MySQL database... MySQL Server version on ",db_info)
                cursor = connection.cursor()
                cursor.execute("select database();")
                record = cursor.fetchone()
                print("Your connected to - ", record)
        except Error as e:
            print(bcolors.FAIL + '[fail]' + bcolors.ENDC + " error while connecting to MySQL")
            pass
        
        print("----------------------# END #-----------------------------")
        print("")
        print("")
        print("---------------------# SSH CHECK #-------------------------")
        if self.tr.checkconnection():
            print(bcolors.OKBLUE + '[ok]' + bcolors.ENDC, 'server: ' + self.tr.server + ' and user: '
                  + self.tr.username + ' - connection succesfuly.')
        else:
            print(bcolors.FAIL + '[fail]' + bcolors.ENDC, 'server: ' + self.tr.server + ' and user: '
                  + self.tr.username + ' - connection failed.')
        print("----------------------# END #-----------------------------")
        print("")

    def __del__(self):
        shutil.rmtree(self.tmpdir)


def main(argv):
    unixoptions = "c:htubrvds"
    gnuoptions = ["help", "verbose", "update", "backup", "restore", "dump", "restore-dump", "test", "config"]
    verbose = False
    configFile = ""
    if '-v' in argv:
        verbose = True
    if '--verbose' in argv:
        verbose = True

    upd = pyUpdater(verbose)
    action = ""

    try:
        opts, args = getopt.getopt(argv, unixoptions, gnuoptions)
    except getopt.GetoptError:
        print('-h, --help          print this help message')
        print('-u, --update        update code')
        print('-b, --backup        backup code')
        print('-r, --restore       restore code from backup')
        print('-d, --dump          dump database')
        print('-s, --restore-dump  restore database from dump')
        print('-c, --config        specified another config file')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h' or opt == "--help":
            print('-h, --help          print this help message')
            print('-u, --update        update code')
            print('-b, --backup        backup code')
            print('-r, --restore       restore code from backup')
            print('-d, --dump          dump database')
            print('-s, --restore-dump  restore database from dump')
            print('-c, --config        specified another config file')
            sys.exit()
        elif opt in ("-c", "--config"):
            if os.access(os.path.join(arg), os.R_OK):
                upd.setConfigFile(arg)
            else:
                print(bcolors.FAIL + '[fail]' + bcolors.ENDC, os.path.join(arg) +
                      ' is not readable or not exist.')
                sys.exit(2)
        elif opt in ("-u", "--update"):
            action = "update"
        elif opt in ("-b", "--backup"):
            action = "backup"
        elif opt in ("-r", "--restore"):
            action = "restore"
        elif opt in ("-d", "--dump"):
            action = "dump"
        elif opt in ("-s", "--restore-dump"):
            action = "restoredump"
        elif opt in ("-t", "--test"):
            action = "test"

    getattr(upd, action)()


if __name__ == "__main__":
    main(sys.argv[1:])
