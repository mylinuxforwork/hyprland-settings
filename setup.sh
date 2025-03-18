#!/bin/bash
# Created with Packages Installer 0.5
# https://github.com/mylinuxforwork/packages-installer

clear
# Seperator
_sep() {
	echo "----------------------------------------------------"
}

# Spacer
_space() {
	echo
}

# Default
assumeyes=1
cmdoutput=1

# Options
while getopts y?h?o? option
do
    case "${option}"
        in
        y|\?)
	        assumeyes=0
        	;;
        o|\?)
	        cmdoutput=0
        	;;
        h|\?)
		echo "Created with Packages Installer"
		echo
		echo "Usage:"
		echo "-y Skip confirmation"
		echo "-o Show installation command outputs"
		echo "-h Help"
		exit
        	;;
    esac
done

# Variables


# Is installed
_isInstalled_flatpak() {
	package="$1"
	check=$(flatpak info ${package})
	if [[ $check == *"ID:"* ]]; then
	  	echo 0
	else
		echo 1
	fi
}

# Add flathub remote
flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo > /dev/null 2>&1


# Header
_sep
echo "Hyprland Settings App"
echo "Installation script for the ML4W Hyprland Settings App"
_space
echo "Created with Packages Installer"
_sep
_space
echo "IMPORTANT: Please make sure that your system is updated before starting the installation."
_space

# Confirm Start
if [ $assumeyes == 1 ]; then
	while true; do
		read -p "DO YOU WANT TO START THE INSTALLATION NOW? (Yy/Nn): " yn
		case $yn in
		    [Yy]*)
		        break
		        ;;
		    [Nn]*)
		        echo ":: Installation canceled"
		        exit
		        break
		        ;;
		    *)
		        echo ":: Please answer yes or no."
		        ;;
		esac
	done
fi

# sudo permissions
sudo -v
_space

# Packages
check_isinstalled="True"
if [ $check_isinstalled == "true" ]; then
	if [[ $(_isInstalled_apt "org.gnome.Platform/x86_64/47") == 0 ]]; then
		echo ":: org.gnome.Platform/x86_64/47 is already installed"
	else
		echo ":: Installing org.gnome.Platform/x86_64/47..."
		if [ $cmdoutput == 1 ]; then
			flatpak -y install "org.gnome.Platform/x86_64/47" > /dev/null 2>&1
		else
			flatpak -y install "org.gnome.Platform/x86_64/47"
		fi
	fi
else
	echo ":: Installing org.gnome.Platform/x86_64/47..."
	if [ $cmdoutput == 1 ]; then
		flatpak -y --reinstall install "org.gnome.Platform/x86_64/47" > /dev/null 2>&1
	else
		flatpak -y --reinstall install "org.gnome.Platform/x86_64/47"
	fi
fi

if [ ! -d $HOME/.cache ]; then
	mkdir -p $HOME/.cache
fi
wget -q -P "$HOME/.cache" "https://github.com/mylinuxforwork/hyprland-settings/releases/latest/download/com.ml4w.hyprlandsettings.flatpak"
cd "$HOME/.cache"
echo ":: Installing com.ml4w.hyprlandsettings.flatpak"
if [ $cmdoutput == 1 ]; then
	flatpak --user -y --reinstall install com.ml4w.hyprlandsettings.flatpak > /dev/null 2>&1
else
	flatpak --user -y --reinstall install com.ml4w.hyprlandsettings.flatpak
fi
rm "$HOME/.cache/com.ml4w.hyprlandsettings.flatpak"


_space

# Success Message
_sep
echo "Done!"
_sep