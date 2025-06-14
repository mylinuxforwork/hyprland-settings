#!/bin/bash

# ----------------------------------------------------------
# Flatpak Information
# ----------------------------------------------------------

app="com.ml4w.hyprlandsettings"
public_key="ml4w-apps-public-key.asc"
public_key_url="https://mylinuxforwork.github.io/ml4w-flatpak-repo/$public_key"

# ----------------------------------------------------------
# Check if command exists
# ----------------------------------------------------------

_commandExists() {
    local package="$1"
    if ! type $package >/dev/null 2>&1; then
        return 1
    else
        return 0
    fi
}

# ----------------------------------------------------------
# Check if flatpak repo is installed
# ----------------------------------------------------------

is_flatpak_repo_installed() {
  local repo_name="$1"
  flatpak_output=$(flatpak remotes)
  if [[ $flatpak_output == *"$repo_name"* ]]; then
    return 0
  else
    return 1
  fi
}

# ----------------------------------------------------------
# Check if flatpak is already installed
# ----------------------------------------------------------

if ! _commandExists "flatpak"; then
	echo "ERROR: Please install flatpak first."
	exit
fi

# ----------------------------------------------------------
# Check if wget is already installed
# ----------------------------------------------------------

if ! _commandExists "wget"; then
	echo "ERROR: Please install wget first."
	exit
fi

# ----------------------------------------------------------
# Adding flathub
# ----------------------------------------------------------

if is_flatpak_repo_installed "flathub"; then
	echo ":: flathub is already added."
else
	echo ":: Adding flathub"
	flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
fi

# ----------------------------------------------------------
# Adding ml4w-repo
# ----------------------------------------------------------

if is_flatpak_repo_installed "ml4w-repo"; then
	echo ":: ml4w-repo is already added."
else
	echo ":: Downloading Public Key"
	if [ ! -d "$HOME/.cache" ]; then
		mkdir -p "$HOME/.cache"
	fi
	if [ -f "$HOME/.cache/$public_key" ]; then
		rm "$HOME/.cache/$public_key"
	fi
	wget -P "$HOME/.cache" "$public_key_url"
	if [ ! -f "$HOME/.cache/$public_key" ]; then
		echo "ERROR: Download of Public Key failed."
		exit
	fi	
	echo ":: Adding ml4w-repo"
	flatpak remote-add --user --if-not-exists ml4w-repo https://mylinuxforwork.github.io/ml4w-flatpak-repo/ml4w-apps.flatpakrepo --gpg-import=$HOME/.cache/$public_key
fi

# ----------------------------------------------------------
# Install app
# ----------------------------------------------------------

echo ":: Installing $app"
flatpak -y install --reinstall --user ml4w-repo $app

# ----------------------------------------------------------
# Cleanup
# ----------------------------------------------------------

if [ -f "$HOME/.cache/$public_key" ]; then
	rm "$HOME/.cache/$public_key"
fi

# ----------------------------------------------------------
# Finishing up
# ----------------------------------------------------------

echo
echo ":: Setup complete. Run the app with flatpak run $app"