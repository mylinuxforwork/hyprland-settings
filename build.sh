#!/bin/bash
rm -rf ~/tmp
mkdir ~/tmp
cp -r . ~/tmp
rm -rf ~/tmp/.git
rm ~/tmp/.gitignore
cd ..
ARCH=x86_64 appimagetool tmp
echo ":: AppImage created"
# cp ML4W_Hyprland_Settings-x86_64.AppImage ~/ml4w-hyprland-settings/
cp ML4W_Hyprland_Settings-x86_64.AppImage ~/dotfiles-versions/dotfiles/apps/
echo ":: AppImage copied to ~/dotfiles-versions/dotfiles/apps/"
