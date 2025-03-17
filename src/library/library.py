import gi
import subprocess
import json
import os
import pathlib
import shutil

from gi.repository import Gtk, Adw, Gio, Gdk

# Paths
path_name = str(pathlib.Path(__file__).resolve().parent.parent)
homeFolder = os.path.expanduser('~') # Path to home folder
configFolderName = "com.ml4w.hyprlandsettings" # config folder name
configFolder = homeFolder + "/.config/" + configFolderName # Config folder name

# Library of helper functions
class Library:

    # Execute hyprctl.sh
    def executeHyprCtl(self):
        print(":: Execute: " + configFolder + "/hyprctl.sh")
        subprocess.Popen(["flatpak-spawn", "--host", configFolder + "/hyprctl.sh"])

    # Load content from hyprctl.json
    def loadHyprctlJson(self):
        hyprctl_json = open(configFolder + "/hyprctl.json")
        return hyprctl_json

    def writeHyprctlJson(self,result):
        with open(configFolder + '/hyprctl.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)

    # Generates Hyprctl Dictionary
    def getHyprctlDictionary(self):
        hyprctl_json = self.loadHyprctlJson()

        # Transform to array
        hyprctl_arr = json.load(hyprctl_json)

        # Convert to dictionary
        hyprctl_dict = {}
        for row in hyprctl_arr:
            hyprctl_dict[row["key"]] = row["value"]

        return hyprctl_dict

    # Load hyprctl descriptions
    def loadHyprctlDescriptions(self):
        result = subprocess.Popen(["flatpak-spawn", "--host", "hyprctl", "descriptions"], stdout=subprocess.PIPE, text=True)
        outcome = result.communicate()[0]
        outcome = outcome.replace("{{", "[{")
        outcome = outcome.replace("}}", "}]")
        outcome = outcome.replace('next,cursor','"next,cursor"')
        outcome = outcome.replace(': disabled,enabled,only when dragging into the groupbar',': "disabled,enabled,only when dragging into the groupbar"')
        outcome = outcome.replace(': Disabled,Enabled,Auto',': "Disabled,Enabled,Auto"')
        outcome = outcome.replace(': Disabled,Enabled,Force',': "Disabled,Enabled,Force"')
        outcome = outcome.replace(': follow mouse,left or top,right or bottom',': "follow mouse,left or top,right or bottom"')
        outcome = outcome.replace(': positional,current,opening',': "positional,current,opening"')
        outcome = outcome.replace('supports css style gaps (top, right, bottom, left -> 5 10 15 20)",','')
        outcome = outcome.replace(': "gaps between windows and monitor edges', ': "TEMP css style gaps (top, right, bottom, left -> 5 10 15 20)",')
        outcome = outcome.replace(': "gaps between windows', ': "gaps between windows supports css style gaps (top, right, bottom, left -> 5 10 15 20)",')
        outcome = outcome.replace('TEMP', 'gaps between windows')
        outcome = outcome.replace('	','')

        # Create a temporary file from the output
        file=open(configFolder + "/hyprctl_description.json","w+")
        file.write(str(outcome))
        file.close()

        return outcome

    # Generates json from hyprctl descriptions
    def getHyprctlDescriptions(self):

        # Generate hyprctl_description.json
        # outcome = self.loadHyprctlDescriptions()

        # Load from shipped json
        with open(path_name + '/json/hyprctl_description.json') as f:
            config_json = json.load(f)

        return config_json

    # Converts rgb to hey
    def rgb_to_hex(self, rgb):
        r = int(rgb[0])
        g = int(rgb[1])
        b = int(rgb[2])
        return f'ff{r:02x}{g:02x}{b:02x}'

    # Converts rgba to hex
    def rgba_to_hex(self, rgba):
        r = int(rgba[0])
        g = int(rgba[1])
        b = int(rgba[2])
        a = int(float(rgba[3]) * 255)
        return f'{a:02x}{r:02x}{g:02x}{b:02x}'

    # Run application setup
    def runSetup(self):
        # Create ml4w-hyprland-settings in .config folder
        pathlib.Path(configFolder).mkdir(parents=True, exist_ok=True)
        print(":: Using configuration in: " + configFolder)

        #Update hyprctl.sh in settingsFolder
        shutil.copy(path_name + '/scripts/hyprctl.sh', configFolder)
        print(":: hyprctl.sh updated in " + configFolder)

        # Create empty hyprctl.json if not exists
        if not os.path.exists(configFolder + '/hyprctl.json'):
            shutil.copy(path_name + '/json/hyprctl.json', configFolder)
            print(":: hyprctl.json created in " + configFolder)

    # Run hyprctl command with keyword and value
    def runHyprctl(self,keyword, value):
        print(":: Execute hyprctl keyword " + keyword + " " + str(value))
        subprocess.Popen(["flatpak-spawn", "--host", "hyprctl", "keyword", keyword, str(value)])

    def reloadHyprctl(self):
        print(":: hyprctl reload")
        subprocess.Popen(["flatpak-spawn", "--host", "hyprctl", "reload"])

    # Get current value of keyword
    def loadKeywordValue(self,keyword):
        result = subprocess.Popen(["flatpak-spawn", "--host", "hyprctl", "getoption", keyword], stdout=subprocess.PIPE, text=True)
        outcome = result.communicate()[0]
        out_arr = outcome.split("\n")
        value = outcome.split("\n")[0]
        return value

    # Create a Switch Row for boolean values
    def createSwitchRow(self,title,description,value):
        switchRow = Adw.SwitchRow()
        switchRow.set_title(title)
        switchRow.set_subtitle(description)
        switchRow.set_active(value)
        return switchRow

    # Create SpinRow
    def createSpinRow(self,title,description,value,digits):
        spinRow = Adw.SpinRow()
        spinRow.set_title(title)
        spinRow.set_digits(digits)
        spinRow.set_subtitle(description)
        return spinRow

    # Create Adjustment for SpinRow
    def createAdjust(self,lower,upper,step,value):
        adjust = Gtk.Adjustment()
        adjust.set_lower(lower)
        adjust.set_upper(upper)
        adjust.set_value(value)
        adjust.set_step_increment(step)
        return adjust

    # Create Adjustment for SpinRow
    def createFloatAdjust(self,lower,upper,step,value):
        adjust = Gtk.Adjustment()
        adjust.set_lower(lower)
        adjust.set_upper(upper)
        adjust.set_value(value)
        adjust.set_step_increment(step)
        return adjust

    def createActionRow(self,title,description,value):
        actionRow = Adw.ActionRow()
        actionRow.set_title(title)
        actionRow.set_subtitle(description)
        return actionRow

    # Get current keyword value
    def getKeywordValue(self,keyword,rowtype):
        value = self.loadKeywordValue(keyword)

        # Check if option exists
        if value != "no such option":
            if "int" in value:
                custom_val = value.split("int: ")[1]
            elif "float" in value:
                custom_val = value.split("float: ")[1]
            elif "custom type" in value:
                if "col" in keyword:
                    custom_val = value.split("custom type: ")[1]
                    custom_val = "0x" + custom_val.split(" ")[0]
                else:
                    custom_val = value.split("custom type: ")[1]
                    custom_val = custom_val.split(" ")[0]

            if rowtype[keyword] == 0:
                if custom_val == "1":
                    value = True
                else:
                    value = False

            if rowtype[keyword] == 1:
                if "int" in value:
                    value = custom_val
                else:
                    value = "no such option"

            if rowtype[keyword] == 7:
                value = custom_val

            if rowtype[keyword] == 2:
                if "float" in value:
                    value = float(custom_val)
                else:
                    value = "no such option"

        return value
