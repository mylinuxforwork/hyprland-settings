# main.py
#
# Copyright 2025 Unknown
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import sys
import gi
import subprocess
import os
import threading
import json
import pathlib
import shutil
import time
from multiprocessing import Process

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, Gio, Gdk
from gi.repository import GLib
from gi.repository import GObject
from subprocess import Popen, PIPE
from .window import HyprlandSettingsWindow
from .settings import HyprlandKeywordsSettings
from .library.library import Library

lib = Library()

# The main application singleton class.
class HyprlandSettingsApplication(Adw.Application):

    hyprctl = {} # hyprctl dictionary synced with hyprctlfile
    rowtype = {} # rowtype dictionary for keywords
    action_rows = {} # Dictionary for action row objects
    pref_rows = {} # Dictionary for variables + value

    # List Stores
    hyprvariablestore = Gio.ListStore()

    # Supported Types
    supported_types = [0,1,2,7]

    keyword_blocked = False # Temp Status of removing a keyword
    def __init__(self):
        super().__init__(application_id='com.ml4w.hyprlandsettings',
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS)
        self.create_action('quit', lambda *_: self.quit(), ['<primary>q'])
        self.create_action('about', self.on_about_action)
        self.create_action('settings', self.on_settings_action)

        self.create_action('hyprland_wiki', self.on_hyprland_wiki)
        self.create_action('hyprland_variables', self.on_hyprland_variables)
        self.create_action('help', self.on_help)
        self.create_action('report_issue', self.on_report_issue)
        self.create_action('check_updates', self.on_check_updates)

        # Setup Configuration
        lib.runSetup()

        # Execute Hyprctl
        lib.executeHyprCtl()

    # Called when the application is activated.
    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = HyprlandSettingsWindow(application=self)
        self.win_settings = HyprlandKeywordsSettings()
        # self.props.active_window.hyprvariables_set_list.bind_model(self.hyprvariablestore,self.create_hyprvariable_row)

        # Show main window
        win.present()

        # Get pages
        self.options_group = self.win_settings.keywords_group

        # get groups
        self.keywords_group = win.keywords_group

        # novariables
        self.novariables = win.novariables

        thread = threading.Thread(target=self.initUI)
        thread.daemon = True
        thread.start()


    # Open Settings Window
    def on_settings_action(self, *args):
        self.win_settings.present(self.props.active_window)
        self.win_settings.set_search_enabled(True)

    def check_novariables(self):
        if len(self.hyprctl) > 0:
            self.keywords_group.set_visible(True)
            self.novariables.set_visible(False)
        else:
            self.keywords_group.set_visible(False)
            self.novariables.set_visible(True)

    # Initialization of the UI
    def initUI(self):

        # Get hyprctl dictionary from hyprctl.json
        self.hyprctl = lib.getHyprctlDictionary()
        self.check_novariables()

        # Load hyprctl descriptions
        config_json = lib.getHyprctlDescriptions()

        # Create Rows
        counter = 0
        for i in config_json:
            if i["type"] in self.supported_types:

                # print(i["value"] + ": " + str(i["type"]))

                # Fill rowtype dictionary
                self.rowtype[i["value"]] = i["type"]

                # Get row values
                if i["value"] not in self.hyprctl:
                    value = lib.getKeywordValue(i["value"],self.rowtype)
                else:
                    value = self.hyprctl[i["value"]]
                    # print("Set " + i["value"] + ": " + value)

                # Fill with all keywords and values
                self.pref_rows[i["value"]] = value

                # Check for invalid option
                if value != "no such option":
                    counter = counter + 1
                    match i["type"]:
                        case 0:
                            self.createSwitchRow(i,value)
                        case 1:
                            self.createSpinRow(i,value)
                        case 2:
                            self.createSpinRow(i,value)
                        case 7:
                            self.createColorRow(i,value)

    # Toggle keyword between options and keywords group
    def toggle_keyword(self,widget,row,btn,keyword,rtype):

        if rtype == 0:
            value = "1" if (row.get_active()) else "0"
        elif rtype == 7:
            value = self.pref_rows[keyword]
        else:
            value = round(row.get_value(), 2)

        if btn.get_label() == "Add":
            # Add keyword to hyprctl.json
            self.updateHyprctl(keyword,self.pref_rows[keyword])
            self.options_group.remove(row)
            self.keywords_group.add(row)
            btn.set_label("Remove")
        else:
            # Remove keyword from hyprctl.json
            self.removeHyptctl(keyword)
            btn.set_label("Add")
            self.keywords_group.remove(row)
            self.options_group.add(row)
            lib.reloadHyprctl()

        self.check_novariables()

    # -------------------------------------------------------
    # SpinRow
    # -------------------------------------------------------
    def createSpinRow(self,row,value):
        keyword = row["value"]

        # Check value type
        if row["type"] == 1:
            climb_rate = 1
            digits = 0
            value = int(value)
        else:
            climb_rate = 0.1
            digits = 2

        # Create Spin Row
        spinRow = lib.createSpinRow(keyword,row["description"],value,digits)
        adjust = lib.createAdjust(row["data"]["min"],row["data"]["max"],climb_rate,value)
        spinRow.set_adjustment(adjust)
        adjust.connect("value-changed", self.on_spin_changed, keyword, row)
        btn = Gtk.Button()
        btn.set_valign(3)
        btn.connect("clicked",self.toggle_keyword,spinRow,btn,keyword,row["type"])
        spinRow.add_prefix(btn)

        # Add Button
        if row["value"] not in self.hyprctl:
            btn.set_icon_name("xapp-favorite-symbolic")
            btn.set_label("Add")
            self.options_group.add(spinRow)
        else:
            btn.set_icon_name("xapp-unfavorite-symbolic")
            btn.set_label("Remove")
            self.keywords_group.add(spinRow)

    def on_spin_changed(self,widget,keyword,row):
        if not self.keyword_blocked:

            # Convert value format
            if row["type"] == 1:
                value = int(widget.get_value())
            else:
                value = round(widget.get_value(), 2)

            if keyword in self.hyprctl:

                # Update hyprctl.json
                self.updateHyprctl(keyword,value)

            self.pref_rows[keyword] = value

            # Run hyprctl with new value
            lib.runHyprctl(keyword,value)

        self.keyword_blocked = False

    # -------------------------------------------------------
    # SwitchRow
    # -------------------------------------------------------
    def createSwitchRow(self,row,value):

        keyword = row["value"]
        value = True if (value == "true") else False
        switchRow = lib.createSwitchRow(keyword,row["description"],value)
        switchRow.connect("notify::active", self.on_switch_change, row)

        btn = Gtk.Button()
        btn.set_valign(3)
        btn.connect("clicked",self.toggle_keyword,switchRow,btn,keyword,row["type"])
        switchRow.add_prefix(btn)

        # Add Button
        if row["value"] not in self.hyprctl:
            btn.set_icon_name("xapp-favorite-symbolic")
            btn.set_label("Add")
            self.options_group.add(switchRow)
        else:
            btn.set_icon_name("xapp-unfavorite-symbolic")
            btn.set_label("Remove")
            self.keywords_group.add(switchRow)


    def on_switch_change(self,widget,*data):

        if not self.keyword_blocked:

            # Run hyprctl with new value
            value = "true" if (widget.get_active()) else "false"
            if data[1]["value"] in self.hyprctl:
                self.updateHyprctl(data[1]["value"],value)

            self.pref_rows[data[1]["value"]] = value
            lib.runHyprctl(data[1]["value"],value)

        self.keyword_blocked = False

    # -------------------------------------------------------
    # ColorRow
    # -------------------------------------------------------
    def createColorRow(self,row,value):

        keyword = row["value"]
        colorRow = lib.createActionRow(keyword,row["description"],value)

        btn = Gtk.Button()
        btn.set_valign(3)
        btn.connect("clicked",self.toggle_keyword,colorRow,btn,keyword,row["type"])

        # Add Button
        if keyword not in self.hyprctl:
            btn.set_icon_name("xapp-favorite-symbolic")
            btn.set_label("Add")
            self.options_group.add(colorRow)
        else:
            btn.set_icon_name("xapp-unfavorite-symbolic")
            btn.set_label("Remove")
            self.keywords_group.add(colorRow)

        color_value = value[2:]
        color_value = color_value[2:] + color_value[:2]
        color = Gtk.ColorDialogButton()
        colorRow.add_prefix(btn)
        color.set_valign(3)

        color_rgba = Gdk.RGBA()
        color_rgba.parse("#" + color_value)
        color.set_rgba(color_rgba)

        color_dialog = Gtk.ColorDialog()
        color.connect("notify::rgba",self.on_color_select,keyword,row)
        color.set_dialog(color_dialog)

        colorRow.add_suffix(color)

    def on_color_select(self,widget,*data):
        if not self.keyword_blocked:
            rgbaStr = widget.get_rgba().to_string()
            if "rgba" in rgbaStr:
                rgbaStr = rgbaStr.replace("rgba(", "")
                rgbaStr = rgbaStr.replace(")", "")
                value = "0x" + lib.rgba_to_hex(rgbaStr.split(","))
            else:
                rgbaStr = rgbaStr.replace("rgb(", "")
                rgbaStr = rgbaStr.replace(")", "")
                value = "0x" + lib.rgb_to_hex(rgbaStr.split(","))

            if data[1] in self.hyprctl:
                self.updateHyprctl(data[1],value)
            self.pref_rows[data[1]] = value

            lib.runHyprctl(data[1],value)

        self.keyword_blocked = False

    # Remove from hyprctl.json
    def removeHyptctl(self,keyword):
        result = []
        del_key = ""
        for k, v in self.hyprctl.items():
            if k != keyword:
                result.append({'key': k, 'value': v})
            else:
                del_key = k
        self.hyprctl.pop(del_key)
        lib.writeHyprctlJson(result)

    # Update hyprctl.json
    def updateHyprctl(self,keyword,value):
        result = []
        self.hyprctl[keyword] = value
        for k, v in self.hyprctl.items():
            result.append({'key': k, 'value': v})
        lib.writeHyprctlJson(result)

    def on_help(self, widget, _):
        subprocess.Popen(["flatpak-spawn", "--host", "xdg-open", "https://github.com/mylinuxforwork/hyprland-settings/wiki"])

    def on_check_updates(self, widget, _):
        subprocess.Popen(["flatpak-spawn", "--host", "xdg-open", "https://github.com/mylinuxforwork/hyprland-settings/releases/latest"])

    def on_report_issue(self, widget, _):
        subprocess.Popen(["flatpak-spawn", "--host", "xdg-open", "https://github.com/mylinuxforwork/hyprland-settings/issues"])

    def on_hyprland_wiki(self, widget, _):
        subprocess.Popen(["flatpak-spawn", "--host", "xdg-open", "https://wiki.hyprland.org/"])

    def on_hyprland_variables(self, widget, _):
        subprocess.Popen(["flatpak-spawn", "--host", "xdg-open", "https://wiki.hyprland.org/Configuring/Variables/"])

    # Callback for the app.about action.
    def on_about_action(self, *args):
        about = Adw.AboutDialog(
            application_name="ML4W Hyprland Settings App",
            application_icon='com.ml4w.hyprlandsettings',
            developer_name="Stephan Raabe",
            version="2.1",
            website="https://github.com/mylinuxforwork/hyprland-settings",
            issue_url="https://github.com/mylinuxforwork/hyprland-settings/issues",
            support_url="https://github.com/mylinuxforwork/hyprland-settings/issues",
            copyright="© 2025 Stephan Raabe",
            license_type=Gtk.License.GPL_3_0_ONLY
        )
        about.present(self.props.active_window)

    # Add an application action.
    def create_action(self, name, callback, shortcuts=None):
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)

# The application's entry point.
def main(version):
    app = HyprlandSettingsApplication()
    return app.run(sys.argv)
