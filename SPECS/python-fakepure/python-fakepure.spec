# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

# Stand-in for: openRuyi Base pure-Python torch consumers
# (python-accelerate, python-timm, python-scikit-learn, ...).
#
# It writes NO package name anywhere -- the only torch reference is the
# python3dist(faketorch) that %%pyproject_buildrequires and the automatic
# dependency generator derive from pyproject.toml.  That is exactly the
# constraint openRuyi imposes, and it is what makes the flavor choice
# unexpressible in the spec.  Test A1 lives here.

%global srcname fakepure

Name:           python-%{srcname}
Version:        1.0.0
Release:        %autorelease
Summary:        Pure-Python torch consumer stand-in
License:        MulanPSL-2.0
URL:            https://github.com/Sakura286/test-package-require
BuildArch:      noarch

Source0:        pyproject.toml
Source1:        __init__.py

BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros

%description
Test stand-in for a Base package that requires torch through
python3dist(torch) only, and is thin enough not to care which backend
answers.  Used to test identity resolution (P1).

%prep
rm -rf %{srcname}
mkdir -p %{srcname}
cp -p %{SOURCE0} .
cp -p %{SOURCE1} %{srcname}/__init__.py

%generate_buildrequires
# No -R: runtime deps become BuildRequires too, so the build-time resolution of
# python3dist(faketorch) is exercised as well as the install-time one.
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files %{srcname}

%check
%pyproject_check_import

%files -f %{pyproject_files}

%changelog
%autochangelog
