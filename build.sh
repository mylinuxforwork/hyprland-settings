#!/bin/bash
rm -rf ~/tmp
mkdir ~/tmp
cp -r . ~/tmp
rm -rf ~/tmp/.git
rm -rf ~/tmp/release
rm -rf ~/tmp/screenshots
rm ~/tmp/.gitignore
rm ~/tmp/build.sh
rm ~/tmp/install.sh
cd ..
ARCH=x86_64 appimagetool tmp
echo ":: AppImage created"
# cp ML4W_Hyprland_Settings-x86_64.AppImage ~/hyprland-settings/release/
cp ML4W_Hyprland_Settings-x86_64.AppImage ~/dotfiles-versions/dotfiles/dotfiles/apps/
echo ":: AppImage copied to ~/dotfiles-versions/dotfiles/dotfiles/apps/"
