# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

# Stand-in for: rocm-specs/SPECS/python-torch/python-torch.spec
#
# Same multibuild flavor split (cpu / rocm), same two-way Conflicts, same
# provides-filtering knobs -- but it builds in seconds instead of hours, so the
# dependency-resolution questions can be answered without a torch build.
#
# Deliberate deviation from the real spec: libfaketorch.so is installed into
# %%{_libdir} rather than %%{python3_sitearch}/faketorch/lib.  Only the *path*
# differs; the mechanism under test (a __provides_exclude_from regex applied to
# a shipped .so) is identical, and %%{_libdir} makes the consumer packages link
# and dlopen without rpath games.

%global srcname faketorch

# The default flavor builds a "CPU-only" faketorch; _multibuild adds "rocm".
%global flavor @BUILD_FLAVOR@%{nil}
%if "%{flavor}" == "rocm"
%bcond rocm 1
%else
%bcond rocm 0
%endif

### The two variables under test ###############################################
#
# P2 -- treat libfaketorch.so as a private library, i.e. suppress its soname
# provide.  Mirrors python-torch.spec:17-22 (torch_privlibs).  Build with
# --without privlibs to re-expose it, which is what Fedora and openRuyi Base do.
%bcond privlibs 1
#
# P1 -- drop the auto-generated python3dist(faketorch) from the rocm flavor, so
# the generic torch identity resolves to CPU.  Mirrors python-torch.spec:195.
# Build with --without distexclude to let both flavors carry the identity
# (the Arch/Debian model).
%bcond distexclude 1
#
################################################################################

%if %{with privlibs}
%global __provides_exclude_from ^%{_libdir}/libfaketorch\\.so$
%global __requires_exclude ^libfaketorch\\.so
%endif

%if %{with rocm}
Name:           python-%{srcname}-rocm
%else
Name:           python-%{srcname}
%endif
Version:        2.13.0
Release:        %autorelease
Summary:        Dependency-resolution test stand-in for python-torch
License:        MulanPSL-2.0
URL:            https://github.com/Sakura286/test-package-require

Source0:        faketorch.c
Source1:        pyproject.toml
Source2:        __init__.py

BuildRequires:  gcc
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros
# No %%generate_buildrequires here, so the PEP 517 backend must be named.
BuildRequires:  python3dist(setuptools)

%if %{with rocm}
%if %{with distexclude}
%global __provides_exclude ^python3(\\.[0-9]+)?dist\\(%{srcname}\\)
%endif
Provides:       %{srcname}-rocm = %{version}-%{release}
Conflicts:      python-%{srcname}
%else
Provides:       %{srcname} = %{version}-%{release}
Conflicts:      python-%{srcname}-rocm
%endif

%description
Test stand-in for python-torch, used to answer dependency-resolution questions
about the CPU/ROCm flavor split without paying for a real torch build.

This is the %{?with_rocm:rocm}%{!?with_rocm:cpu} flavor.  It carries the same
dependency metadata as the real thing and no useful functionality whatsoever.

%prep
rm -rf %{srcname}
mkdir -p %{srcname}
cp -p %{SOURCE0} .
cp -p %{SOURCE1} .
cp -p %{SOURCE2} %{srcname}/__init__.py

%build
gcc %{build_cflags} %{build_ldflags} -shared -fPIC \
    %{?with_rocm:-DFAKETORCH_ROCM} \
    -Wl,-soname,libfaketorch.so \
    -o libfaketorch.so %{SOURCE0}
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files %{srcname}
install -Dpm 0755 libfaketorch.so %{buildroot}%{_libdir}/libfaketorch.so

%check
%pyproject_check_import

%files -f %{pyproject_files}
%{_libdir}/libfaketorch.so

%changelog
%autochangelog
