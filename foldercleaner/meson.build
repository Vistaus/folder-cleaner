pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'foldercleaner')
gnome = import('gnome')

gnome.compile_resources(meson.project_name(),
	meson.project_name() + '.gresource.xml',
	gresource_bundle: true,
	install: true,
	install_dir: pkgdatadir,
)

python3 = import('python3')

conf = configuration_data()
conf.set('PYTHON', python3.find_python().path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', join_paths(get_option('prefix'), get_option('localedir')))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: meson.project_name() + '.in',
  output: meson.project_name(),
  configuration: conf,
  install: true,
  install_dir: get_option('bindir')
)

folder_cleaner_sources = [
	'__init__.py',
	'constants.py',
	'window.py',
	'preferences.py',
	'aboutdialog.py',
	'basic_formats.py',
	'user_folder.py',
	'sorting.py',
    'helpers.py',
    'folder_box.py',
	'main.py',
]

install_data(folder_cleaner_sources, install_dir: moduledir)
