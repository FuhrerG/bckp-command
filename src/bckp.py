#!/usr/bin/python3
from subprocess import call
from getpass import getuser
from pwd import getpwuid
from grp import getgrgid
from sys import exit
from configparser import ConfigParser
from argparse import ArgumentParser
import uuid
import os
import time

###############################################################################
#                                    UTILS                                    #
###############################################################################

def exist_file(file):
    return call('[ ! -f ' + file + ' ]', shell = True)

def exist_dir(file):
    return call('[ ! -d ' + file + ' ]', shell = True)

def exist(file):
    return exist_dir(file) or exist_file(file)

def alias_of_path(file):
    conf.read(confFile)
    for opcion, valor in conf['PATHS'].items():
        if opcion == file:
            return valor
    return False

def path_of_alias(alias):
    conf.read(confFile)
    for opcion, valor in conf['PATHS'].items():
        if valor == alias:
            return opcion
    return False

def getLastVersion(file):
    bckpConf = ConfigParser()
    bckpConf.read(file)
    max = -1
    for section in bckpConf.sections():
        if section != 'DEFAULT':
            max = int(section) if int(section) > max else max
    return max

###############################################################################
#                                 LIST BACKUP                                 #
###############################################################################

def list_backup(args):
    print(args)
    print('list_info' + str(args.list_info))

###############################################################################
#                                 ADD  BACKUP                                 #
###############################################################################
    
def add_backup(args):
    for n in range(len(args.file)):
        file = args.file[n]

        if exist(file):
            file = file[:-1] if file[-1] == '/' else file
            path_file = os.path.abspath(file)

            if not (path_file in conf['PATHS'].keys()):
                create_backup_dir(path_file, conf['CONFIG']['namespace'])

            create_backup(args.append, alias_of_path(path_file))
        else:
            print('bckp: cannot stat ' + file + ': No such file or directory')

def create_backup_dir(path_file, id):
    alias = alias_of_path(path_file) if alias_of_path(path_file) is not False else str(uuid.uuid5(uuid.UUID(id), path_file))
    alias_dir = '/etc/backup/' + alias
    aliasConf = alias_dir + '/.bk.data'

    backConf = ConfigParser()
    backConf.optionxform = lambda x: x
    backConf.read(aliasConf)

    global conf
    global confFile

    conf['PATHS'] = {path_file : alias}
    with open(confFile, 'w') as f:
        conf.write(f)

    call('mkdir ' + alias_dir, shell = True)
    call('touch ' + aliasConf, shell = True)
    backConf['DEFAULT']={}
    backConf['DEFAULT']['path'] = path_file

def create_backup(append, alias):
    alias_dir = '/etc/backup/' + alias
    aliasConf = alias_dir + '/.bk.data'
    file = path_of_alias(alias)

    backConf = ConfigParser()
    backConf.optionxform = lambda x: x
    backConf.read(aliasConf)
    actualVersion = '0'        
    
    if append:
        actualVersion = str(getLastVersion(aliasConf) + 1)
    else:
        backConf.sections().clear()

    backConf[actualVersion]={}
    backConf[actualVersion]['mode'] = oct(os.stat(file).st_mode)[-3:]
    backConf[actualVersion]['owner'] = getpwuid(os.stat(file).st_uid).pw_name
    backConf[actualVersion]['group'] = getgrgid(os.stat(file).st_gid).gr_name
    backConf[actualVersion]['date'] = time.ctime()

    with open(aliasConf, 'w') as f:
        backConf.write(f)

    call('chmod -R 644 ' + alias_dir, shell = True)

###############################################################################
#                               RESTORE  BACKUP                               #
###############################################################################

def restore_backup(args):
    return

###############################################################################
#                                CLEAR  BACKUP                                #
###############################################################################

def clear_backups(args):
    call("find /etc/backup/* -not -name '.bckp.conf' -exec rm -rdf {} +", shell = True)

###############################################################################
#                                REMOVE BACKUP                                #
###############################################################################

def remove_backup(args):
    return

###############################################################################

if getuser() == 'root':

    conf = ConfigParser()
    conf.optionxform = lambda x: x
    confFile = '/etc/backup/.bckp.conf'
    conf.read(confFile)

    str_list        = 'list the backups and information about them'
    str_list_info   = 'list all information about the backups'
    str_list_owner  = 'list the owner of the backups'
    str_list_time   = 'list the time of the backups'
    str_list_mode   = 'list the mode of the backups'
    str_list_path   = 'list the path of the backups'

    str_add     = 'add a new backup'
    str_append  = 'if the backup already exists, a new one will be created instead of replacing the existing one'
    str_message = 'message to identify the backup'
    str_file    = 'file we want to make a backup'

    str_restore = 'restores the backup'
    str_name    = 'name of the backup'

    str_remove  = 'removes the original file when backup is created'

    str_clear   = 'removes all backups'

    parser = ArgumentParser(description = 'This command create, update a backup for a file')
    subparsers = parser.add_subparsers(help='sub-command help')

    parser_list = subparsers.add_parser('list', help=str_list)
    parser_list.set_defaults(func=list_backup)
    parser_list.add_argument('-i',  '--list_info',  help = str_list_info,   action = 'store_true')
    parser_list.add_argument('-p',  '--list_path',  help = str_list_path,   action = 'store_true')
    parser_list.add_argument('-o',  '--list_owner', help = str_list_owner,  action = 'store_true')
    parser_list.add_argument('-t',  '--list_time',  help = str_list_time,   action = 'store_true')

    parser_add = subparsers.add_parser('add', help=str_add)
    parser_add.set_defaults(func=add_backup)
    parser_add.add_argument('-a',   '--append',     help = str_append,  action = 'store_true')
    parser_add.add_argument('-m',   '--message',    help = str_message,  type=str, nargs=1)
    parser_add.add_argument('file', nargs = '+',    help = str_file)

    parser_restore = subparsers.add_parser('restore', help=str_restore)
    parser_restore.set_defaults(func=restore_backup)
    parser_restore.add_argument('name', nargs = 1,  help = str_name, type=str)

    parser_remove = subparsers.add_parser('remove', help=str_remove)
    parser_remove.set_defaults(func=remove_backup)
    parser_remove.add_argument('name', nargs = 1,  help = str_name, type=str)

    parser_clear = subparsers.add_parser('clear', help=str_clear)
    parser_clear.set_defaults(func=clear_backups)

    args = parser.parse_args()
    args.func(args)

else:
    print('bckp: cannot create backup for the file: Permission denied')
