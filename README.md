# ML4W Hyprland Settings 1.0 BETA 1

This applications supports you to customize your Hyprland installation. You can overwrite the existing configuration with custom values without adding complex configuration files.

[![Screenshot](screenshots/screenshot.png "Title Text")](screenshots/screenshot.png)

# Installation

You can use the integrated installer script to setup the application on your system.

<a href="https://gitlab.com/stephan-raabe/ml4w-hyprland-settings/-/raw/main/install.sh?ref_type=heads&inline=false">Download the install.sh file here</a>

```
# 1.) Change into to the downloads folder
cd ~/Downloads

# 2.) Make the install.sh executable
chmod +x install.sh

# 3.) Start the installation
./install.sh

```

# How to use it

You can start the application from your application launcher or with your terminal from the apps folder with

```
# 1.) Change into to the apps folder
cd ~/apps

# 2.) Start the app
./ML4W_Hyprland_Settings-x86_64.AppImage

```

The app shows variables and current values of your running Hyprland.

You can change the values and overwrite the existing values. The change will be axecuted immediatly.

In the Set Variables tab you can see which values you have overwritten and can restore the old values be removing the entry.

To restore the changes after a later login or after a reboot, please add the following line to your hyprland.conf

```
exec-once = ~/.config/ml4w-hyprland-settings/hyprctl.sh
```

# Dependencies

- jp
- fuse2
- gtk4
- libadwaita
