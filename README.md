# ML4W Hyprland Settings App

This applications supports you to customize your Hyprland installation. You can overwrite the existing configuration with custom values without adding complex configuration files.

![image](https://github.com/user-attachments/assets/6f56dbc8-9db5-445e-81df-b4156473b397)

![image](https://github.com/user-attachments/assets/3688f2ef-47fe-49ff-b45a-eef4c39c043a)

# Requirements

The ML4W Hyprland Settings App can only be launched from a running Hyprland Session.

```
# Install Flatpak on your distribution
# https://flatpak.org/setup/

```
# Installation

You can install the app with this command from your terminal.

```
bash <(curl -s https://raw.githubusercontent.com/mylinuxforwork/hyprland-settings/master/setup.sh)
```
After the installation you can start the app with:

```
flatpak run com.ml4w.hyprlandsettings
```
To restore the changes after every login into Hyprland, please add the following line to your hyprland.conf

```
exec = ~/.config/com.ml4w.hyprlandsettings/hyprctl.sh
```
# Update

Just run the installation again.

# Configuration

In the folder ~/.config/com.ml4whyprlandsettings, you will also find the stored values that you have set with the app.


