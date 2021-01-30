%global uuid    com.github.Latesil.%{name}

Name:           folder-cleaner
Version:        1.2
Release:        1%{?dist}
Summary:        Simple programm for sorting files in selected folder, or remove them

License:        GPLv3+
URL:            https://gitlab.com/Latesil/folder-cleaner
Source0:        %{url}/-/archive/v%{version}/%{name}-v%{version}.tar.gz
BuildArch:      noarch

BuildRequires:  desktop-file-utils
BuildRequires:  intltool
BuildRequires:  libappstream-glib
BuildRequires:  meson
BuildRequires:  python3-devel
BuildRequires:  pkgconfig(gtk+-3.0)
Requires:       hicolor-icon-theme

%description
%{summary}.


%prep
%autosetup -n %{name}-v%{version} -p1


%build
%meson
%meson_build


%install
%meson_install
%find_lang %{uuid}


%check
appstream-util validate-relax --nonet %{buildroot}%{_metainfodir}/*.xml
desktop-file-validate %{buildroot}%{_datadir}/applications/*.desktop


%files -f %{uuid}.lang
%license LICENSE
%doc README.md
%{_bindir}/%{name}
%{_datadir}/%{name}/
%{_datadir}/applications/*.desktop
%{_datadir}/glib-2.0/schemas/*.gschema.xml
%{_datadir}/icons/hicolor/*/*/*.png
%{_datadir}/icons/hicolor/symbolic/*/*.svg
%{_metainfodir}/*.xml


%changelog
* Sat Jan 30 2020 Latesil <vihilantes@gmail.com> - 1.2-1
- Update to 1.2

* Sat Jan 23 2020 Latesil <vihilantes@gmail.com> - 1.1.1-1
- Update to 1.1.1

* Tue Jan 19 2020 Latesil <vihilantes@gmail.com> - 1.1-1
- Update to 1.1

* Mon May 11 2020 Latesil <vihilantes@gmail.com> - 1.0.2-1
- Update to 1.0.2

* Thu Feb 20 2020 Latesil <vihilantes@gmail.com> - 1.0.1-1
- Update to 1.0.1

* Thu Feb 20 2020 Artem Polishchuk <ego.cordatus@gmail.com> - 1.0.0-1
- Initial package
