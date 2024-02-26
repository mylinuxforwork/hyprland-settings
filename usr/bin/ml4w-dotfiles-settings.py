#  __  __ _    _  ___        __  ____       _   _   _                 
# |  \/  | |  | || \ \      / / / ___|  ___| |_| |_(_)_ __   __ _ ___ 
# | |\/| | |  | || |\ \ /\ / /  \___ \ / _ \ __| __| | '_ \ / _` / __|
# | |  | | |__|__   _\ V  V /    ___) |  __/ |_| |_| | | | | (_| \__ \
# |_|  |_|_____| |_|  \_/\_/    |____/ \___|\__|\__|_|_| |_|\__, |___/
#                                                           |___/     
                                                             
import sys
import gi
import subprocess
import os
import threading
import json
import pathlib
import shutil

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, Gio
from gi.repository import GLib
from gi.repository import GObject

# Get script path
pathname = os.path.dirname(sys.argv[0])

# -----------------------------------------
# Define UI template
# -----------------------------------------
@Gtk.Template(filename = pathname + '/src/settings.ui')

# -----------------------------------------
# Main Window
# -----------------------------------------
class MainWindow(Adw.PreferencesWindow):
    __gtype_name__ = 'Ml4wSettingsWindow'
    waybar_show_bluetooth = Gtk.Template.Child()
    waybar_show_network = Gtk.Template.Child()
    waybar_show_chatgpt = Gtk.Template.Child()
    waybar_show_systray = Gtk.Template.Child()
    waybar_show_screenlock = Gtk.Template.Child()

    # Get objects from template
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

# -----------------------------------------
# Main App
# -----------------------------------------
class MyApp(Adw.Application):
    win = Adw.ApplicationWindow() # Application Window
    path_name = pathname # Path of Application
    homeFolder = os.path.expanduser('~') # Path to home folder
    dotfiles = homeFolder + "/dotfiles/"
    block_reload = True
    settings = {}

    waybar_themes = [
        "ml4w-minimal",
        "ml4w",
        "ml4w-blur",
        "ml4w-blur-bottom",
        "ml4w-bottom"
    ]

    def __init__(self, **kwargs):
        super().__init__(application_id='com.ml4w.dotfilessettings',
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS)
        self.create_action('quit', lambda *_: self.quit(), ['<primary>q'])
        self.create_action('waybar_show_bluetooth', self.on_waybar_show_bluetooth)

    def do_activate(self):
        # Define main window
        win = self.props.active_window
        if not win:
            win = MainWindow(application=self)

        # Load settings
        if not os.path.exists(self.dotfiles + ".settings/settings.json"):
            shutil.copy(self.path_name + '/settings.json', self.dotfiles + ".settings/")
        settings_file = open(self.dotfiles + ".settings/settings.json")
        settings_arr = json.load(settings_file)
        for row in settings_arr:
            self.settings[row["key"]] = row["value"]

        self.waybar_show_bluetooth = win.waybar_show_bluetooth
        self.waybar_show_network = win.waybar_show_network
        self.waybar_show_chatgpt = win.waybar_show_chatgpt
        self.waybar_show_systray = win.waybar_show_systray
        self.waybar_show_screenlock = win.waybar_show_screenlock
        
        # Bluetooth
        if self.settings["waybar_bluetooth"]:
            self.waybar_show_bluetooth.set_active(True)
        else:
            self.waybar_show_bluetooth.set_active(False)

        '''
        # Network
        if self.settings["waybar_network"]:
            self.waybar_show_network.set_active(False)
        else:
            self.waybar_show_network.set_active(True)

        # ChatGPT
        if self.settings["waybar_chatgpt"]:
            self.waybar_show_chatgpt.set_active(False)
        else:
            self.waybar_show_chatgpt.set_active(True)

        # Systray
        if self.settings["waybar_systray"]:
            self.waybar_show_systray.set_active(False)
        else:
            self.waybar_show_systray.set_active(True)

        # Systray
        if self.settings["waybar_screenlock"]:
            self.waybar_show_idle_inhibitor.set_active(False)
        else:
            self.waybar_show_idle_inhibitor.set_active(True)
        '''

        self.block_reload = False

        # Show Application Window
        win.present()
        print (":: Welcome to ML4W Dotfiles Settings App")

    def on_waybar_show_bluetooth(self, widget, _):
        if not self.block_reload:
            if self.waybar_show_bluetooth.get_active():
                for t in self.waybar_themes:
                    self.replaceInFile("waybar/themes/" + t + "/config",'"bluetooth"','"bluetooth",')
                self.updateSettings("waybar_bluetooth", True)
            else:
                for t in self.waybar_themes:
                    self.replaceInFile("waybar/themes/" + t + "/config",'"bluetooth"','//"bluetooth",')
                self.updateSettings("waybar_bluetooth", False)
            self.reloadWaybar()

    def updateSettings(self,keyword,value):
        result = []
        self.settings[keyword] = value
        for k, v in self.settings.items():
            result.append({'key': k, 'value': v})
        self.writeToSettings(result)

    def writeToSettings(self,result):
        with open(self.dotfiles + '.settings/settings.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)

    def searchInFile(self, f, search):
        with open(self.dotfiles + f, 'r') as file:
            content = file.read()
            if search in content:
                return True
            else:
                return False

    # Replace Text in File
    def replaceInFile(self, f, search, replace):
        file = open(self.dotfiles + f, 'r')
        lines = file.readlines()
        count = 0
        found = 0
        # Strips the newline character
        for l in lines:
            count += 1
            if search in l:
                found = count
                print("Found in " + str(found))
        if found > 0:
            lines[found - 1] = replace + "\n"
            with open(self.dotfiles + f, 'w') as file:
                file.writelines(lines)

    # Reload Waybar
    def reloadWaybar(self):
        launch_script = self.dotfiles + "waybar/launch.sh"
        subprocess.Popen(["setsid", launch_script, "1>/dev/null" ,"2>&1" "&"])

    # Add Application actions
    def create_action(self, name, callback, shortcuts=None):
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)

    def changeTheme(self,win):
        app = win.get_application()
        sm = app.get_style_manager()
        sm.set_color_scheme(Adw.ColorScheme.PREFER_DARK)

# Application Start
app = MyApp()
sm = app.get_style_manager()
sm.set_color_scheme(Adw.ColorScheme.PREFER_DARK)
app.run(sys.argv)