%define gtk2_version 2.11.3
%define dbus_glib_version 0.70
%define dbus_version 0.90
%define gnome_keyring_version 2.21.92
%define gconf2_version 2.14.0
%define libnotify_version 0.2.1
%define _default_patch_fuzz 999

%define po_package gnome-session-2.0

Summary: GNOME session manager
Name: gnome-session
Version: 2.28.0
Release: 15%{?dist}
URL: http://www.gnome.org
Source0: http://download.gnome.org/sources/gnome-session/2.28/%{name}-%{version}.tar.bz2
# latest upstream translations
# see https://bugzilla.redhat.com/show_bug.cgi?id=553603
Source3: as.po

License: GPLv2+
Group: User Interface/Desktops
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Requires: system-logos
# required to get gconf-sanity-check-2 in the right place
Requires: GConf2-gtk >= %{gconf2_version}
# Needed for gnome-settings-daemon
Requires: control-center

# pull in dbus-x11, see bug 209924
Requires: dbus-x11

# we need an authentication agent in the session
Requires: polkit-gnome
# and we want good defaults
Requires: polkit-desktop-policy

## we conflict with gdm that contains the GNOME gdm xsession
Conflicts: gdm < 1:2.6.0.8-5

BuildRequires: gtk2-devel >= %{gtk2_version}
BuildRequires: dbus-devel >= %{dbus_version}
BuildRequires: dbus-glib-devel >= %{dbus_glib_version}
BuildRequires: gnome-keyring-devel >= %{gnome_keyring_version}
BuildRequires: libnotify-devel >= %{libnotify_version}
BuildRequires: GConf2-devel >= %{gconf2_version}
BuildRequires: GConf2-gtk >= %{gconf2_version}
BuildRequires: gnome-desktop-devel
BuildRequires: pango-devel
BuildRequires: gnome-settings-daemon-devel
BuildRequires: desktop-file-utils
BuildRequires: libXau-devel
BuildRequires: libXrandr-devel
BuildRequires: xorg-x11-xtrans-devel

# this is so the configure checks find /usr/bin/halt etc.
BuildRequires: usermode

BuildRequires: intltool, autoconf, automake
BuildRequires: libtool
BuildRequires: gettext
BuildRequires: libX11-devel libXt-devel
BuildRequires: libXtst-devel
BuildRequires: xmlto
BuildRequires: DeviceKit-power-devel
BuildRequires: gnome-common

# for patch3
BuildRequires: libnotify-devel

Requires(pre): GConf2 >= %{gconf2_version}
Requires(post): GConf2 >= %{gconf2_version}
Requires(preun): GConf2 >= %{gconf2_version}

# https://bugzilla.gnome.org/show_bug.cgi?id=592520
#Patch0: unresponsive-timeout.patch
# https://bugzilla.gnome.org/show_bug.cgi?id=592519
#Patch1: show-lock.patch
# https://bugzilla.gnome.org/show_bug.cgi?id=598211
Patch2: xsmp-stop.patch

# https://bugzilla.gnome.org/show_bug.cgi?id=597030
Patch3: 0001-Add-ability-to-perform-actions-after-a-period-of-idl.patch

# https://bugzilla.gnome.org/show_bug.cgi?id=607094
Patch4: nag-root-user.patch

# https://bugzilla.gnome.org/show_bug.cgi?id=613270
Patch5: add-custom-session-selector.patch

# translation updates
# https://bugzilla.redhat.com/show_bug.cgi?id=553594
Patch6: gnome-session-translations.patch

# https://bugzilla.gnome.org/show_bug.cgi?id=575544
Patch7: add-save-back.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=589184
Patch8: fix-up-man-page.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=573024
Patch9: drop-no-description.patch

%description
gnome-session manages a GNOME desktop or GDM login session. It starts up
the other core GNOME components and handles logout and saving the session.

%package xsession
Summary: gnome-session desktop file
Group: User Interface/Desktop
Requires: gnome-session = %{version}-%{release}

%description xsession
Desktop file to add GNOME to display manager session menu.

%package custom-session
Summary: A facility to select and store saved sessions
Group: User Interface/Desktop
Requires: gnome-session = %{version}-%{release}

%description custom-session
Installs a 'Custom' entry in the display manager session menu that
lets the user manage multiple saved sessions.

%prep
%setup -q
#%patch0 -p1 -b .unresponsive-timeout
#%patch1 -p1 -b .show-lock
%patch2 -p1 -b .xsmp-stop
%patch3 -p1 -b .max-idle
%patch4 -p1 -b .nag-root-user
%patch5 -p1 -b .add-custom-session-selector

echo "ACLOCAL_AMFLAGS = -I m4" >> Makefile.am

autoreconf -i -f

cp %{SOURCE3} po

%patch6 -p1 -b .translations
%patch7 -p1 -b .add-save-back
%patch8 -p1 -b .fix-up-man-page
%patch9 -p1 -b .drop-no-description

%build

%configure --enable-docbook-docs --docdir=%{_datadir}/doc/%{name}-%{version} --enable-session-selector
make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT

export GCONF_DISABLE_MAKEFILE_SCHEMA_INSTALL=1
make install DESTDIR=$RPM_BUILD_ROOT
unset GCONF_DISABLE_MAKEFILE_SCHEMA_INSTALL

desktop-file-install --vendor gnome --delete-original                   \
  --dir $RPM_BUILD_ROOT%{_datadir}/applications			        \
  --add-only-show-in GNOME                                              \
  $RPM_BUILD_ROOT%{_datadir}/applications/*

/bin/rm -f $RPM_BUILD_ROOT%{_datadir}/gnome/autostart/gnome-login-sound.desktop
/bin/rm -f $RPM_BUILD_ROOT%{_datadir}/gnome/shutdown/gnome-logout-sound.sh
/bin/rm -f $RPM_BUILD_ROOT%{_libdir}/gnome-session/helpers/gnome-login-sound

mkdir -p $RPM_BUILD_ROOT%{_datadir}/gnome/autostart

cp AUTHORS COPYING NEWS README $RPM_BUILD_ROOT%{_datadir}/doc/%{name}-%{version}

%find_lang %{po_package}

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/ldconfig
export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
gconftool-2 --makefile-install-rule %{_sysconfdir}/gconf/schemas/gnome-session.schemas >& /dev/null || :

%pre
if [ "$1" -gt 1 ]; then
  export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
  gconftool-2 --makefile-uninstall-rule %{_sysconfdir}/gconf/schemas/gnome-session.schemas >& /dev/null || :
fi

%preun
if [ "$1" -eq 0 ]; then
  export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
  gconftool-2 --makefile-uninstall-rule %{_sysconfdir}/gconf/schemas/gnome-session.schemas >& /dev/null || :
fi

%postun -p /sbin/ldconfig

%files xsession
%defattr(-,root,root)
%{_datadir}/xsessions/gnome.desktop

%files custom-session
%defattr(-,root,root)
%{_datadir}/xsessions/gnome-custom-session.desktop
%{_bindir}/gnome-session-selector
%{_bindir}/gnome-session-custom-session
%{_datadir}/gnome-session/session-selector.ui
%doc %{_mandir}/man*/gnome-session-selector*

%files -f %{po_package}.lang
%defattr(-,root,root)
%doc %dir %{_datadir}/doc/%{name}-%{version}
%doc %{_datadir}/doc/%{name}-%{version}/AUTHORS
%doc %{_datadir}/doc/%{name}-%{version}/COPYING
%doc %{_datadir}/doc/%{name}-%{version}/NEWS
%doc %{_datadir}/doc/%{name}-%{version}/README
%doc %dir %{_datadir}/doc/%{name}-%{version}/dbus
%doc %{_datadir}/doc/%{name}-%{version}/dbus/*
%doc %{_mandir}/man*/gnome-session-properties*
%doc %{_mandir}/man*/gnome-session-save*
%doc %{_mandir}/man*/gnome-session*
%doc %{_mandir}/man*/gnome-wm*
%{_datadir}/applications/gnome-session-properties.desktop
%dir %{_datadir}/gnome-session
%{_datadir}/gnome/autostart
%{_bindir}/gnome-session
%{_bindir}/gnome-session-properties
%{_bindir}/gnome-session-save
%{_bindir}/gnome-wm
%{_sysconfdir}/gconf/schemas/*.schemas
%{_datadir}/gnome-session/gsm-inhibit-dialog.ui
%{_datadir}/gnome-session/session-properties.ui
%{_datadir}/icons/hicolor/*/apps/session-properties.png
%{_datadir}/icons/hicolor/scalable/apps/session-properties.svg
%dir %{_libdir}/gnome-session
%dir %{_libdir}/gnome-session/helpers
%{_libdir}/gnome-session/helpers/*
%{_sysconfdir}/xdg/autostart/gnome-settings-daemon-helper.desktop

%changelog
* Mon Aug 02 2010 Ray Strode <rstrode@redhat.com> 2.28.0-15
- Relicense session selector patch
  Related: #576291

* Thu Jul 08 2010 Ray Strode <rstrode@redhat.com> 2.28.0-14
- Fix up man page
  Resolves: #589184
- Drop "No description" text from capplet
  Resolves: #573024

* Mon Jun 21 2010 Ray Strode <rstrode@redhat.com> 2.28.0-13
- Add save button back
  Resolves: #501614

* Fri Jun 18 2010 Ray Strode <rstrode@redhat.com> 2.28.0-12
- Add rename support and various aesthetic improvements
  Related: #576291

* Wed Jun 02 2010 Ray Strode <rstrode@redhat.com> 2.28.0-11
- Make sure the custom session selector isn't pulled into the wrong
  subpackage
  Related: #576291

* Tue Jun  1 2010 Matthias Clasen <mclasen@redhat.com> 2.28.0-10
- Updated translations
Resolves: #553594

* Wed May 19 2010 Ray Strode <rstrode@redhat.com> 2.28.0-9
- Drop stale gnome.desktop
  Resolves: #553591

* Mon Mar 22 2010 Ray Strode <rstrode@redhat.com> 2.28.0-8
Resolves: #576291
- Add custom session selector

* Fri Jan 15 2010 Ray Strode <rstrode@redhat.com> - 2.28.0-6
Resolves: #555804
- Nag user if they try to log in as root

* Thu Jan 14 2010 Matthias Clasen  <mclasen@redhat.com> - 2.28.0-5
- Update the as_IN translations (#553603)

* Fri Nov  6 2009 Matthias Clasen  <mclasen@redhat.com> - 2.28.0-3
- Add ability to perform actions after a period of idleness

* Fri Oct 23 2009 Matthias Clasen  <mclasen@redhat.com> - 2.28.0-2
- Avoid a crash on certain xsmp error conditions

* Wed Sep 23 2009 Matthias Clasen  <mclasen@redhat.com> - 2.28.0-1
- Update to 2.28.0

* Wed Sep  9 2009 Matthias Clasen  <mclasen@redhat.com> - 2.27.92-1
- Update to 2.27.92

* Thu Aug 13 2009 Matthias Clasen  <mclasen@redhat.com> - 2.27.5-2
- Require polkit-desktop-policy

* Tue Jul 28 2009 Matthias Clasen  <mclasen@redhat.com> - 2.27.5-1
- Update to 2.27.5

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.27.4-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Mon Jul 20 2009 Matthias Clasen  <mclasen@redhat.com> - 2.27.4-2
- Require polkit-gnome, we need an authentication agent in the session

* Wed Jul 15 2009 Matthias Clasen  <mclasen@redhat.com> - 2.27.4-1
- Update to 2.27.4

* Fri Jul 10 2009 Matthias Clasen  <mclasen@redhat.com> - 2.26.1-5
- Avoid pointless warnings

* Sun Jun 14 2009 Matthias Clasen  <mclasen@redhat.com> - 2.26.1-4
- Drop unused files

* Fri Jun 12 2009 Matthias Clasen  <mclasen@redhat.com> - 2.26.1-3
- Fix some oversights in the PolicyKit port

* Tue May 12 2009 Matthias Clasen  <mclasen@redhat.com> - 2.26.1-2
- Port to PolicyKit 1

* Tue Apr 14 2009 Matthias Clasen  <mclasen@redhat.com> - 2.26.1-1
- Update to 2.26.1
- See http://download.gnome.org/sources/gnome-session/2.26/gnome-session-2.26.1.news

* Wed Apr  8 2009 Matthias Clasen  <mclasen@redhat.com> - 2.26.0.90-1
- Update to 2.26.0.90

* Sun Apr  5 2009 Matthias Clasen  <mclasen@redhat.com> - 2.26.0-2
- Avoid some warnings (#493688)

* Mon Mar 16 2009 Matthias Clasen  <mclasen@redhat.com> - 2.26.0-1
- Update to 2.26.0

* Fri Mar  6 2009 Matthias Clasen  <mclasen@redhat.com> - 2.25.92-2
- Turn off excessive debug spew

* Tue Mar  3 2009 Matthias Clasen  <mclasen@redhat.com> - 2.25.92-1
- Update to 2.25.92

* Thu Feb 26 2009 Matthias Clasen  <mclasen@redhat.com> - 2.25.91-4
- Make -xsession arch again
- Fix xsync usage

* Tue Feb 24 2009 Matthias Clasen  <mclasen@redhat.com> - 2.25.91-3
- Make -xsession noarch

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.25.91-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Wed Feb 18 2009 Matthias Clasen  <mclasen@redhat.com> - 2.25.91-1
- Update to 2.25.91

* Tue Feb  3 2009 Matthias Clasen  <mclasen@redhat.com> - 2.25.90-1
- Update to 2.25.90

* Tue Jan 20 2009 Matthias Clasen  <mclasen@redhat.com> - 2.25.5-2
- Update to 2.25.5
- Fix BuildRequires

* Wed Dec 17 2008 Matthias Clasen  <mclasen@redhat.com> - 2.25.3-1
- Update to 2.25.3

* Thu Dec  4 2008 Matthias Clasen  <mclasen@redhat.com> - 2.25.2-2
- Update to 2.25.2

* Tue Nov 25 2008 Matthias Clasen  <mclasen@redhat.com> - 2.24.1-5
- Spec file cleanups

* Mon Nov 10 2008 Matthias Clasen  <mclasen@redhat.com> - 2.24.1-4
- Fix client registration in some cases 

* Sun Oct 26 2008 Matthias Clasen  <mclasen@redhat.com> - 2.24.1-3
- Make the capplet resizable (#468577)

* Wed Oct 22 2008 Matthias Clasen  <mclasen@redhat.com> - 2.24.1-1
- Update to 2.24.1
- Drop upstreamed patches

* Wed Oct 15 2008 Ray Strode <rstrode@redhat.com> - 2.24.0-11
- Remove some dubious code to fix panel race at startup that
  would make shutdown menu item disappear for some users.

* Fri Oct 10 2008 Ray Strode <rstrode@redhat.com> - 2.24.0-10
- Rewrite patch another time leverage better api and be more
  terse

* Fri Oct 10 2008 Ray Strode <rstrode@redhat.com> - 2.24.0-9
- Bring shutdown menu item back.  More fallout from my buggy
  patch introduced in -7

* Thu Oct  9 2008 Ray Strode <rstrode@redhat.com> - 2.24.0-8
- Fix assertion failure in last patch

* Thu Oct  9 2008 Ray Strode <rstrode@redhat.com> - 2.24.0-7
- Add new api for panel to figure out whether or not to show
  Shutdown menu item.

* Fri Oct  3 2008 Matthias Clasen  <mclasen@redhat.com> - 2.24.0-6
- Fix missing translations in the capplet
- Fix small UI issues in the capplet

* Sun Sep 28 2008 Matthias Clasen  <mclasen@redhat.com> - 2.24.0-5
- BR xorg-x11-xtrans-devel (#464316)

* Fri Sep 26 2008 Ray Strode  <rstrode@redhat.com> - 2.24.0-4
- Make the new xsession subpackage require the version of
  gnome-session it's built against

* Thu Sep 25 2008 Ray Strode  <rstrode@redhat.com> - 2.24.0-3
- Split gnome-session.desktop off into subpackage

* Mon Sep 22 2008 Matthias Clasen  <mclasen@redhat.com> - 2.24.0-2
- Update to 2.24.0
- Drop upstreamed patches

* Thu Sep 18 2008 Matthias Clasen  <mclasen@redhat.com> - 2.23.92-6
- Plug memory leaks

* Thu Sep 18 2008 Matthias Clasen  <mclasen@redhat.com> - 2.23.92-5
- Plug memory leaks

* Mon Sep 15 2008 Matthias Clasen  <mclasen@redhat.com> - 2.23.92-4
- Plug memory leaks

* Sun Sep 14 2008 Matthias Clasen  <mclasen@redhat.com> - 2.23.92-3
- Plug memory leaks

* Sun Sep 14 2008 Matthias Clasen  <mclasen@redhat.com> - 2.23.92-2
- Plug memory leaks

* Mon Sep  8 2008 Jon McCann  <jmccann@redhat.com> - 2.23.92-1
- Update to 2.23.92

* Tue Sep  2 2008 Matthias Clasen  <mclasen@redhat.com> - 2.23.91-1
- Update to 2.23.91

* Thu Aug 28 2008 Jon McCann  <jmccann@redhat.com> - 2.23.91.0.2008.08.28.1
- Update to snapshot

* Fri Aug 22 2008 Matthias Clasen  <mclasen@redhat.com> - 2.23.90-1
- Update to 2.23.90

* Thu Aug 14 2008 Lennart Poettering  <lpoetter@redhat.com> - 2.23.6-4
- Drop login/logout sound scripts since we do this now in libcanberra

* Tue Aug 12 2008 Matthias Clasen  <mclasen@redhat.com> - 2.23.6-3
- Fix a crash in the at-spi-registryd-wrapper

* Thu Aug  7 2008 Matthias Clasen  <mclasen@redhat.com> - 2.23.6-2
- Fix another icon name

* Tue Aug  5 2008 Matthias Clasen  <mclasen@redhat.com> - 2.23.6-1
- Update to 2.23.6

* Wed Jul 30 2008 Jon McCann  <jmccann@redhat.com> - 2.23.6.0.2008.07.30.1
- New snapshot from DBus branch

* Mon Jul 29 2008 Jon McCann  <jmccann@redhat.com> - 2.23.6.0.2008.07.29.1
- New snapshot from DBus branch

* Mon Jul 28 2008 Jon McCann  <jmccann@redhat.com> - 2.23.5.0.2008.07.28.1
- New snapshot from DBus branch

* Thu Jul 24 2008 Matthias Clasen  <mclasen@redhat.com> - 2.23.5.0.2008.07.21.4
- Fix a crash

* Mon Jul 22 2008 Jon McCann  <jmccann@redhat.com> - 2.23.5.0.2008.07.21.3
- Add BuildRequires PolicyKit-gnome-devel

* Mon Jul 21 2008 Jon McCann  <jmccann@redhat.com> - 2.23.5.0.2008.07.21.2
- New snapshot to fix build

* Mon Jul 21 2008 Jon McCann  <jmccann@redhat.com> - 2.23.5.0.2008.07.21.1
- Snapshot from DBus branch

* Wed Jul  9 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.4.1-4
- Fix a typo in the previous patch

* Wed Jul  9 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.4.1-3
- Use more standard icon names

* Tue Jul  8 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.4.1-2
- Escape comments for markup

* Wed Jun 18 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.4.1-1
- Update to 2.23.4.1

* Wed Jun  4 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.3-1
- Update to 2.23.3

* Fri May 16 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.2.2-3
- Make nautilus start again

* Thu May 15 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.2.2-2
- Don't crash while handling legacy sessions

* Wed May 14 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.2.2-1
- Update to 2.23.2.2

* Fri Apr 25 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.1-1
- Update to 2.23.1

* Thu Apr 10 2008 Matthias Clasen <mclasen@redhat.com> - 2.22.1.1-1
- Update to 2.22.1.1 (fixes a crash in the trash migration code)

* Mon Apr  7 2008 Matthias Clasen <mclasen@redhat.com> - 2.22.1-1
- Update to 2.22.1

* Sun Apr  6 2008 Matthias Clasen <mclasen@redhat.com> - 2.22.0-2
- Drop gnome-volume-manager from the default session

* Mon Mar 10 2008 Matthias Clasen <mclasen@redhat.com> - 2.22.0-1
- Update to 2.22.0

* Thu Mar 06 2008 - Bastien Nocera <bnocera@redhat.com> - 2.21.93-1
- Update to 2.21.93, drop esound dependencies and patches

* Tue Feb 26 2008 Matthias Clasen <mclasen@redhat.com> - 2.21.92-1
- Update to 2.21.92

* Tue Feb 12 2008  Matthias Clasen <mclasen@redhat.com> - 2.21.91-1
- Update to 2.21.91

* Mon Feb 11 2008 - Bastien Nocera <bnocera@redhat.com> - 2.21.90-2
- Add patch to make login sounds work
- Remove unneeded patch to launch gnome-user-share, it launches
  using autostart now

* Tue Jan 29 2008  Matthias Clasen <mclasen@redhat.com> - 2.21.90-1
- Update to 2.21.90

* Tue Jan 15 2008  Matthias Clasen <mclasen@redhat.com> - 2.21.5-1
- Update to 2.21.5

* Tue Nov 27 2007  Matthias Clasen <mclasen@redhat.com> - 2.20.2-1
- Update to 2.20.2 (translation updates)

* Tue Oct 30 2007 - Bastien Nocera <bnocera@redhat.com> - 2.20.1-2
- Enable sound by default, without looking at the prefs

* Mon Oct 15 2007 Matthias Clasen <mclasen@redhat.com> - 2.20.1-1
- Update to 2.20.1 (translation updates)

* Thu Sep 27 2007 Ray Strode <rstrode@redhat.com> - 2.20.0-2
- drop redhat-artwork dep.  We don't need it.

* Mon Sep 17 2007 Matthias Clasen <mclasen@redhat.com> - 2.20.0-1
- Update to 2.20.0

* Tue Sep 11 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.92-3
- Plug memory leaks in the ICE code

* Wed Sep  5 2007 Kristian Høgsberg <krh@redhat.com> - 2.19.92-2
- Update gnome-session-2.17.5-window-manager.patch to apply (remove
  chunks that are now upstream).

* Tue Sep  4 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.92-1
- Update to 2.19.92

* Thu Aug 23 2007 Adam Jackson <ajax@redhat.com> - 2.19.90-2
- Rebuild for build ID

* Mon Aug 13 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.90-1
- Update to 2.19.90

* Fri Aug 10 2007 Kristian Høgsberg <krh@redhat.com> - 2.19.6-5
- Edit window manager patch again to add 'glib' to compiz launch.

* Thu Aug  9 2007 Kristian Høgsberg <krh@redhat.com> - 2.19.6-4
- Edit the right window manager patch and delete the old one.

* Thu Aug  9 2007 Kristian Høgsberg <krh@redhat.com> - 2.19.6-3
- Export LIBGL_ALWAYS_INDIRECT before starting compiz.

* Fri Aug  3 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.6-2
- Update license field

* Mon Jul 30 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.6-1
- Update to 2.19.6

* Sun Jul  8 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.5-1
- Update to 2.19.5

* Fri Jul  6 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.4-3
- Move /usr/share/gnome/wm-properties to control-center-filesystem

* Tue Jun 19 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.4-2
- Fix a hang on login with a11y

* Sun Jun 17 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.4-1
- Update to 2.19.4

* Mon Jun  4 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.3-1
- Update to 2.19.3
- Drop upstreamed patch

* Tue May 22 2007 - Bastien Nocera <bnocera@redhat.com> - 2.19.2-2
- Fix up logic in iris patch

* Sun May 20 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.2-1
- Update to 2.19.2

* Tue May 15 2007 Ray Strode <rstrode@redhat.com> - 2.18.0-7
- Don't show iris animation when using compiz (bug 237842)

* Sun May  6 2007 Matthias Clasen <mclasen@redhat.com> - 2.18.0-6
- Don't own /usr/share/applications

* Sat Apr 14 2007 Matthias Clasen <mclasen@redhat.com> - 2.18.0-5
- Add a dependency on dbus-x11

* Thu Apr 12 2007 David Zeuthen <davidz@redhat.com> - 2.18.0-4
- start same kind of AT's in session as started in gdm (#229912)

* Fri Mar 30 2007 Ray Strode <rstrode@redhat.com> - 2.18.0-3
- remove xdg autostart dir since it's part of filesystem now

* Wed Mar 21 2007 Ray Strode <rstrode@redhat.com> - 2.18.0-2
- remove eggcups from default session (bug 233261)

* Tue Mar 13 2007 Matthias Clasen <mclasen@redhat.com> - 2.18.0-1
- Update to 2.18.0

* Wed Feb 28 2007 Matthias Clasen <mclasen@redhat.com> - 2.17.92-1
- Update to 2.17.92

* Fri Feb 23 2007 Jeremy Katz <katzj@redhat.com> - 2.17.91-2
- disable a11y registry timeout so that we don't get the popup with 
  the livecd (#227214)

* Tue Feb 13 2007 Matthisa Clasen <mclasen@redhat.com> - 2.17.91-1
- Update to 2.17.91

* Tue Feb  6 2007 Kristian Høgsberg <krh@redhat.com> - 2.17.90.1-3
- Update gnome-session-2.15.90-window-manager.patch to start
  gtk-window-decorator instead of gnome-window-decorator for compiz.

  [ Update: the patch is not applied and upstream gnome-session does
    the right thing. ]

* Mon Feb  5 2007 Matthias Clasen <mclasen@redhat.com> - 2.17.90.1-2
- Require GConf2-gtk for gconf-sanity-check 

* Tue Jan 23 2007 Matthias Clasen <mclasen@redhat.com> - 2.17.90.1-1
- Update to 2.17.90.1

* Sun Jan 21 2007 Matthias Clasen <mclasen@redhat.com> - 2.17.90-1
- Update to 2.17.90
- Clean up BuildRequires

* Wed Jan 10 2007 Matthias Clasen <mclasen@redhat.com> - 2.17.5-1
- Update to 2.17.5

* Mon Nov 27 2006 Ray Strode <rstrode@redhat.com> - 2.17.2-6
- don't set http_proxy variable if proxy requires password (bug
  217332)

* Wed Nov 22 2006 Matthias Clasen <mclasen@redhat.com> - 2.17.2-4
- Own the /usr/share/gnome/wm-properties directory (#216514)

* Mon Nov 20 2006 Ray Strode <rstrode@redhat.com> - 2.17.2-3
- don't make gnome.desktop executable (bug 196105)

* Sat Nov 11 2006 Matthias Clasen  <mclasen@redhat.com> - 2.17.2-2
- Fix gnome-wm for compiz

* Tue Nov  7 2006 Matthias Clasen  <mclasen@redhat.com> - 2.17.2-1
- Update to 2.17.2

* Thu Oct 26 2006 Ray Strode <rstrode@redhat.com> - 2.16.1-2.fc7
- don't hose users with a stale http_proxy variable if they
  use autoconfiguration and uses to use manual configuration.
  Patch by Mark McLoughlin (bug 212319)

* Sat Oct 21 2006 Matthias Clasen <mclasen@redhat.com> - 2.16.1-1
- Update to 2.16.1

* Wed Oct 18 2006 Matthias Clasen <mclasen@redhat.com> - 2.16.0-4
- Fix scripts according to the packaging guidelines

* Thu Sep  7 2006 Matthias Clasen <mclasen@redhat.com> - 2.16.0-3.fc6
- Fix position of icons in the splash screen  (#205508)

* Wed Sep  6 2006 Ray Strode <rstrode@redhat.com> - 2.16.0-2.fc6
- set http_proxy environment variable from GNOME settings 
  (bug 190041)

* Mon Sep  4 2006 Matthias Clasen <mclasen@redhat.com> - 2.16.0-1.fc6
- Update to 2.16.0

* Mon Aug 21 2006 Matthias Clasen <mclasen@redhat.com> - 2.15.92-1.fc6
- Update to 2.15.92
- Add %%preun and %%postun scripts

* Mon Aug 14 2006 Ray Strode <rstrode@redhat.com> - 2.15.91-1.fc6
- Update to 2.15.91

* Sun Aug 13 2006 Ray Strode <rstrode@redhat.com> - 2.15.90-4.fc6
- fix window manager launching script. Patch from 
  Tim Vismor <tvismor@acm.org> (bug 202312)

* Fri Aug 11 2006 Ray Strode <rstrode@redhat.com> - 2.15.90-3.fc6
- start gnome-window-decorator and pass "gconf" when invoking
  compiz

* Thu Aug 10 2006 Ray Strode <rstrode@redhat.com> - 2.15.90-2.fc6
- update patch from 2.15.4-3 to be more session friendly (bug 201473)

* Fri Aug  4 2006 Matthias Clasen <mclasen@redhat.com> - 2.15.90-1.fc6
- Update to 2.15.90

* Thu Aug  3 2006 Soren Sandmann <sandmann@redhat.com> - 2.15.4-3
- Add patch to (a) add configuration option for window manager, (b) start the window
  manager, and (c) disable splash screen by default.

* Wed Jul 19 2006 John (J5) Palmieri <johnp@redhat.com> - 2.15.4-2
- Add BR for dbus-glib-devel

* Thu Jul 13 2006 Ray Strode <rstrode@redhat.com> - 2.15.4-1
- Update to 2.15.4

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 2.15.1-5.1
- rebuild

* Mon Jun 12 2006 Bill Nottingham  <notting@redhat.com> 2.15.1-5
- remove obsolete automake14 buildreq

* Fri Jun  9 2006 Matthias Clasen  <mclasen@redhat.com> 2.15.1-4
- Add more missing BuildRequires

* Tue Jun  6 2006 Matthias Clasen  <mclasen@redhat.com> 2.15.1-3
- Add BuildRequires: intltool, autoconf, automake 

* Mon Jun  5 2006 Matthias Clasen <mclasen@redhat.com> - 2.15.1-2
- Require system-logos, not fedora-logos

* Wed May 10 2006 Matthias Clasen <mclasen@redhat.com> - 2.15.1-1
- Update to 2.15.1

* Mon Apr 10 2006 Matthias Clasen <mclasen@redhat.com> - 2.14.1-2
- Update to 2.14.1

* Mon Mar 13 2006 Matthias Clasen <mclasen@redhat.com> - 2.14.0-1
- Update to 2.14.0

* Thu Mar 09 2006 Ray Strode <rstrode@redhat.com> - 2.13.92-5
- fix up path creation functions 

* Thu Mar 09 2006 Ray Strode <rstrode@redhat.com> - 2.13.92-4
- create ~/.config/autostart before trying to migrate
  session-manual to it (bug 179602).

* Mon Mar 06 2006 Ray Strode <rstrode@redhat.com> - 2.13.92-3
- Patch from Vincent Untz to fix session editing (upstream bug 333641)
- Desensitize buttons for operations that the user isn't allowed
  to do (bug 179479).

* Wed Mar 01 2006 Karsten Hopp <karsten@redhat.de> 2.13.92-2
- BuildRequires: gnome-desktop-devel, libX11-devel, libXt-devel

* Tue Feb 28 2006 Ray Strode <rstrode@redhat.com> - 2.13.92-1
- Update to 2.13.92
- Add patch from CVS HEAD to maintain compatibility with
  version 2.13.91

* Thu Feb 23 2006 Ray Strode <rstrode@redhat.com> - 2.13.91-2
- take ownership of autostart dir (bug 182335)

* Mon Feb 13 2006 Matthias Clasen <mclasen@redhat.com> - 2.13.91-1
- Update to 2.13.91

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 2.13.90-1.2
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 2.13.90-1.1
- rebuilt for new gcc4.1 snapshot and glibc changes

* Sat Jan 28 2006 Matthias Clasen <mclasen@redhat.com> - 2.13.90-1
- Update to 2.13.90

* Tue Jan 17 2006 Matthias Clasen <mclasen@redhat.com> - 2.13.5-1
- Update to 2.13.5

* Mon Jan 16 2006 Matthias Clasen <mclasen@redhat.com> - 2.13.4-2
- Disable the fatal-criticals, since it crashes too much 

* Fri Jan 13 2006 Matthias Clasen <mclasen@redhat.com> - 2.13.4-1
- Update to 2.13.4

* Thu Jan 12 2006 Ray Strode <rstrode@redhat.com> - 2.12.0-6
- Fix screen corruption around splash screen shape (bug 177502)

* Tue Dec 20 2005 John (J5) Palmieri <johnp@redhat.com> - 2.12.0-5
- Handle shaped window for splash screen

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Wed Nov  9 2005 Alexander Larsson <alexl@redhat.com> - 2.12.0-4
- Add gnome-user-share patch

* Tue Nov 8 2005 Ray Strode <rstrode@redhat.com> - 2.12.0-3
- fix up the dummy client ids to match the id passed initially
  passed to the programs in the default session 
  (broke in last update).

* Mon Oct 31 2005 Ray Strode <rstrode@redhat.com> - 2.12.0-2
- remove rhn applet from default session
- s/magicdev/gnome-volume-manager/

* Thu Sep  8 2005 Matthias Clasen <mclasen@redhat.com> - 2.12.0-1
- Update to 2.12.0

* Tue Sep  6 2005 Ray Strode <rstrode@redhat.com> - 2.11.91-3
- Don't take ownership of /usr/share/xsessions (bug 145791).

* Tue Aug 16 2005 Warren Togami <wtogami@redhat.com> - 2.11.91-2
- rebuild for new cairo

* Tue Aug  9 2005 Ray Strode <rstrode@redhat.com> - 2.11.91-1
- Update to upstream version 2.11.91 (fixes bug 165357).
- drop some patches

* Thu Apr 18 2005 Ray Strode <rstrode@redhat.com> - 2.10.0-2
- Install gnome.desktop to /usr/share/xsessions (bug 145791)

* Thu Mar 17 2005 Ray Strode <rstrode@redhat.com> - 2.10.0-1
- Update to upstream version 2.10.0

* Wed Feb  2 2005 Matthias Clasen <mclasen@redhat.com> 2.9.4-1
- Update to 2.9.4

* Mon Dec 20 2004 Daniel Reed <djr@redhat.com> 2.8.0-7
- rebuild for new libhowl.so.0 library (for GnomeMeeting 1.2) (this was a mistake)

* Tue Nov 02 2004 Ray Strode <rstrode@redhat.com> 2.8.0-6
- Rebuild for devel branch

 * Tue Nov 02 2004 Ray Strode <rstrode@redhat.com> 2.8.0-5
- Convert Tamil translation to UTF8 
  (Patch from Lawrence Lim <llim@redhat.com>, bug 135351)

* Fri Oct 08 2004 Ray Strode <rstrode@redhat.com> 2.8.0-4
- Add g-v-m to default session since it wasn't already (?).
- Remove g-v-m from default session on s390

* Thu Oct 07 2004 Ray Strode <rstrode@redhat.com> 2.8.0-3
- Check for NULL program name when looking for client
  match in session.

* Fri Sep 24 2004 Ray Strode <rstrode@redhat.com> 2.8.0-2
- Add "Session" item to More Preferences menu

* Fri Sep 17 2004 Ray Strode <rstrode@redhat.com> 2.8.0-1
- Update to 2.8.0 
- Remove "Session" item from Preferences menu

* Fri Sep 03 2004 Ray Strode <rstrode@redhat.com> 2.7.91-2
- Fix from Federico for infamous hanging splash screen problem.
  (http://bugzilla.gnome.org/show_bug.cgi?id=151664)

* Tue Aug 31 2004 Ray Strode <rstrode@redhat.com> 2.7.91-1
- Update to 2.7.91

* Wed Aug 18 2004 Ray Strode <rstrode@redhat.com> 2.7.4-3
- Change folder name from "autostart" to more aptly named
  "session-upgrades" from suggestion by Colin Walters.
- put non-upstream gconf key in rh_extensions

* Wed Aug 18 2004 Ray Strode <rstrode@redhat.com> 2.7.4-2
- Provide drop-a-desktop-file method of adding programs
  to the user's session.

* Fri Jul 30 2004 Ray Strode <rstrode@redhat.com> 2.7.4-1
- Update to 2.7.4

* Wed Jul 14 2004 root <markmc@localhost.localdomain> - 2.6.0-7
- Add patch to activate vino based on the "remote_access/enabled"
  preference

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Mon Jun 14 2004 Ray Strode <rstrode@redhat.com> 2.6.0-5
- Prevent having duplicate packages in different collections

* Mon Jun 14 2004 Ray Strode <rstrode@redhat.com> 2.6.0-4
- Use desktop-file-install instead of patching 
  session-properties.desktop.  Add X-Red-Hat-Base category.

* Thu Jun 10 2004 Ray Strode <rstrode@redhat.com> 2.6.0-3
- Add terminating list delimiter to OnlyShowIn entry of 
  session-properties.desktop

* Fri Apr 16 2004 Warren Togami <wtogami@redhat.com> 2.6.0-2
- #110725 BR automake14 autoconf gettext

* Wed Mar 31 2004 Mark McLoughlin <markmc@redhat.com> 2.6.0-1
- Update to 2.6.0

* Wed Mar 10 2004 Mark McLoughlin <markmc@redhat.com>
- Update to 2.5.91

* Tue Feb 24 2004 Mark McLoughlin <markmc@redhat.com> 2.5.90-1
- Update to 2.5.90
- Remove extraneous fontconfig BuildRequires
- Resolve conflicts with the icons and splash-repaint patches

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Mon Jan 26 2004 Alexander Larsson <alexl@redhat.com> 2.5.3-1
- Update to 2.5.3

* Wed Nov 05 2003 Than Ngo <than@redhat.com> 2.4.0-2
- don't show gnome-session-properties in KDE (bug #102533)

* Fri Aug 29 2003 Alexander Larsson <alexl@redhat.com> 2.3.7-3
- fix up gnome.desktop location

* Fri Aug 29 2003 Alexander Larsson <alexl@redhat.com> 2.3.7-2
- add gnome.desktop session for new gdm

* Wed Aug 27 2003 Alexander Larsson <alexl@redhat.com> 2.3.7-1
- update to 2.3.7
- require control-center (#100562)

* Fri Aug 15 2003 Alexander Larsson <alexl@redhat.com> 2.3.6.2-1
- update for gnome 2.3

* Sun Aug 10 2003 Elliot Lee <sopwith@redhat.com> 2.2.2-4
- Rebuild

* Tue Jul 22 2003 Jonathan Blandford <jrb@redhat.com>
- at-startup patch to add let at's start

* Wed Jun 04 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue Jun  3 2003 Jeff Johnson <jbj@redhat.com>
- add explicit epoch's where needed.

* Tue May 27 2003 Alexander Larsson <alexl@redhat.com> 2.2.2-1
- Update to 2.2.2
- Add XRandR backport
- Fix up old patches, patch7 was upstream

* Mon Feb 24 2003 Owen Taylor <otaylor@redhat.com> 2.2.0.2-5
- Wait for GSD to start before continuing with session

* Tue Feb 18 2003 Havoc Pennington <hp@redhat.com> 2.2.0.2-4
- repaint proper area of text in splash screen, #84527

* Tue Feb 18 2003 Havoc Pennington <hp@redhat.com> 2.2.0.2-3
- change icon for magicdev to one that exists in Bluecurve theme
  (part of #84491)

* Thu Feb 13 2003 Havoc Pennington <hp@redhat.com> 2.2.0.2-2
- load icons from icon theme

* Wed Feb  5 2003 Havoc Pennington <hp@redhat.com> 2.2.0.2-1
- 2.2.0.2

* Tue Feb  4 2003 Jonathan Blandford <jrb@redhat.com>
- remove extraneous separator.  Still ugly.

* Wed Jan 29 2003 Havoc Pennington <hp@redhat.com>
- add icons for the stuff in the default session #81489

* Wed Jan 22 2003 Tim Powers <timp@redhat.com>
- rebuilt

* Sat Jan 11 2003 Havoc Pennington <hp@redhat.com>
- 2.1.90
- drop purgedelay patch, as it was increased upstream (though only to 2 minutes instead of 5)

* Fri Dec  6 2002 Tim Waugh <twaugh@redhat.com> 2.1.2-2
- Add eggcups to default session.

* Wed Nov 13 2002 Havoc Pennington <hp@redhat.com>
- 2.1.2

* Tue Sep  3 2002 Owen Taylor <otaylor@redhat.com>
- Up purge delay for session manager to 5 minutes to avoid problem 
  with openoffice.org timing out

* Wed Aug 28 2002 Havoc Pennington <hp@redhat.com>
- put gdm session in here, conflict with old gdm
- use DITHER_MAX for dithering to make splash screen look good in 16
  bit

* Tue Aug 27 2002 Havoc Pennington <hp@redhat.com>
- fix missing icons and misaligned text in splash

* Fri Aug 23 2002 Tim Waugh <twaugh@redhat.com>
- Fix login sound disabling (bug #71664).

* Wed Aug 14 2002 Havoc Pennington <hp@redhat.com>
- put rhn applet in default session

* Wed Aug 14 2002 Havoc Pennington <hp@redhat.com>
- fix the session file, should speed up login a lot
- put magicdev in default session

* Thu Aug  8 2002 Havoc Pennington <hp@redhat.com>
- 2.0.5 with more translations

* Tue Aug  6 2002 Havoc Pennington <hp@redhat.com>
- 2.0.4
- remove gnome-settings-daemon from default session

* Wed Jul 31 2002 Havoc Pennington <hp@redhat.com>
- 2.0.3
- remove splash screen, require redhat-artwork instead

* Wed Jul 24 2002 Owen Taylor <otaylor@redhat.com>
- Set GTK_RC_FILES so we can change the gtk1 theme

* Tue Jul 16 2002 Havoc Pennington <hp@redhat.com>
- pass --with-halt-command=/usr/bin/poweroff
  --with-reboot-command=/usr/bin/reboot

* Tue Jun 25 2002 Owen Taylor <otaylor@redhat.com>
- Version 2.0.1, fixing missing po files

* Wed Jun 19 2002 Havoc Pennington <hp@redhat.com>
- put in new default session with pam-panel-icon
- disable schema install in make install, fixes rebuild failure.

* Sun Jun 16 2002 Havoc Pennington <hp@redhat.com>
- rebuild with new libraries

* Thu Jun 13 2002 Havoc Pennington <hp@redhat.com>
- rebuild in different environment

* Thu Jun 13 2002 Havoc Pennington <hp@redhat.com>
- add fix from Nalin to build require usermode

* Tue Jun 11 2002 Havoc Pennington <hp@redhat.com>
- 2.0.0

* Mon Jun 10 2002 Havoc Pennington <hp@redhat.com>
- install the schemas, so we get a logout dialog and splash
- put in the splash from 7.3

* Sun Jun 09 2002 Havoc Pennington <hp@redhat.com>
- rebuild in different environment

* Sun Jun 09 2002 Havoc Pennington <hp@redhat.com>
- rebuild in new environment, require newer gtk2

* Sun Jun  9 2002 Havoc Pennington <hp@redhat.com>
- remove obsoletes/provides gnome-core

* Fri Jun 07 2002 Havoc Pennington <hp@redhat.com>
- rebuild in different environment

* Wed Jun  5 2002 Havoc Pennington <hp@redhat.com>
- 1.5.21

* Sun May 26 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Tue May 21 2002 Havoc Pennington <hp@redhat.com>
- rebuild in different environment

* Tue May 21 2002 Havoc Pennington <hp@redhat.com>
- 1.5.19
- add more build reqs to chill out build system
- provide gnome-core

* Fri May  3 2002 Havoc Pennington <hp@redhat.com>
- obsolete gnome-core
- 1.5.18

* Fri Apr 19 2002 Havoc Pennington <hp@redhat.com>
- default to metacity

* Tue Apr 16 2002 Havoc Pennington <hp@redhat.com>
- Initial build.


