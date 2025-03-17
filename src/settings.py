from gi.repository import Adw
from gi.repository import Gtk

@Gtk.Template(resource_path='/com/ml4w/hyprlandsettings/settings.ui')
class HyprlandKeywordsSettings(Adw.PreferencesDialog):
    __gtype_name__ = 'HyprlandKeywordsSettings'

    keywords_group = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
