project(
	'folder-cleaner',
	version: '1.2',
	meson_version: '>= 0.50.0',
)

message('Looking for dependencies')
dependency('glib-2.0')
dependency('gobject-introspection-1.0', version: '>=1.35.9')
dependency('gtk+-3.0', version: '>=3.24.1')
dependency('libhandy-1', version: '>=1.0.0')


appname = 'com.github.Latesil.folder-cleaner'

i18n  = import('i18n')

subdir('data')
subdir('foldercleaner')
subdir('po')
# subdir('nautilus-script')

meson.add_install_script('build-aux/meson/postinstall.py')
