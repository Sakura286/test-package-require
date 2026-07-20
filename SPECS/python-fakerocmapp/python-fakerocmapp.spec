# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

# Stand-in for: rocm-specs/SPECS/python-vllm (rocm flavor).
#
# This is the package that carries test A2, the pivot of the whole question:
# it needs the ROCm flavor, AND it pulls in python-fakepure, which requires the
# ambiguous python3dist(faketorch).  With prjconf "Prefer: python-faketorch",
# does OBS resolve fakepure's requirement to the CPU flavor and then report
# unresolvable on the Conflicts -- or does it back off and reuse the ROCm
# flavor already in the build set?

%global srcname fakerocmapp

# How this package asks for the ROCm backend:
#   --with byname     (default) explicit "BuildRequires: python-faketorch-rocm",
#                     what rocm-specs/SPECS/python-vllm.spec:79,137 does today,
#                     but against openRuyi's name-free convention.
#   --without byname  name-free: only python3dist(faketorch), with the flavor
#                     chosen by the repository's prjconf "Prefer:".
%bcond byname 1

Name:           python-%{srcname}
Version:        1.0.0
Release:        %autorelease
Summary:        ROCm-side application stand-in
License:        MulanPSL-2.0
URL:            https://github.com/Sakura286/test-package-require
BuildArch:      noarch

Source0:        __init__.py

BuildRequires:  python3-devel
# The transitive route to the ambiguous capability.
BuildRequires:  python-fakepure
%if %{with byname}
BuildRequires:  python-faketorch-rocm
%else
BuildRequires:  python3dist(faketorch)
%endif

Requires:       python-fakepure
%if %{with byname}
Requires:       python-faketorch-rocm
%else
Requires:       python3dist(faketorch)
%endif

%description
Test stand-in for a ROCm-only application that also depends on a generic
Base-style torch consumer.  Used to test whether the build- and install-time
solvers can hold "this one must be the ROCm flavor" and "this one just needs
some torch" at the same time.

%prep
rm -rf %{srcname}
mkdir -p %{srcname}
cp -p %{SOURCE0} %{srcname}/__init__.py

%build

%install
install -d %{buildroot}%{python3_sitelib}/%{srcname}
install -pm 0644 %{srcname}/__init__.py %{buildroot}%{python3_sitelib}/%{srcname}/

%files
%{python3_sitelib}/%{srcname}/

%changelog
%autochangelog
