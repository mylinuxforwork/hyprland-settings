# ML4W Hyprland Settings App

This applications supports you to customize your Hyprland installation. You can overwrite the existing configuration with custom values without adding complex configuration files.

# Installation

The app is available as flatpak but requires currently a manual installation and update.

You can download the app here: 

https://raw.githubusercontent.com/mylinuxforwork/dotfiles/main/share/apps/com.ml4w.hyprlandsettings.flatpak

```
# Install Flatpak on your distribution
# https://flatpak.org/setup/

# Add flathub remote
flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo

# Install the runtime
flatpak -y install org.gnome.Platform/x86_64/47

# Open the Download folder
cd ~/Downloads

# Install the flatpak
flatpak --user install com.ml4w.hyprlandsettings.flatpak
```

# Update

You can download the latest version here: 

https://raw.githubusercontent.com/mylinuxforwork/dotfiles/main/share/apps/com.ml4w.hyprlandsettings.flatpak

```
# Open the Download folder
cd ~/Downloads

# Install the flatpak
flatpak --user -y --reinstall install com.ml4w.hyprlandsettings.flatpak
```
