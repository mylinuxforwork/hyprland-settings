#!/bin/bash
#  _                          _   _ 
# | |__  _   _ _ __  _ __ ___| |_| |
# | '_ \| | | | '_ \| '__/ __| __| |
# | | | | |_| | |_) | | | (__| |_| |
# |_| |_|\__, | .__/|_|  \___|\__|_|
#        |___/|_|                   
# 
# Execute this file in the hyprland.conf with exec-always

script=$(readlink -f $0)
path=$(dirname $script)
if [ ! -f $path/hyprctl.json ] ;then
    echo "ERROR: hyprctl.json not found"
    exit 1
fi

jq -c '.[]' $path/hyprctl.json | while read i; do
    _val() {
        echo $1 | jq -r '.value'
    }
    _key() {
        echo $1 | jq -r '.key'
    }
    key=$(_key $i)
    val=$(_val $i)
    echo "Execute: hyprctl keyword $key $val"
    hyprctl keyword $key $val
done
