# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

# Stand-in for: openRuyi Base compiled torch consumers
# (python-torchvision, python-torchaudio).
#
# Links against libfaketorch, so RPM generates an automatic
# "Requires: libfaketorch.so()(64bit)".  Whether that requirement can be
# satisfied is decided entirely by python-faketorch's --with/--without privlibs.
# Test B4 lives here.

%global srcname fakeext

Name:           python-%{srcname}
Version:        1.0.0
Release:        %autorelease
Summary:        Compiled torch consumer stand-in
License:        MulanPSL-2.0
URL:            https://github.com/Sakura286/test-package-require

Source0:        fakeext.c
Source1:        __init__.py

BuildRequires:  gcc
BuildRequires:  python3-devel
# Name-free, per openRuyi convention.  Which flavor answers this at build time
# is what prjconf "Prefer:" decides.
BuildRequires:  python3dist(faketorch)

%description
Test stand-in for a Base package carrying a compiled torch extension.  Its
soname requirement on libfaketorch.so is the thing that makes Base's
python-torchvision uninstallable against rocm-specs' torch.

%prep
rm -rf %{srcname}
mkdir -p %{srcname}
cp -p %{SOURCE0} .
cp -p %{SOURCE1} %{srcname}/__init__.py

%build
gcc %{build_cflags} %{build_ldflags} -shared -fPIC \
    -o %{srcname}/_%{srcname}.so %{SOURCE0} -lfaketorch

%install
install -d %{buildroot}%{python3_sitearch}/%{srcname}
install -pm 0644 %{srcname}/__init__.py %{buildroot}%{python3_sitearch}/%{srcname}/
install -pm 0755 %{srcname}/_%{srcname}.so %{buildroot}%{python3_sitearch}/%{srcname}/

%files
%{python3_sitearch}/%{srcname}/

%changelog
%autochangelog
