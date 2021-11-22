#!/usr/bin/python3
from subprocess import call
from getpass import getuser
from pwd import getpwuid
from grp import getgrgid
from sys import exit
import argparse
import os
import time

#############################################################################################################

def get_bup_info(file):
    file = file if call('[ ! -f ' + file + ' ]', shell = True) else file+'/.bk.data'
    with open(file, 'r') as f:
        f.seek(51)
        path = f.readline()[9:-1]
        mod = f.readline()[9:-1]
        own = f.readline()[9:-1]
        grp = f.readline()[9:-1]
        mdt = f.readline()[9:-1]
        f.seek(f.tell() + 51, os.SEEK_SET)
        content = f.read()
    return path, mod, own, grp, mdt, content

def file_name(file, append):
    max = '-1'
    # si file es una ruta obten la ultima parte de la ruta
    if '/' in file:
        file = file.split('/')[-1]
    print(max)
    if append:
        with os.scandir('/etc/backup/') as dir:
            for files in dir:
                if files.name[:len(file)] == file:
                    print(files.name)
                    actual = files.name[len(file)+4:]
                    print('actual: ' + actual)
                    max = actual if int(actual) > int(max) else max
                    print('max: ' + max)

    max = str(int(max) + 1)
    print('maxfin: ' + max)
    return '/etc/backup/' + file + '~bk_' + max

def create_f_backup(file, append):
    dest = file_name(file, append)
    call('touch ' + dest, shell = True)
    with open(dest, 'w') as f:
        f.write('##################################################\n')
        f.write('# path:  ' + os.path.abspath(file) + '\n')
        f.write('# mode:  ' + oct(os.stat(file).st_mode)[-3:] + '\n')
        f.write('# owner: ' + getpwuid(os.stat(file).st_uid).pw_name + '\n')
        f.write('# group: ' + getgrgid(os.stat(file).st_gid).gr_name + '\n')
        f.write('# date:  ' + time.ctime() + '\n')
        f.write('##################################################\n')
        with open(file, 'r') as src:
            content = src.read()
            f.write(content)
    call('chmod 444 ' + dest, shell = True)

def create_d_backup(file, append):
    dest = file_name(file, append)
    conf = dest + '/.bk.data'
    call('cp -r ' + file + ' ' + dest, shell = True)
    call('cd ' + dest, shell = True)
    call('touch ' + conf, shell = True)
    with open(conf, 'w') as f:
        f.write('##################################################\n')
        f.write('# path:  ' + os.path.abspath(file) + '\n')
        f.write('# mode:  ' + oct(os.stat(file).st_mode)[-3:] + '\n')
        f.write('# owner: ' + getpwuid(os.stat(file).st_uid).pw_name + '\n')
        f.write('# group: ' + getgrgid(os.stat(file).st_gid).gr_name + '\n')
        f.write('# date:  ' + time.ctime() + '\n')
        f.write('##################################################\n')
    call('chmod -R 444 ' + dest, shell = True)

def restore_f_backup(file):
    file = '/etc/backup/' + file
    path, mod, own, grp, mdt, content = get_bup_info(file)

    if exist_file(path, 0):
        call('rm ' + path, shell = True)
    call('touch ' + path,  shell = True)
    call('chmod ' + mod + ' ' + path, shell = True)
    call('chown ' + own + ' ' + path, shell = True)
    call('chgrp ' + grp + ' ' + path, shell = True)
    with open(path, 'w') as f:
        f.write(content)

def restore_d_backup(file):
    file = '/etc/backup/' + file
    path, mod, own, grp, mdt, content = get_bup_info(file)

    call('rm -r ' + path, shell = True)
    call('cp -r ' + file + ' ' + path,  shell = True)
    call('chmod ' + mod + ' ' + path, shell = True)
    call('chown ' + own + ' ' + path, shell = True)
    call('chgrp ' + grp + ' ' + path, shell = True)
    call('rm ' + path + '/.bk.data', shell = True)


def end_info(n):
    return u'  \u2514 ' if n == 0 else u'  \u251c '

def list_backups(flags):
    with os.scandir('/etc/backup/') as dir:
        for file in dir:
            path, mod, own, grp, mdt, content = get_bup_info(file.path)
            print('* ' + file.name + ':')
            if flags != [1,0,0,0,0]:
                total = 2*flags[2] + 2*flags[3] + flags[4] if flags[1] == 0 else 5
                #print(' |')
            if flags[1] or flags[2]:
                total -= 2;
                print(u'  \u251c Path: '  + path)
                print(end_info(total) + 'Mode: '  + mod)
            if flags[1] or flags[4]:
                total -= 1
                print(end_info(total) + 'Date: '  + mdt)
            if flags[1] or flags[3]:
                total -= 2
                print(u'  \u251c Owner: ' + own)
                print(end_info(total) + 'Group: ' + grp)
            print()

def exist_file(file, restore):
    if restore:
        file = '/etc/backup/' + file
    return call('[ ! -f ' + file + ' ]', shell = True)

def exist_dir(file, restore):
    if restore:
        file = '/etc/backup/' + file
    return call('[ ! -d ' + file + ' ]', shell = True)

#############################################################################################################

if getuser() == 'root':

    str_list    = 'list all backups created'
    str_restore = 'restores the backup'
    str_remove  = 'removes the original file when backup is created'
    str_append  = 'if the backup already exists, a new one will be created instead of replacing the existing one'
    str_file    = 'file we want to make a backup'
    str_dir     = 'create a backup for a directory'
    str_clear   = 'removes all backups'

    parser = argparse.ArgumentParser(description = 'This command create, update a backup for a file')

    parser.add_argument('-l',  '--list',       help = str_list,    action = 'store_true')
    parser.add_argument('-a',  '--list_info',  help = str_list,    action = 'store_true')
    parser.add_argument('-p',  '--list_path',  help = str_list,    action = 'store_true')
    parser.add_argument('-o',  '--list_owner', help = str_list,    action = 'store_true')
    parser.add_argument('-t',  '--list_time',  help = str_list,    action = 'store_true')
    parser.add_argument('-r',  '--restore',    help = str_restore, action = 'store_true')
    parser.add_argument('-d',  '--remove',     help = str_remove,  action = 'store_true')
    parser.add_argument('-j',  '--append',     help = str_append,  action = 'store_true')
    parser.add_argument('-c',  '--clear',      help = str_clear,   action = 'store_true')

    parser.add_argument('file', nargs = '*', help = str_file)
    args = parser.parse_args()

    list_info = [args.list, args.list_info, args.list_path, args.list_owner, args.list_time]


    if list_info[0]:
        list_backups(list_info)
        exit()
    elif 1 in list_info:
        print('bckp: cannot use parameters a, p, o, d without l')
        exit()
    elif args.clear:
        call('rm -r /etc/backup/*', shell = True)
        exit()
    elif len(args.file) > 0:
        for n in range(len(args.file)):
            file = args.file[n]
            if file[-1] == '/':
                file = file[:-1]

            if exist_file(file, args.restore):
                if args.restore:
                    restore_f_backup(file)
                    if args.remove:
                        call('rm /etc/backup/' + file, shell = True)
                else:
                    create_f_backup(file, args.append)
                    if args.remove:
                        call('rm ' + file, shell = True)

            elif exist_dir(file, args.restore):
                if args.restore:
                    restore_d_backup(file)
                    if args.remove:
                        call('rm -R /etc/backup/' + file, shell = True)
                else:
                    create_d_backup(file, args.append)
                    if args.remove:
                        call('rm -R ' + file, shell = True)

            else:
                print('bckp: cannot stat ' + file + ': No such file or directory')
    else:
        print('bckp: missing file operand')

else:
    print('bckp: cannot create backup for the file: Permission denied')
