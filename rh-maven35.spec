%global scl_name_prefix rh-
%global scl_name_base maven
%global scl_name_version 35
%global scl %{scl_name_prefix}%{scl_name_base}%{scl_name_version}
%scl_package %scl

%global debug_package %{nil}


Name:       %scl_name
Version:    2.0
Release:    0%{?dist}
Summary:    Package that installs %scl

License:    GPLv2+
Source4:    README
Source5:    LICENSE
Source6:    macros.build

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
Requires:   %{name}-javapackages-local

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
%%scl_maven %scl
%%scl_prefix_maven %scl_prefix
%%_scl_prefix_maven %_scl_prefix
%%_scl_scripts_maven %_scl_scripts
%%_scl_root_maven %_scl_root
# Generic paths inside SCL root
%%_bindir_maven %_bindir
%%_datadir_maven %_datadir
%%_defaultdocdir_maven %_defaultdocdir
%%_docdir_maven %_docdir
%%_exec_prefix_maven %_exec_prefix
%%_includedir_maven %_includedir
%%_infodir_maven %_infodir
%%_libdir_maven %_libdir
%%_libexecdir_maven %_libexecdir
%%_localstatedir_maven %_localstatedir
%%_mandir_maven %_mandir
%%_prefix_maven %_prefix
%%_sbindir_maven %_sbindir
%%_sharedstatedir_maven %_sharedstatedir
%%_sysconfdir_maven %_sysconfdir
# Java-specific paths inside SCL root
%%_ivyxmldir_maven %_ivyxmldir
%%_javaconfdir_maven %_javaconfdir
%%_javadir_maven %_javadir
%%_javadocdir_maven %_javadocdir
%%_jnidir_maven %_jnidir
%%_jvmcommondatadir_maven %_jvmcommondatadir
%%_jvmcommonlibdir_maven %_jvmcommonlibdir
%%_jvmcommonsysconfdir_maven %_jvmcommonsysconfdir
%%_jvmdatadir_maven %_jvmdatadir
%%_jvmdir_maven %_jvmdir
%%_jvmlibdir_maven %_jvmlibdir
%%_jvmprivdir_maven %_jvmprivdir
%%_jvmsysconfdir_maven %_jvmsysconfdir
%%_mavenpomdir_maven %_mavenpomdir
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
cat %{SOURCE6} >>%{buildroot}%{_root_sysconfdir}/rpm/macros.%{scl}-config

install -d -m 755 %{buildroot}%{_scl_scripts}
install -p -m 755 enable %{buildroot}%{_scl_scripts}/

# install rpm magic
install -Dpm0644 macros.%{scl_name} %{buildroot}%{_root_sysconfdir}/rpm/macros.%{scl_name_prefix}%{scl_name_base}-scldevel

# install dirs used by some deps
install -dm0755 %{buildroot}%{_scl_root}%{python_sitelib}
install -dm0755 %{buildroot}%{_defaultlicensedir}

# install generated man page
install -m 755 -d %{buildroot}%{_mandir}/man1
install -m 755 -d %{buildroot}%{_mandir}/man7
install -m 644 %{scl_name}.7 %{buildroot}%{_mandir}/man7/%{scl_name}.7


%files runtime
%doc README LICENSE
%{scl_files}
%{_mandir}/*
%{_prefix}/lib/python2.*
%{_defaultlicensedir}

%files build
%{_root_sysconfdir}/rpm/macros.%{scl}-config

%files scldevel
%{_root_sysconfdir}/rpm/macros.%{scl_name_prefix}%{scl_name_base}-scldevel

%changelog
