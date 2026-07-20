<!--
SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>

SPDX-License-Identifier: MulanPSL-2.0
-->

# test-package-require

A minimal test rig for the openRuyi ROCm stack's dependency-resolution
questions. It answers in seconds what a real `python-torch` / `python-vllm`
build answers in hours.

Nothing here computes anything. Every package exists only to carry the same
*dependency metadata* as the real package it stands in for, produced by the
same RPM generators — not hand-written `Provides:` lines, which would only test
the string we typed.

## The two problems under test

| | Problem | Mechanism |
|---|---|---|
| **P1** | Which flavor owns the generic torch identity? | `__provides_exclude` on `python3dist(...)` |
| **P2** | Compiled consumers can't resolve their soname | `__provides_exclude_from` on the shipped `.so` |

They are independent, and the rig shows that fixing one does not fix the other.

## The packages

| Package | Stands in for |
|---|---|
| `python-faketorch` | `python-torch` (same `@BUILD_FLAVOR@` cpu/rocm multibuild, same two-way `Conflicts`) |
| `python-fakepure` | Base pure-Python consumers: `python-accelerate`, `python-timm`, `python-scikit-learn` |
| `python-fakeext` | Base compiled consumers: `python-torchvision`, `python-torchaudio` |
| `python-fakerocmapp` | `python-vllm` (rocm flavor) |

`python-faketorch` puts both problems behind bconds, so one spec covers the
whole matrix without edits:

```
--without privlibs     expose libfaketorch.so()(64bit)      (undo P2)
--without distexclude  let the rocm flavor keep the identity (undo P1)
```

Three variants get built from those:

- **prod** — what `rocm-specs` ships today (both exclusions on)
- **identity** — proposal B: both flavors carry `python3dist(faketorch)`
- **full** — proposal B plus the P2 fix

## Running it

On any openRuyi box (the x86 QEMU VM is fine):

```sh
scripts/build-local.sh      # builds every variant into ~/rpmrepo/*, ~15 s
scripts/resolve-matrix.sh   # dry-run dnf resolution matrix, ~10 s
```

`resolve-matrix.sh` never installs anything — every scenario is
`dnf install --assumeno`.

## Results (2026-07-20, x86_64 openRuyi, dnf5 / rpm 6.0.1)

```
scenario                           verdict     detail
-------------------------------------------------------------------------
prod: fakepure alone               RESOLVED    cpu
prod: rocm + fakepure              UNRESOLVED  requires python3.13dist(faketorch) >= 2
prod: rocm + fakeext               UNRESOLVED
identity: fakepure alone           RESOLVED    cpu
identity: rocm + fakepure          RESOLVED    rocm
identity: rocm + fakeext           UNRESOLVED
full: fakepure alone               RESOLVED    cpu
full: rocm + fakepure              RESOLVED    rocm
full: rocm + fakeext               RESOLVED    rocm
full: rocmapp (by name)            RESOLVED    rocm
full: rocmapp (name-free)          RESOLVED    cpu
```

What that says:

1. **`prod: rocm + fakepure` UNRESOLVED** reproduces the production pain in
   miniature — the reason `python-torch-rocm-shim` exists.
2. **`identity: rocm + fakepure` RESOLVED as rocm** — once both flavors carry
   the identity, libsolv reuses the flavor already pinned in the transaction.
   No shim needed. Proposal B works at install time.
3. **`identity: rocm + fakeext` still UNRESOLVED** — P1 and P2 really are
   independent. Restoring the identity does nothing for torchvision.
4. **`full: rocm + fakeext` RESOLVED** — only re-exposing the sonames fixes the
   compiled consumers.
5. **`full: rocmapp (name-free)` RESOLVED as cpu** — the one that should worry
   us. A ROCm application that may only write `python3dist(faketorch)` gets the
   **CPU** backend, silently, with no error. Install-time flavor selection is
   simply not expressible under a name-free convention; it can only be shifted,
   never stated.

## Still open (needs OBS)

The build-time half — how the OBS expander behaves with `Prefer:` and
`Conflicts` — cannot be answered locally. See `OBS.md`.
