#  _   _                  _                 _ 
# | | | |_   _ _ __  _ __| | __ _ _ __   __| |
# | |_| | | | | '_ \| '__| |/ _` | '_ \ / _` |
# |  _  | |_| | |_) | |  | | (_| | | | | (_| |
# |_| |_|\__, | .__/|_|  |_|\__,_|_| |_|\__,_|
#        |___/|_|                             
#
                                                            
import sys
import gi
import subprocess
import os
import threading
import json
import pathlib
import shutil
import time

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, Gio, Gdk
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
    settings_page = Gtk.Template.Child()
    options_page = Gtk.Template.Child()
    keywords_group = Gtk.Template.Child()

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
    configFolderName = "ml4w-hyprland-settings" # config folder name
    configFolder = homeFolder + "/.config/" + configFolderName # Config folder name
    settingsFolder = "" # Settingsfolder
    hyprctlFile = "" # hyprctl.conf
    hyprctl = {} # hyprctl dictionary synced with hyprctlfile
    rowtype = {} # rowtype dictionary for keywords
    pref_rows = {} # Dictionary for pref row objects
    action_rows = {} # Dictionary for action row objects
    keyword_blocked = False # Temp Status of removing a keyword

    def __init__(self, **kwargs):
        super().__init__(application_id='com.ml4w.hyprlandsettings',
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS)
        self.create_action('quit', lambda *_: self.quit(), ['<primary>q'])
        self.create_action('about', self.on_about)

    def do_activate(self):
        # Setup Configuration      
        self.runSetup()

        # Define main window
        win = self.props.active_window
        if not win:
            win = MainWindow(application=self)

        # Get pages
        self.settings_page = win.settings_page
        self.options_page = win.options_page

        # get groups
        self.keywords_group = win.keywords_group

        # Initialization
        self.initUI()

        # load hyprctl.sh on startup
        self.init_hyprctl = True

        if (self.init_hyprctl):
            value = "true"
            print(":: Execute: " + self.settingsFolder + "hyprctl.sh")
            subprocess.Popen(self.settingsFolder + "/hyprctl.sh")

        # Show Application Window
        win.present()
        print (":: Welcome to ML4W Hyprland Settings App")

    def initUI(self):
        # Load hyprctl.json
        hyprctl_file = open(self.settingsFolder + "/hyprctl.json")
        hyprctl_arr = json.load(hyprctl_file)
        for row in hyprctl_arr:
            self.hyprctl[row["key"]] = row["value"]

        if os.path.exists(self.settingsFolder + "/settings.json"):
            # Load Custom configuration
            config_file = open(self.settingsFolder + '/settings.json')  
            config = json.load(config_file)
            print(":: Using custom settings.json in " + self.settingsFolder)
        else:
            # Load Default configuration
            config_file = open(pathname + '/settings.json')  
            config = json.load(config_file)
            print(":: Using default settings.json in " + pathname)
        

        # Create Groups
        for p in config["groups"]:
            prefGroup = Adw.PreferencesGroup()
            prefGroup.set_title(p["title"])
            prefGroup.name="group_" + p["title"]
            prefGroup.set_description(p["description"])

            # Create Rows
            for i in p["rows"]:

                # Fill rowtype dictionary
                self.rowtype[i["keyword"]] = i["type"]

                # Get row values
                if i["keyword"] not in self.hyprctl:
                    value = self.getKeywordValue(i["keyword"])
                else:
                    if (i["type"] == "SpinRowFloat"):
                        value = self.hyprctl[i["keyword"]]*10
                    else:
                        value = self.hyprctl[i["keyword"]]

                
                # Create rows
                if i["type"] == "SpinRow":
                    self.createSpinRow(prefGroup,i,value)
                elif i["type"] == "SpinRowFloat":
                    self.createSpinFloatRow(prefGroup,i,value)
                elif i["type"] == "SwitchRow":
                    self.createSwitchRow(prefGroup,i,value)        
                elif i["type"] == "ColorRow":
                    self.createColorRow(prefGroup,i,value)        

            self.settings_page.add(prefGroup)
        
        # Create keyword rows
        for keyword in self.hyprctl:
            self.createActionRow(keyword)

    # ActionRow
    def createActionRow(self,keyword):
        actionRow = Adw.ActionRow()
        actionRow.set_title(keyword)
        btn = Gtk.Button()
        btn.set_label("Remove")
        btn.set_valign(3)
        btn.connect("clicked",self.remove_keyword,keyword)
        actionRow.add_suffix(btn)
        self.keywords_group.add(actionRow)
        self.action_rows[keyword] = actionRow
        
    def remove_keyword(self, widget,v):
        subprocess.Popen(["hyprctl", "reload"])
        print(":: Hyprctl Reload")
        # time.sleep(1)
        self.removeHyptctl(v)
        self.keywords_group.remove(self.action_rows[v])
        self.action_rows.pop(v)
        self.keyword_blocked = True
        value = self.getKeywordValue(v)
        if self.rowtype[v] == "SpinRow":
            self.pref_rows[v].set_value(int(value))        
        if self.rowtype[v] == "SpinRowFloat":
            self.pref_rows[v].set_value(int(value)*10)        
        if self.rowtype[v] == "SwitchRow":
            self.pref_rows[v].set_active(value)
        if self.rowtype[v] == "ColorRow":
            color_rgba = Gdk.RGBA()
            if "rgb" in value:
                color_rgba.parse("#" + value.split("(")[1].split(")")[0])
            else:
                color_rgba.parse("#" + value[2:])
            self.pref_rows[v].set_rgba(color_rgba)
        
        print(":: Execute: " + self.settingsFolder + "/hyprctl.sh")
        subprocess.Popen(self.settingsFolder + "/hyprctl.sh")

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
        self.pref_rows[row["keyword"]] = spinRow

    def on_spin_change(self,adjust,*data):
        if not self.keyword_blocked:
            subprocess.Popen(["hyprctl", "keyword", data[1]["keyword"], str(int(adjust.get_value()))])
            if data[1]["keyword"] not in self.hyprctl:
                self.createActionRow(data[1]["keyword"])
            self.updateHyprctl(data[1]["keyword"],int(adjust.get_value()))
        self.keyword_blocked = False            

    # SpinRowFloat
    def createSpinFloatRow(self,pref,row,value):
        spinRow = Adw.SpinRow()
        spinRow.set_title(row["title"])
        spinRow.set_subtitle(row["subtitle"])
        adjust = Gtk.Adjustment()
        adjust.set_lower(row["lower"])
        adjust.set_upper(row["upper"])
        adjust.set_value(int(value))
        adjust.set_step_increment(row["step"])
        spinRow.set_adjustment(adjust)
        adjust.connect("value-changed", self.on_spinfloat_change, adjust, row)
        pref.add(spinRow)
        self.pref_rows[row["keyword"]] = spinRow

    def on_spinfloat_change(self,adjust,*data):
        if not self.keyword_blocked:
            value = adjust.get_value()/10
            subprocess.Popen(["hyprctl", "keyword", data[1]["keyword"], str(value)])
            if data[1]["keyword"] not in self.hyprctl:
                self.createActionRow(data[1]["keyword"])
            self.updateHyprctl(data[1]["keyword"],value)
        self.keyword_blocked = False            

    #SwitchRow
    def createSwitchRow(self,pref,row,value):
        switchRow = Adw.SwitchRow()
        switchRow.set_title(row["title"])
        switchRow.set_subtitle(row["subtitle"])
        switchRow.set_active(value)
        switchRow.connect("notify::active", self.on_switch_change, row)
        pref.add(switchRow)
        self.pref_rows[row["keyword"]] = switchRow

    def on_switch_change(self,widget,*data):
        if not self.keyword_blocked:
            if (widget.get_active()):
                value = "true"
            else:
                value = "false"
            subprocess.Popen(["hyprctl", "keyword", data[1]["keyword"], value])
            if data[1]["keyword"] not in self.hyprctl:
                self.createActionRow(data[1]["keyword"])
            self.updateHyprctl(data[1]["keyword"],widget.get_active())
        self.keyword_blocked = False            

    #ColorRow
    def createColorRow(self,pref,row,value):
        colorRow = Adw.ActionRow()
        colorRow.set_title(row["title"])
        colorRow.set_subtitle(row["subtitle"])
        color = Gtk.ColorDialogButton()
        color.set_valign(3)

        color_rgba = Gdk.RGBA()
        if "rgb" in value:
            color_rgba.parse("#" + value.split("(")[1].split(")")[0])
        else:
            color_rgba.parse("#" + value[2:])

        color.set_rgba(color_rgba)
        color_dialog = Gtk.ColorDialog()
        color.connect("notify::rgba",self.on_color_select, row)
        color.set_dialog(color_dialog)
        colorRow.add_suffix(color)

        pref.add(colorRow)
        self.pref_rows[row["keyword"]] = color

    def rgb_to_hex(self, rgb):
        r = int(rgb[0])
        g = int(rgb[1])
        b = int(rgb[2])
        return f'{r:02x}{g:02x}{b:02x}'        

    def rgba_to_hex(self, rgba):
        r = int(rgba[0])
        g = int(rgba[1])
        b = int(rgba[2])
        a = int(float(rgba[3]) * 255)
        # return f'{r:02x}{g:02x}{b:02x}{a:02x}'        
        return f'{r:02x}{g:02x}{b:02x}'        

    def on_color_select(self,widget,*data):
        if not self.keyword_blocked:
            rgbaStr = widget.get_rgba().to_string()

            if "rgba" in rgbaStr:
                rgbaStr = rgbaStr.replace("rgba(", "")
                rgbaStr = rgbaStr.replace(")", "")
                rgba_hex = "rgb(" + self.rgba_to_hex(rgbaStr.split(",")) + ")"
            else:
                rgbaStr = rgbaStr.replace("rgb(", "")
                rgbaStr = rgbaStr.replace(")", "")
                rgba_hex = "rgb(" + self.rgb_to_hex(rgbaStr.split(",")) + ")"
            
            if data[1]["keyword"] not in self.hyprctl:
                self.createActionRow(data[1]["keyword"])
            self.updateHyprctl(data[1]["keyword"],rgba_hex)
            subprocess.Popen(["hyprctl", "keyword", data[1]["keyword"], rgba_hex])
        self.keyword_blocked = False

    # Update and write hyprctl.json
    def removeHyptctl(self,keyword):
        result = []
        del_key = ""
        for k, v in self.hyprctl.items():
            if k != keyword:
                result.append({'key': k, 'value': v})
            else:
                del_key = k
        self.hyprctl.pop(del_key)
        self.writeToHyprctl(result)

    def updateHyprctl(self,keyword,value):
        result = []
        self.hyprctl[keyword] = value
        for k, v in self.hyprctl.items():
            result.append({'key': k, 'value': v})
        self.writeToHyprctl(result)

    def writeToHyprctl(self,result):
        with open(self.settingsFolder + '/hyprctl.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)

    # Get current keyword value
    def getKeywordValue(self,keyword):
        result = subprocess.run("hyprctl getoption " + keyword, shell=True, capture_output=True, text=True)
        outcome = result.stdout
        out_arr = outcome.split("\n")
        value = outcome.split("\n")[0]
        if "int" in value:
            int_val = value.split("int: ")[1]
        if "float" in value:
            float_val = value.split("float: ")[1]
        if "custom type" in value:
            custom_val = value.split("custom type: ")[1]
            int_val = custom_val.split(" ")[0]
        if (self.rowtype[keyword] == "SpinRowFloat"):
            value = int(float(float_val)*10)
        elif (self.rowtype[keyword] == "ColorRow"):
            colorhex = custom_val.split(" ")[0]
            value = colorhex
        elif (self.rowtype[keyword] == "SwitchRow"):
            if int_val == "1":
                value = True
            else:
                value = False
        else:
            value = int(int_val)
        return value

    # File setup
    def runSetup(self):
        # Create ml4w-hyprland-settings in .config folder
        pathlib.Path(self.configFolder).mkdir(parents=True, exist_ok=True) 
        self.settingsFolder = self.configFolder
        print(":: Using configuration in: " + self.settingsFolder)

        #Update hyprctl.sh in settingsFolder        
        shutil.copy(self.path_name + '/hyprctl.sh', self.settingsFolder)
        print(":: hyprctl.sh updated in " + self.settingsFolder)

        # Create empty hyprctl.json if not exists
        if not os.path.exists(self.settingsFolder + '/hyprctl.json'):
            shutil.copy(self.path_name + '/hyprctl.json', self.settingsFolder)
            print(":: hyprctl.json created in " + self.settingsFolder)

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

    def on_about(self, widget, _):
        
        dialog = Adw.AboutWindow(
            application_icon="application-x-executable",
            application_name="ML4W Hyprland Settings App",
            developer_name="Stephan Raabe",
            version="1.0",
            website="https://gitlab.com/stephan-raabe/ml4w-hyprland-settings",
            issue_url="https://gitlab.com/stephan-raabe/ml4w-hyprland-settings/-/issues",
            support_url="https://gitlab.com/stephan-raabe/ml4w-hyprland-settings/-/issues",
            copyright="© 2024 Stephan Raabe",
            license_type=Gtk.License.GPL_3_0_ONLY
        )
        dialog.present()

# Application Start
app = MyApp()
sm = app.get_style_manager()
sm.set_color_scheme(Adw.ColorScheme.PREFER_DARK)
app.run(sys.argv)