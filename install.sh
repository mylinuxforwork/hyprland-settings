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
    "jp"
    "fuse2" 
    "gtk4" 
    "libadwaita" 
    "python"
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
echo "for ML4W Hyprland Settings"
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

# Select the dotfiles version
wget -P ~/Downloads/ https://gitlab.com/stephan-raabe/ml4w-hyprland-settings/-/archive/main/ml4w-hyprland-settings-main.zip
echo ":: Download complete."
echo

# Unzip
unzip -o -q ~/Downloads/ml4w-hyprland-settings-main.zip -d ~/Downloads/
echo ":: Unzip complete."
cd $HOME/Downloads/dotfiles-ml4w-hyprland-settings-main
echo ":: Changed into ~/Downloads/ml4w-hyprland-settings-main/"

# Start the installatiom
if gum confirm "DO YOU WANT TO START THE INSTALLATION NOW?" ;then
    echo
    echo ":: Starting the installation now..."
    sleep 2

elif [ $? -eq 130 ]; then
        exit 130
else
    echo "Installation canceled."
    echo "You can start the installation manually with ~/Downloads/dotfiles-$version/install.sh"
    exit;
fi

# Decide on installation directory
if [ !-d ~/apps ] ;then
    mkdir ~/apps
fi
echo ":: Copy of files started"
cp release/ML4W_Hyprland_Settings-x86_64.AppImage ~/apps
cp icon.png ~/apps/ml4w-hyprland-settings.png
cp ml4w-hyprland-settings.desktop ~/.local/share/applications
echo 
echo "DONE! You can start the app from your application launcher or with the terminal from the folder apps."
