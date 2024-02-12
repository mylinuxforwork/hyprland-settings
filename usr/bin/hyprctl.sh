#!/bin/bash
if [ ! -f hyprctl2.json ] ;then
    echo "ERROR: hyprctl.json not found"
    exit 1
fi
readarray hyprctl < <(jq '.[]' hyprctl.json)
counter=0
for value in "${hyprctl[@]}"
do
    key=$(jq 'keys | .['$counter']' hyprctl.json)
    IFS='"' read -ra key <<< "$key"
    hyprctl keyword ${key[1]} $value
    ((counter++))
done