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

action_dir = join_paths('hicolor', 'scalable', 'actions')
action_icons = [
    # each icon must be registered here
    join_paths(action_dir, 'star-filled-symbolic.svg'),
    join_paths(action_dir, 'xapp-favorite-symbolic.svg'),
    join_paths(action_dir, 'xapp-unfavorite-symbolic.svg')
]

install_data(
  action_icons,
  install_dir: join_paths(get_option('datadir'), 'icons', action_dir)
)
