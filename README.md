# ML4W Hyprland Settings App

This applications supports you to customize your Hyprland installation. You can overwrite the existing configuration with custom values without adding complex configuration files.

![image](https://github.com/user-attachments/assets/dd1eb200-ccfe-46d6-8137-de6b10abf0b9)

# Requirements

The ML4W Hyprland Settings App can only be launched from a running Hyprland Session.

```
# Install Flatpak on your distribution
# https://flatpak.org/setup/

# Add flathub remote
flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo

# Install the runtime
sudo flatpak -y install org.gnome.Platform/x86_64/47
```

# Installation

The app is now available as flatpak but requires currently a manual installation and update.

Visit the releases page (https://github.com/mylinuxforwork/hyprland-settings/releases) and download the file com.ml4w.hyprlandsettings.flatpak

```
# Open the Download folder
cd ~/Downloads

# Install the flatpak
flatpak --user install com.ml4w.hyprlandsettings.flatpak
```

# Update

Visit the releases page (https://github.com/mylinuxforwork/hyprland-settings/releases) and download the file com.ml4w.hyprlandsettings.flatpak

```
# Open the Download folder
cd ~/Downloads

# Install the flatpak
flatpak --user -y --reinstall install com.ml4w.hyprlandsettings.flatpak
```
