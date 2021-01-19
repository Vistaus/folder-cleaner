project(
	'folder-cleaner',
	version: '1.1',
	meson_version: '>= 0.50.0',
)

appname = 'com.github.Latesil.folder-cleaner'

i18n  = import('i18n')

subdir('data')
subdir('foldercleaner')
subdir('po')
# subdir('nautilus-script')

meson.add_install_script('build-aux/meson/postinstall.py')
