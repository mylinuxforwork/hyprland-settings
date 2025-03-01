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

    keyword_blocked = False # Temp Status of removing a keyword

    def __init__(self):
        super().__init__(application_id='com.ml4w.hyprlandsettings',
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS)
        self.create_action('quit', lambda *_: self.quit(), ['<primary>q'])
        self.create_action('about', self.on_about_action)
        self.create_action('settings', self.on_settings_action)

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
            self.win_settings.set_modal(True)

        # Get pages
        self.options_group = self.win_settings.keywords_group

        # get groups
        self.keywords_group = win.keywords_group

        thread = threading.Thread(target=self.initUI)
        thread.daemon = True
        thread.start()

        # Show main window
        win.present()

    # Open Settings Window
    def on_settings_action(self, *args):
        self.win_settings.present()

    # Initialization of the UI
    def initUI(self):

        # Get hyprctl dictionary from hyprctl.json
        self.hyprctl = lib.getHyprctlDictionary()

        # Load hyprctl descriptions
        config_json = lib.getHyprctlDescriptions()

        # Create Rows
        for i in config_json:

            # Fill rowtype dictionary
            self.rowtype[i["value"]] = i["type"]

            # Get row values
            if i["value"] not in self.hyprctl:
                value = lib.getKeywordValue(i["value"],self.rowtype)
            else:
                if (i["type"] == "SpinRowFloat"):
                    value = self.hyprctl[i["value"]]
                else:
                    value = self.hyprctl[i["value"]]

            # Check for invalid option
            if value != "no such option":

                # Create rows
                if i["type"] == 1:
                    self.createSpinRow(i,value)
                elif i["type"] == 2:
                    self.createSpinRow(i,value)
                elif i["type"] == 0:
                    self.createSwitchRow(i,value)
                elif i["type"] == "ColorRow":
                    self.createColorRow(i,value)

    # Toggle keyword between options and keywords group
    def toggle_keyword(self,widget,row,btn,keyword,rtype):

        if rtype == 0:
            value = "1" if (row.get_active()) else "0"
        else:
            value = round(row.get_value(), 2)

        if btn.get_label() == "Add":

            # Add keyword to hyprctl.json
            self.updateHyprctl(keyword,value)

            self.options_group.remove(row)
            self.keywords_group.add(row)
            btn.set_label("Remove")
        else:

            # Remove keyword from hyprctl.json
            self.removeHyptctl(keyword)

            btn.set_label("Add")
            self.keywords_group.remove(row)
            self.options_group.add(row)

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
            btn.set_label("Add")
            self.options_group.add(spinRow)
        else:
            self.keywords_group.add(spinRow)
            btn.set_label("Remove")

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
            btn.set_label("Add")
            self.options_group.add(switchRow)
        else:
            self.keywords_group.add(switchRow)
            btn.set_label("Remove")

    def on_switch_change(self,widget,*data):

        if not self.keyword_blocked:

            # Run hyprctl with new value
            value = "true" if (widget.get_active()) else "false"
            self.updateHyprctl(data[1]["value"],value)
            lib.runHyprctl(data[1]["value"],value)

        self.keyword_blocked = False

    # -------------------------------------------------------
    # ColorRow
    # -------------------------------------------------------
    def createColorRow(self,row,value):
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

    def on_color_select(self,widget,*data):
        if not self.keyword_blocked:
            rgbaStr = widget.get_rgba().to_string()

            if "rgba" in rgbaStr:
                rgbaStr = rgbaStr.replace("rgba(", "")
                rgbaStr = rgbaStr.replace(")", "")
                rgba_hex = "rgb(" + lib.rgba_to_hex(rgbaStr.split(",")) + ")"
            else:
                rgbaStr = rgbaStr.replace("rgb(", "")
                rgbaStr = rgbaStr.replace(")", "")
                rgba_hex = "rgb(" + lib.rgb_to_hex(rgbaStr.split(",")) + ")"

            if data[1]["keyword"] not in self.hyprctl:
                self.createActionRow(data[1]["keyword"])
            self.updateHyprctl(data[1]["keyword"],rgba_hex)
            lib.runHyprctl(data[1]["keyword"], rgba_hex)
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

    # Callback for the app.about action.
    def on_about_action(self, *args):
        about = Adw.AboutDialog(
            application_name="ML4W Hyprland Settings App",
            developer_name="Stephan Raabe",
            version="1.1",
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
