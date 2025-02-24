pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
moduledir = pkgdatadir / 'hyprland_settings'
gnome = import('gnome')

gnome.compile_resources('hyprland-settings',
  'hyprland-settings.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
)

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').full_path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', get_option('prefix') / get_option('localedir'))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'hyprland-settings.in',
  output: 'hyprland-settings',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'r-xr-xr-x'
)

hyprland_settings_sources = [
  '__init__.py',
  'main.py',
  'window.py',
  'hyprctl.sh',
  'settings.json',
  'hyprctl.json'
]

install_data(hyprland_settings_sources, install_dir: moduledir)
