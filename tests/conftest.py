import os
import sys
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

os.environ['GDK_BACKEND'] = 'x11'
os.environ['GTK_THEME'] = 'Adwaita'
os.environ['GSETTINGS_BACKEND'] = 'memory'

try:
    import gi
    gi.require_version('Gtk', '4.0')
    gi.require_version('Adw', '1')
    from gi.repository import Gtk, Adw, Gio, GLib
    GTK_AVAILABLE = True
except (ImportError, ValueError):
    GTK_AVAILABLE = False
    Gtk = None
    Adw = None
    Gio = None
    GLib = None


@pytest.fixture
def temp_dir():
    temp_directory = tempfile.mkdtemp(prefix="hyprland_settings_test_")
    yield Path(temp_directory)
    shutil.rmtree(temp_directory, ignore_errors=True)


@pytest.fixture
def mock_config_dir(temp_dir, monkeypatch):
    config_dir = temp_dir / ".config" / "hyprland-settings"
    config_dir.mkdir(parents=True, exist_ok=True)
    
    monkeypatch.setenv("HOME", str(temp_dir))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(temp_dir / ".config"))
    
    return config_dir


@pytest.fixture
def sample_hyprctl_json(mock_config_dir):
    sample_data = [
        {"key": "general:border_size", "value": "2"},
        {"key": "general:gaps_in", "value": "5"},
        {"key": "general:gaps_out", "value": "10"},
        {"key": "decoration:rounding", "value": "10"},
        {"key": "decoration:active_opacity", "value": "1.0"},
        {"key": "animations:enabled", "value": "true"}
    ]
    
    json_file = mock_config_dir / "hyprctl.json"
    with open(json_file, 'w') as f:
        json.dump(sample_data, f, indent=2)
    
    return json_file


@pytest.fixture
def sample_hyprctl_descriptions():
    return [
        {
            "value": "general:border_size",
            "description": "Size of window borders",
            "type": 1,
            "data": {"min": 0, "max": 10}
        },
        {
            "value": "general:gaps_in",
            "description": "Gaps between windows",
            "type": 1,
            "data": {"min": 0, "max": 20}
        },
        {
            "value": "animations:enabled",
            "description": "Enable animations",
            "type": 0,
            "data": {}
        },
        {
            "value": "decoration:rounding",
            "description": "Window corner rounding",
            "type": 2,
            "data": {"min": 0, "max": 20}
        },
        {
            "value": "decoration:active_opacity",
            "description": "Active window opacity",
            "type": 3,
            "data": {"min": 0.0, "max": 1.0}
        },
        {
            "value": "general:col.active_border",
            "description": "Active border color",
            "type": 7,
            "data": {}
        }
    ]


@pytest.fixture
def mock_hyprctl_command():
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="OK",
            stderr=""
        )
        yield mock_run


@pytest.fixture
def mock_subprocess():
    with patch('subprocess.Popen') as mock_popen:
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b"OK", b"")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        yield mock_popen


@pytest.fixture
def gtk_app():
    if not GTK_AVAILABLE:
        pytest.skip("GTK not available")
    app = Gtk.Application(
        application_id='com.test.hyprlandsettings',
        flags=Gio.ApplicationFlags.FLAGS_NONE
    )
    yield app


@pytest.fixture
def adw_app():
    if not GTK_AVAILABLE:
        pytest.skip("GTK not available")
    app = Adw.Application(
        application_id='com.test.hyprlandsettings',
        flags=Gio.ApplicationFlags.DEFAULT_FLAGS
    )
    yield app


@pytest.fixture
def mock_library(mock_config_dir, sample_hyprctl_json):
    try:
        from src.library.library import Library
        
        with patch.object(Library, 'runSetup') as mock_setup, \
             patch.object(Library, 'executeHyprCtl') as mock_execute:
            
            lib = Library()
            lib.config_path = str(mock_config_dir)
            lib.hyprctl_json_path = str(sample_hyprctl_json)
            
            mock_setup.return_value = None
            mock_execute.return_value = None
            
            yield lib
    except ImportError:
        pytest.skip("Library module not available")


@pytest.fixture
def mock_settings_window(adw_app):
    try:
        from src.settings import HyprlandKeywordsSettings
        
        with patch.object(HyprlandKeywordsSettings, '__init__', return_value=None):
            settings = HyprlandKeywordsSettings()
            settings.keywords_group = MagicMock()
            yield settings
    except ImportError:
        pytest.skip("Settings module not available")


@pytest.fixture
def mock_main_window(adw_app):
    try:
        from src.window import HyprlandSettingsWindow
        
        with patch.object(HyprlandSettingsWindow, '__init__', return_value=None):
            window = HyprlandSettingsWindow(application=adw_app)
            window.keywords_group = MagicMock()
            window.novariables = MagicMock()
            yield window
    except ImportError:
        pytest.skip("Window module not available")


@pytest.fixture
def mock_threading():
    with patch('threading.Thread') as mock_thread:
        mock_thread_instance = MagicMock()
        mock_thread_instance.start = MagicMock()
        mock_thread_instance.daemon = True
        mock_thread.return_value = mock_thread_instance
        yield mock_thread


@pytest.fixture
def sample_rgb_color():
    return {
        "rgb": "255,128,64",
        "rgba": "255,128,64,0.8",
        "hex": "ff8040",
        "hex_with_alpha": "ccff8040"
    }


@pytest.fixture
def mock_gtk_widgets():
    if not GTK_AVAILABLE:
        pytest.skip("GTK not available")
    widgets = {
        'switch_row': MagicMock(spec=Adw.SwitchRow),
        'spin_row': MagicMock(spec=Adw.SpinRow),
        'action_row': MagicMock(spec=Adw.ActionRow),
        'button': MagicMock(spec=Gtk.Button),
        'adjustment': MagicMock(spec=Gtk.Adjustment),
        'color_button': MagicMock(spec=Gtk.ColorDialogButton),
        'preferences_group': MagicMock(spec=Adw.PreferencesGroup)
    }
    
    widgets['switch_row'].get_active.return_value = True
    widgets['spin_row'].get_value.return_value = 5.0
    widgets['button'].get_label.return_value = "Add"
    
    return widgets


@pytest.fixture(autouse=True)
def reset_singleton():
    if GTK_AVAILABLE and Gio:
        if hasattr(Gio.Application, '_instances'):
            Gio.Application._instances = {}
    yield
    if GTK_AVAILABLE and Gio:
        if hasattr(Gio.Application, '_instances'):
            Gio.Application._instances = {}


@pytest.fixture
def cleanup_gtk():
    yield
    
    if GTK_AVAILABLE and Gtk:
        while Gtk.events_pending():
            Gtk.main_iteration_do(False)