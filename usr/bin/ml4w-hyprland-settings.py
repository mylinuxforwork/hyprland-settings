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
    preference_page = Gtk.Template.Child()

    # Get objects from template
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

# -----------------------------------------
# Main App
# -----------------------------------------
class MyApp(Adw.Application):

    # Path to home folder
    win = Adw.ApplicationWindow()
    hyprctl = {}

    def __init__(self, **kwargs):
        super().__init__(application_id='com.ml4w.welcome',
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS)
        self.create_action('quit', lambda *_: self.quit(), ['<primary>q'])

    # Activation
    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = MainWindow(application=self)

        # Setup Configuration      

        # get preference page
        self.preference_page = win.preference_page

        # Load data from hyprctl
        
        hyprctl_file = open(pathname + '/hyprctl.json')
        self.hyprctl = json.load(hyprctl_file)

        # Load Default configuration
        config_file = open(pathname + '/settings.json')  
        config = json.load(config_file)

        # Create Groups
        for p in config["groups"]:
            prefGroup = Adw.PreferencesGroup()
            prefGroup.set_title(p["title"])
            prefGroup.set_description(p["description"])

            # Create Rows
            for i in p["rows"]:
                if i["keyword"] not in self.hyprctl:
                    value = i["default"]
                else:
                    value = self.hyprctl[i["keyword"]]
                if i["type"] == "SpinRow":
                    self.createSpinRow(prefGroup,i,value)
                elif i["type"] == "SwitchRow":
                    self.createSwitchRow(prefGroup,i,value)        

            self.preference_page.add(prefGroup)

        # Show Application Window
        win.present()
        print (":: Welcome to ML4W Settings App")

    # ------------------------------------------------------
    # Row Templates
    # ------------------------------------------------------

    # SpinRow
    def createSpinRow(self,pref,row,value):
        spinRow = Adw.SpinRow()
        spinRow.set_title(row["title"])
        spinRow.set_subtitle(row["subtitle"])
        adjust = Gtk.Adjustment()
        adjust.set_lower(row["lower"])
        adjust.set_upper(row["upper"])
        adjust.set_value(int(value))
        adjust.set_step_increment(row["step"])
        
        spinRow.set_adjustment(adjust)
        adjust.connect("value-changed", self.on_spin_change, adjust, row)
        pref.add(spinRow)

    def on_spin_change(self,adjust,*data):
        subprocess.Popen(["hyprctl", "keyword", data[1]["keyword"], str(int(adjust.get_value()))])
        self.updateHyprctl(data[1]["keyword"],int(adjust.get_value()))

    #SwitchRow
    def createSwitchRow(self,pref,row,value):
        switchRow = Adw.SwitchRow()
        switchRow.set_title(row["title"])
        switchRow.set_subtitle(row["subtitle"])
        switchRow.set_active(int(value))
        switchRow.connect("notify::active", self.on_switch_change, row)
        pref.add(switchRow)

    def on_switch_change(self,widget,*data):
        if widget.get_active():
            value = "1"
        else:
            value = "0"
        subprocess.Popen(["hyprctl", "keyword", data[1]["keyword"], value])
        self.updateHyprctl(data[1]["keyword"],value)

    # ------------------------------------------------------
    # Write hyprctl.sh
    # ------------------------------------------------------

    def updateHyprctl(self,keyword,value):
        self.hyprctl[keyword] = value
        with open(pathname + '/hyprctl.json', 'w', encoding='utf-8') as f:
            json.dump(self.hyprctl, f, ensure_ascii=False, indent=4)

    # ------------------------------------------------------
    # About Window
    # ------------------------------------------------------

    def on_about(self, widget, _):
        
        dialog = Adw.AboutWindow(
            application_icon="application-x-executable",
            application_name="ML4W Settings",
            developer_name="Stephan Raabe",
            version="1.0.0",
            website="https://gitlab.com/stephan-raabe/dotfiles",
            issue_url="https://gitlab.com/stephan-raabe/dotfiles/-/issues",
            support_url="https://gitlab.com/stephan-raabe/dotfiles/-/issues",
            copyright="© 2024 Stephan Raabe",
            license_type=Gtk.License.GPL_3_0_ONLY
        )
        dialog.present()

    # ------------------------------------------------------
    # Helper Functions
    # ------------------------------------------------------

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

# -----------------------------------------
# Application Start
# -----------------------------------------
app = MyApp()
sm = app.get_style_manager()
sm.set_color_scheme(Adw.ColorScheme.PREFER_DARK)
app.run(sys.argv)