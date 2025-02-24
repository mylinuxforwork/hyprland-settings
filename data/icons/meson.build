application_id = 'com.ml4w.hyprlandsettings'

scalable_dir = 'hicolor' / 'scalable' / 'apps'
install_data(
  scalable_dir / ('@0@.png').format(application_id),
  install_dir: get_option('datadir') / 'icons' / scalable_dir
)

symbolic_dir = 'hicolor' / 'symbolic' / 'apps'
install_data(
  symbolic_dir / ('@0@-symbolic.png').format(application_id),
  install_dir: get_option('datadir') / 'icons' / symbolic_dir
)
