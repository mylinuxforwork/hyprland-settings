#!/bin/bash
if [ ! -f hyprctl.json ] ;then
    echo "ERROR: hyprctl.json not found"
    exit 1
fi

jq -c '.[]' hyprctl.json | while read i; do
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
