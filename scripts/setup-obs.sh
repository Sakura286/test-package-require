#!/bin/bash
# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0
#
# Create/refresh the OBS side of the test rig.  Idempotent: safe to re-run after
# changing prjconf or a _service.
#
# Push the git repo first -- the _service files pull the specs from GitHub, so
# OBS builds whatever is on the "main" branch, not what is in your working tree.

set -euo pipefail

PROJECT="${PROJECT:-home:Sakura286:test_package}"
HERE="$(cd "$(dirname "$0")/.." && pwd)"
WORK="${WORK:-$HERE/../tmp/obs-test_package}"

echo "== project meta and prjconf =="
osc meta prj "$PROJECT" -F "$HERE/OBS/project-meta.xml"
osc meta prjconf "$PROJECT" -F "$HERE/OBS/prjconf"

mkdir -p "$WORK"
cd "$WORK"
[ -d .osc ] || osc checkout "$PROJECT" -o . 2>/dev/null || osc init "$PROJECT"

for pkg in python-faketorch python-fakepure python-fakeext python-fakerocmapp; do
	echo "== $pkg =="
	[ -d "$pkg" ] || osc mkpac "$pkg"
	cp "$HERE/OBS/$pkg"/_* "$pkg/"
	(cd "$pkg" && osc add _* 2>/dev/null || true; osc ci -m "$pkg: sync OBS metadata")
done

echo
echo "Watch with:  osc results $PROJECT"
