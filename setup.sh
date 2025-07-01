#!/bin/bash

# ----------------------------------------------------------
# Flatpak Information
# ----------------------------------------------------------

app="com.ml4w.hyprlandsettings"
repo="ml4w-repo"
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

_is_flatpak_repo_installed() {
	local repo_name="$1"
	flatpak_output=$(flatpak remotes)
	if [[ $flatpak_output == *"$repo_name"* ]]; then
		echo ":: Repo '$repo_name' is already added."
		return 0
	else
		echo ":: Repo '$repo_name' is NOT added."
		return 1
	fi
}

# ----------------------------------------------------------
# Check if flatpak is already installed in repo
# ----------------------------------------------------------

_is_flatpak_installed() {
  if flatpak list --columns=application,origin | grep -qE "^$app\s+$repo$"; then
    echo ":: Flatpak '$app' from repository '$repo' is installed."
    return 0
  else
    echo ":: Flatpak '$app' from repository '$repo' is NOT installed."
    return 1
  fi
}

# ----------------------------------------------------------
# Check if flatpak is user installed
# ----------------------------------------------------------

_is_flatpak_installed_user() {
	flatpak_output=$(flatpak list --user --columns=application,origin)
	if [[ $flatpak_output == *"$app"* ]]; then
		echo ":: Flatpak '$app' is installed for the current user but should be installed system-wide."
		echo ":: It will now be uninstalled first."
		return 0
	else
		echo ":: Flatpak '$app' is NOT installed for the current user."
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

if ! _is_flatpak_repo_installed "flathub"; then
	sudo flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
fi

# ----------------------------------------------------------
# Adding ml4w-repo
# ----------------------------------------------------------

if ! _is_flatpak_repo_installed "ml4w-repo"; then
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
	sudo flatpak remote-add --if-not-exists ml4w-repo https://mylinuxforwork.github.io/ml4w-flatpak-repo/ml4w-apps.flatpakrepo --gpg-import=$HOME/.cache/$public_key
fi

# ----------------------------------------------------------
# Cleanup
# ----------------------------------------------------------

if [ -f "$HOME/.cache/$public_key" ]; then
	echo ":: Removing public key of $repo"
	rm "$HOME/.cache/$public_key"
fi

# ----------------------------------------------------------
# Uninstall app from current user
# ----------------------------------------------------------

if _is_flatpak_installed_user "$app"; then
	flatpak uninstall -y --user $app
fi

# ----------------------------------------------------------
# Install app
# ----------------------------------------------------------

if _is_flatpak_installed $app ml4w-repo; then
	echo ":: Checking updates for '$app'"
	flatpak -y update $app
else
	echo ":: Installing $app"
	sudo flatpak install -y --reinstall ml4w-repo $app
fi

# ----------------------------------------------------------
# Finishing up
# ----------------------------------------------------------

echo
echo ":: Setup complete. Run the app with 'flatpak run $app'"