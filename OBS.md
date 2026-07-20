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

## Results (2026-07-20, home:Sakura286:test_package, x86_64)

Under **production semantics** (the spec's default bconds), `python-fakerocmapp`
is unresolvable in *both* repositories:

```
conflict for providers of python3.13dist(faketorch) >= 2 needed by python-fakepure,
(provider python-faketorch is in conflict with python-faketorch-rocm)
```

That is the build-time twin of the install-time failure — and note `Prefer:`
never gets a say, because with the identity stripped there is only one provider
to prefer. Switching the project to **identity semantics** turns everything
green and answers all three questions:

| | Question | Answer |
|---|---|---|
| **A1** | Does an ambiguous `BuildRequires` fail? | **No.** No `have choice` error; the expander silently follows `Prefer:`. |
| **A2** | Does `Prefer:` back off when it collides with `Conflicts`? | **Yes.** In `cpu_build`, where prjconf prefers the CPU flavor, `python-fakerocmapp` still got `python-faketorch-rocm` — an explicit-name `BuildRequires` wins, and the ambiguous transitive capability resolves to the flavor already in the build set. |
| **A3** | Does per-repository `Prefer:` select the flavor? | **Yes.** The name-free consumers got the CPU flavor in `cpu_build` and the ROCm flavor in `rocm_build`, with no spec change. |

A2 is the one that matters most: **proposal B works at build time.** The
expander does not blindly walk `Prefer:` into a conflict.

But A3's win does not survive packaging. The name-free `python-fakerocmapp`
built in `rocm_build` — against the ROCm flavor — ships:

```
Requires: python-fakepure
Requires: python3dist(faketorch)
```

Nothing records which flavor it was built against, and the install-time matrix
shows that requirement resolving to the **CPU** flavor. Build-time selection is
solvable without naming packages; install-time selection is not.

## Current project state

The project is left in identity semantics with the name-free variant selected:

```
Macros:
%_without_distexclude 1
%_without_byname 1
:Macros
```

Comment either line out and `osc rebuild --all` to move around the matrix.
A prjconf edit alone does not always retrigger — check that the release number
moved before trusting a result.

Note what the install-time matrix already showed: even if A3 works, the
resulting RPM still resolves to the **CPU** flavor at install time
(`full: rocmapp (name-free) → cpu`). Build-time and install-time selection are
separate problems and A3 only solves the first.
