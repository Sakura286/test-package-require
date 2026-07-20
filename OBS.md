<!--
SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>

SPDX-License-Identifier: MulanPSL-2.0
-->

# The build-time half

`scripts/resolve-matrix.sh` answers what **libsolv** does at install time.
It cannot answer what the **OBS expander** does at build time — a separate
implementation with its own rules, and the only one that understands `Prefer:`.

## Setup

```sh
git push                    # OBS pulls specs from GitHub, not your worktree
scripts/setup-obs.sh
osc results home:Sakura286:test_package
```

Two repositories are created over the same target, differing only in prjconf:

```
%if "%_repository" == "rocm_build"
Prefer: python-faketorch-rocm
%else
Prefer: python-faketorch
%endif
```

## The questions

**A1 — does an ambiguous `BuildRequires` resolve or fail?**
`python-fakepure` build-requires `python3dist(faketorch) >= 2` and nothing else.
Build it in the `identity` state (both flavors provide the capability) and see
whether OBS reports `have choice for python3dist(faketorch)` or silently follows
`Prefer:`.

**A2 — does `Prefer:` back off when it collides with `Conflicts`?**
This is the pivot. `python-fakerocmapp` build-requires `python-faketorch-rocm`
*and* `python-fakepure`, and fakepure drags in the ambiguous
`python3.13dist(faketorch)`. With `Prefer: python-faketorch` in force, the
preferred provider conflicts with a package already in the build set.

- If OBS backs off and reuses the rocm flavor → proposal B works at build time
  too, and `Prefer:` is a safe global default.
- If OBS reports unresolvable → the flavor cannot be pinned per package, and
  per-repository prjconf (below) is the only route.

**A3 — does per-repository `Prefer:` actually select the flavor?**
Build `python-fakerocmapp --without byname` (it names no package, only
`python3dist(faketorch)` — fully compliant with openRuyi's convention) in both
repositories. If `cpu_build` gives it the CPU flavor and `rocm_build` gives it
the ROCm flavor, then the build context can carry the choice that the spec is
not allowed to state.

Note what the install-time matrix already showed: even if A3 works, the
resulting RPM still resolves to the **CPU** flavor at install time
(`full: rocmapp (name-free) → cpu`). Build-time and install-time selection are
separate problems and A3 only solves the first.
