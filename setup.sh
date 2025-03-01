#!/bin/bash
runtime="org.gnome.Platform/x86_64/47"
app="com.ml4w.hyprlandsettings"
download="https://github.com/mylinuxforwork/hyprland-settings/releases/latest/download/$app.flatpak"

_commandExists() {
    package="$1"
    if ! type $package >/dev/null 2>&1; then
        echo 1
    else
        echo 0
    fi
}

_checkFlatpakAppExists() {
	app="$1"
	flatpak_output=$(flatpak info $runtime)
	if [[ $flatpak_output == *"ID:"* ]]; then
	  	echo 0
	else
		echo 1
	fi
}

# Check for flatpak
if [ "$(_commandExists "flatpak")" == "1" ]; then
	echo "ERROR: Please install flatpak first."
	exit
fi

# Adding flathub remote
flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo

# Check for runtime
if [ "$(_checkFlatpakAppExists "$runtime")" == "1" ]; then
	echo
	echo ":: Installing runtime $runtime"
	sudo flatpak -y install $runtime
fi

# Download app
echo
echo ":: Downloading $app"
if [ ! -d "$HOME/.cache" ]; then
	mkdir -p "$HOME/.cache"
fi
wget -P "$HOME/.cache" "$download"

# Install app
cd "$HOME/.cache"
flatpak --user -y --reinstall install $app.flatpak

echo
echo ":: Setup complete. Run the app with flatpak run $app"
