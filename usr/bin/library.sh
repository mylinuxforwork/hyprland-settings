#!/bin/bash

# _replaceInFile $startMarker $endMarker $customtext $targetFile
_replaceInFile() {

    # Set function parameters
    start_string=$1
    end_string=$2
    new_string="$3"
    file_path=$4

    # Counters
    start_line_counter=0
    end_line_counter=0
    start_found=0
    end_found=0

    if [ -f $file_path ] ;then

        # Detect Start String
        while read -r line
        do
            ((start_line_counter++))
            if [[ $line = *$start_string* ]]; then
                # echo "Start found in $start_line_counter"
                start_found=$start_line_counter
                break
            fi 
        done < "$file_path"

        # Detect End String
        while read -r line
        do
            ((end_line_counter++))
            if [[ $line = *$end_string* ]]; then
                # echo "End found in $end_line_counter"
                end_found=$end_line_counter
                break
            fi 
        done < "$file_path"

        # Check that deliminters exists
        if [[ "$start_found" == "0" ]] ;then
            echo "ERROR: Start deliminter not found."
            sleep 2
        fi
        if [[ "$end_found" == "0" ]] ;then
            echo "ERROR: End deliminter not found."
            sleep 2
        fi

        # Replace text between delimiters
        if [[ ! "$start_found" == "0" ]] && [[ ! "$end_found" == "0" ]] && [ "$start_found" -le "$end_found" ] ;then
            # Remove the old line
            ((start_found++))

            if [ ! "$start_found" == "$end_found" ] ;then    
                ((end_found--))
                sed -i "$start_found,$end_found d" $file_path
            fi
            # Add the new line
            sed -i "$start_found i $new_string" $file_path
        else
            echo "ERROR: Delimiters syntax."
            sleep 2
        fi
    else
        echo "ERROR: Target file not found."
        sleep 2
    fi
}

# replaceLineInFile $findText $customtext $targetFile
_replaceLineInFile() {
   # Set function parameters
    find_string="$1"
    new_string="$2"
    file_path=$3

    # Counters
    find_line_counter=0
    line_found=0

    if [ -f $file_path ] ;then

        # Detect Line
        while read -r line
        do
            ((find_line_counter++))
            if [[ $line = *$find_string* ]]; then
                # echo "Start found in $start_line_counter"
                line_found=$find_line_counter
                break
            fi 
        done < "$file_path"

        if [[ ! "$line_found" == "0" ]] ;then
            
            #Remove the line
            sed -i "$line_found d" $file_path

            # Add the new line
            sed -i "$line_found i $new_string" $file_path            

        else
            echo "ERROR: Target line not found."
            sleep 2
        fi   

    else
        echo "ERROR: Target file not found."
        sleep 2
    fi
}

# _writeSettings $settingsFile $customtext
_writeSettings() {
    if [ ! -f $1 ] ;then
        touch $1
    fi
    echo "$2" > $1
}

# _writeConf conf/monitor.conf $sel
_writeConf() {
    if [ ! -z $2 ] ;then
        editsel=$(echo "$installFolder/conf/$3/$2" | sed "s+"\/home\/$USER"+~+")
        echo "source = $editsel" > $installFolder/conf/$1
    fi
}

# Reload Waybar
# setsid $HOME/dotfiles/waybar/launch.sh 1>/dev/null 2>&1 &