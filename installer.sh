#!/bin/bash

check_for_bckp() {
    if [ -d /etc/backup ]; then
        echo "Backup directory found"
        return 1
    fi
    if [ -f /usr/bin/bckp ]; then
        echo "bckp command found"
        return 1
    fi
    return 0
}

bckp() {
    check_for_bckp
    if [ $? -eq 1 ]; then
        echo "bckp already installed"
        return 0
    fi
    echo "Installing bckp command"
    chmod +x src/bckp.py
    cp src/bckp.py /usr/bin/bckp
    mkdir -p /etc/backup/
    return 1
}

show_help() {
    echo "Usage: instalador.sh [OPTION]"
    echo "Options:"
    echo "  -h, --help          Show this help message and exit"
    echo "  -i, --install       Install bckp"
    echo "  -u, --uninstall     Uninstall bckp"
    exit 0
}

###############################################################################

# implementa help para el instalador que se llama con el comando -h o --help, la ayuda debe estar en inglés
if [ "$1" = "-h" ] || [ "$1" = "--help" ] || [ $# -eq 0 ]; then
    show_help
fi

if [ "$(id -u)" = "0" ]; then
    if [ "$1" = "-u" ]; then
        echo "Uninstalling bckp"
        rm /usr/bin/bckp
        rm -r /etc/backup
        check_for_bckp
        if [ $? -eq 0 ]; then
            echo "Uninstallation complete"
        else
            echo "Uninstallation failed"
        fi    
    elif [ "$1" = "-i" ]; then
        bckp 
        if [ $? -eq 1 ]; then
            echo "Installation complete"
        else
            echo "Installation failed"
        fi    
    else
        echo "Error: invalid parameters"
    fi
else
    echo "This script must be run as root" 1>&2
fi

