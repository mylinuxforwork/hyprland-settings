#!/bin/bash
clear

# Check if package is installed
_isInstalledPacman() {
    package="$1";
    check="$(sudo pacman -Qs --color always "${package}" | grep "local" | grep "${package} ")";
    if [ -n "${check}" ] ; then
        echo 0; #'0' means 'true' in Bash
        return; #true
    fi;
    echo 1; #'1' means 'false' in Bash
    return; #false
}

# Install required packages
_installPackagesPacman() {
    toInstall=();
    for pkg; do
        if [[ $(_isInstalledPacman "${pkg}") == 0 ]]; then
            echo "${pkg} is already installed.";
            continue;
        fi;
        toInstall+=("${pkg}");
    done;
    if [[ "${toInstall[@]}" == "" ]] ; then
        # echo "All pacman packages are already installed.";
        return;
    fi;
    printf "Package not installed:\n%s\n" "${toInstall[@]}";
    sudo pacman --noconfirm -S "${toInstall[@]}";
}

# Required packages for the installer
packages=(
    "wget"
    "unzip"
    "gum"
    "jq"
    "fuse2" 
    "gtk4" 
    "libadwaita" 
    "python"
    "python-gobject"

)

# Some colors
GREEN='\033[0;32m'
NONE='\033[0m'

# Header
echo -e "${GREEN}"
cat <<"EOF"
 ___           _        _ _           
|_ _|_ __  ___| |_ __ _| | | ___ _ __ 
 | || '_ \/ __| __/ _` | | |/ _ \ '__|
 | || | | \__ \ || (_| | | |  __/ |   
|___|_| |_|___/\__\__,_|_|_|\___|_|   
                                      
EOF
echo "for ML4W Hyprland Settings App"
echo
echo -e "${NONE}"
echo "This script will support you to download and install the ML4W Hyprland Settings App."
echo
while true; do
    read -p "DO YOU WANT TO START THE INSTALLATION NOW? (Yy/Nn): " yn
    case $yn in
        [Yy]* )
            echo "Installation started."
            echo
        break;;
        [Nn]* ) 
            echo "Installation canceled."
            exit;
        break;;
        * ) echo "Please answer yes or no.";;
    esac
done

# Synchronizing package databases
sudo pacman -Sy
echo

# Install required packages
echo ":: Checking that required packages are installed..."
_installPackagesPacman "${packages[@]}";
echo

# Decide on installation directory
echo ":: Installation started"
if [ ! -d $HOME/.local/share/applications/ ] ;then
    mkdir -p $HOME/.local/share/applications/
    echo ":: $HOME/.local/share/applications/ created"
fi
if [ ! -d ~/apps ] ;then
    mkdir ~/apps
    echo ":: apps folder created in $HOME"
fi
cp release/ML4W_Hyprland_Settings-x86_64.AppImage ~/apps
cp icon.png ~/.local/share/applications/ml4w-hyprland-settings.png
cp ml4w-hyprland-settings.desktop ~/.local/share/applications

APPIMAGE="$HOME/apps/ML4W_Hyprland_Settings-x86_64.AppImage"
ICON="$HOME/.local/share/applications/ml4w-hyprland-settings.png"
sed -i "s|HOME|${APPIMAGE}|g" $HOME/.local/share/applications/ml4w-hyprland-settings.desktop
sed -i "s|icon|${ICON}|g" $HOME/.local/share/applications/ml4w-hyprland-settings.desktop

echo 
echo "DONE!" 
echo "Please add the following command to your hyprland.conf of you want to restore the changes after logging in."
echo "exec-once = ~/.config/ml4w-hyprland-settings/hyprctl.sh"
echo 
echo "You can start the app from your application launcher or with the terminal from the folder apps."