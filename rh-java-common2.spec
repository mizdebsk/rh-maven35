%global scl_name_prefix rh-
%global scl_name_base java-common
%global scl_name_version 2
%global scl %{scl_name_prefix}%{scl_name_base}%{scl_name_version}
%scl_package %scl

%global debug_package %{nil}


Name:       %scl_name
Version:    2.0
Release:    0.1%{?dist}
Summary:    Package that installs %scl

License:    GPLv2+
Source4:    README
Source5:    LICENSE

BuildRequires:  help2man
BuildRequires:  python-devel
BuildRequires:  scl-utils-build
BuildRequires:  %{name}-javapackages-tools

%description
This is the main package for the %scl Software Collection.

%package runtime
Summary:    Package that handles %scl Software Collection.
Requires:   scl-utils
Requires:   java-openjdk-headless
Requires:   %{name}-javapackages-tools

%description runtime
Package shipping essential scripts to work with the %scl Software Collection.

%package build
Summary:    Build support tools for the %scl Software Collection.
Requires:   scl-utils-build
Requires:   java-1.8.0-openjdk-devel
Requires:   %{name}-scldevel = %{version}-%{release}

%description build
Package shipping essential configuration marcros/files in order to be able
to build %scl Software Collection.

%package scldevel
Summary:    Package shipping development files for %scl
Requires:   %{name}-runtime = %{version}-%{release}

%description scldevel
Package shipping development files, especially useful for development of
packages depending on %scl Software Collection.

%prep
%setup -c -T
#===================#
# SCL enable script #
#===================#
cat <<EOF >enable
# Generic variables
export PATH="%{_bindir}:\${PATH:-/bin:/usr/bin}"
export MANPATH="%{_mandir}:\${MANPATH}"
export PYTHONPATH="%{_scl_root}%{python_sitelib}\${PYTHONPATH:+:}\${PYTHONPATH:-}"

export JAVACONFDIRS="%{_sysconfdir}/java\${JAVACONFDIRS:+:}\${JAVACONFDIRS:-}"
export XDG_CONFIG_DIRS="%{_sysconfdir}/xdg:\${XDG_CONFIG_DIRS:-/etc/xdg}"
export XDG_DATA_DIRS="%{_datadir}:\${XDG_DATA_DIRS:-/usr/local/share:/usr/share}"
EOF

# This section generates README file from a template and creates man page
# from that file, expanding RPM macros in the template file.
cat >README <<'EOF'
%{expand:%(cat %{SOURCE4})}
EOF

# copy the license file so %%files section sees it
cp %{SOURCE5} .

cat >macros.%{scl_name} <<EOF
# SCL configuration
%%scl_java_common %scl
%%scl_prefix_java_common %scl_prefix
%%_scl_prefix_java_common %_scl_prefix
%%_scl_scripts_java_common %_scl_scripts
%%_scl_root_java_common %_scl_root
# Generic paths inside SCL root
%%_bindir_java_common %_bindir
%%_datadir_java_common %_datadir
%%_defaultdocdir_java_common %_defaultdocdir
%%_docdir_java_common %_docdir
%%_exec_prefix_java_common %_exec_prefix
%%_includedir_java_common %_includedir
%%_infodir_java_common %_infodir
%%_libdir_java_common %_libdir
%%_libexecdir_java_common %_libexecdir
%%_localstatedir_java_common %_localstatedir
%%_mandir_java_common %_mandir
%%_prefix_java_common %_prefix
%%_sbindir_java_common %_sbindir
%%_sharedstatedir_java_common %_sharedstatedir
%%_sysconfdir_java_common %_sysconfdir
# Java-specific paths inside SCL root
%%_ivyxmldir_java_common %_ivyxmldir
%%_javaconfdir_java_common %_javaconfdir
%%_javadir_java_common %_javadir
%%_javadocdir_java_common %_javadocdir
%%_jnidir_java_common %_jnidir
%%_jvmcommondatadir_java_common %_jvmcommondatadir
%%_jvmcommonlibdir_java_common %_jvmcommonlibdir
%%_jvmcommonsysconfdir_java_common %_jvmcommonsysconfdir
%%_jvmdatadir_java_common %_jvmdatadir
%%_jvmdir_java_common %_jvmdir
%%_jvmlibdir_java_common %_jvmlibdir
%%_jvmprivdir_java_common %_jvmprivdir
%%_jvmsysconfdir_java_common %_jvmsysconfdir
%%_mavenpomdir_java_common %_mavenpomdir
EOF


%build
# generate a helper script that will be used by help2man
cat >h2m_helper <<'EOF'
#!/bin/bash
[ "$1" == "--version" ] && echo "%{scl_name} %{version} Software Collection" || cat README
EOF
chmod a+x h2m_helper

# generate the man page
help2man -N --section 7 ./h2m_helper -o %{scl_name}.7
# Fix single quotes in man page.
sed -i "s/'/\\\\(aq/g" %{scl_name}.7

%install
%scl_install

install -d -m 755 %{buildroot}%{_scl_scripts}
install -p -m 755 enable %{buildroot}%{_scl_scripts}/

# install rpm magic
install -Dpm0644 macros.%{scl_name} %{buildroot}%{_root_sysconfdir}/rpm/macros.%{scl_name_prefix}%{scl_name_base}-scldevel

# install dirs used by some deps
install -dm0755 %{buildroot}%{_prefix}/lib/rpm
install -dm0755 %{buildroot}%{_scl_root}%{python_sitelib}

# install generated man page
mkdir -p %{buildroot}%{_mandir}/man7/
install -m 644 %{scl_name}.7 %{buildroot}%{_mandir}/man7/%{scl_name}.7

install -m 755 -d %{buildroot}%{_mandir}/man1
install -m 755 -d %{buildroot}%{_mandir}/man7

install -m 755 -d %{buildroot}%{_javaconfdir}
install -m 755 -d %{buildroot}%{_javadir}
install -m 755 -d %{buildroot}%{_javadocdir}
install -m 755 -d %{buildroot}%{_jnidir}
install -m 755 -d %{buildroot}%{_mavenpomdir}
install -m 755 -d %{buildroot}%{_datadir}/maven-metadata
install -m 755 -d %{buildroot}%{_datadir}/xmvn

%files runtime
%doc README LICENSE
%{scl_files}
%{_prefix}/lib/python2.*
%{_prefix}/lib/rpm
%{_mandir}/man7/%{scl_name}.*
%dir %{_javaconfdir}
%dir %{_javadir}
%dir %{_javadocdir}
# %%{scl_files} macro owns all %%{_prefix}/lib subdirs/files with 555 perms
# we need to override this to prevent file conflict with javapackages-tools
%attr(755,root,root) %dir %{_jnidir}
%dir %{_mavenpomdir}
%dir %{_datadir}/maven-metadata
%dir %{_datadir}/xmvn
%dir %{_mandir}/man1
%dir %{_mandir}/man7

%files build
%{_root_sysconfdir}/rpm/macros.%{scl}-config

%files scldevel
%{_root_sysconfdir}/rpm/macros.%{scl_name_prefix}%{scl_name_base}-scldevel

%changelog
* Tue Feb 14 2017 Michael Simacek <msimacek@redhat.com> - 2.0-0.1
- Prepare for version 2
