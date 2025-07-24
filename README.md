# ML4W Hyprland Settings App

This applications supports you to customize your Hyprland installation. You can overwrite the existing configuration with custom values without editing complex configuration files. 

The ML4W Hyprland Settings App utilizes hyprctl. It is a utility for controlling some parts of the compositor from a CLI or a script. 

![image](https://github.com/user-attachments/assets/6f56dbc8-9db5-445e-81df-b4156473b397)

![image](https://github.com/user-attachments/assets/3688f2ef-47fe-49ff-b45a-eef4c39c043a)

# Installation

The ML4W Hyprland Settings App requires Flatpak:

```
# Install Flatpak on your distribution
# https://flatpak.org/setup/

```

Copy the following command into your terminal.

```
bash -c "$(curl -s https://raw.githubusercontent.com/mylinuxforwork/hyprland-settings/master/setup.sh)"
```

After the installation you can start the app from your application launcher or with the command:

```
flatpak run com.ml4w.hyprlandsettings
```

## Update

You can check and update the app with the following command:

```
flatpak update com.ml4w.hyprlandsettings 
```

## Uninstall

```
flatpak uninstall com.ml4w.hyprlandsettings
```

# Load changes after login

To load your changes after every login into Hyprland and to restore your values, please add the following line to your hyprland.conf

```
exec = ~/.config/com.ml4w.hyprlandsettings/hyprctl.sh
```

# Configuration

In the folder ~/.config/com.ml4w.hyprlandsettings, you will find the stored values that you have set with the app.


