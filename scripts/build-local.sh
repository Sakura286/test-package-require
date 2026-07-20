#!/bin/bash
# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0
#
# Build the whole test rig on an openRuyi box (the QEMU VM is fine) into a set
# of local dnf repositories, one per "semantics variant" of python-faketorch.
#
#   common/    the consumers -- their metadata does not depend on any faketorch
#              bcond, so they are built once and reused by every variant
#   prod/      what rocm-specs ships today: soname suppressed, rocm flavor
#              stripped of python3dist(faketorch)
#   identity/  proposal B: both flavors carry python3dist(faketorch)
#   full/      proposal B + the P2 fix: identity AND soname exposed
#
# Usage:  scripts/build-local.sh [SPECS_DIR]
# Then:   scripts/resolve-matrix.sh

set -euo pipefail

SPECS_DIR="${1:-$(cd "$(dirname "$0")/../SPECS" && pwd)}"
REPO_ROOT="${REPO_ROOT:-$HOME/rpmrepo}"

# rpmautospec does not run outside dist-git; pin the release locally so the NVRs
# stay stable and comparable across variants.
COMMON_DEFS=(-D "autorelease 1" -D "autochangelog %nil")

build() {
	local pkg="$1" outdir="$2"
	shift 2
	local specdir="$SPECS_DIR/$pkg"
	mkdir -p "$outdir"
	rpmbuild -bb "${COMMON_DEFS[@]}" \
		-D "_sourcedir $specdir" \
		-D "_rpmdir $outdir" \
		"$@" "$specdir/$pkg.spec" >"$outdir/$pkg.build.log" 2>&1 || {
		echo "FAILED: $pkg $* -- see $outdir/$pkg.build.log" >&2
		tail -20 "$outdir/$pkg.build.log" >&2
		return 1
	}
	echo "  built $pkg $*"
}

publish() {
	local dir="$1" name="$2"
	find "$dir" -name '*.rpm' -exec mv -t "$dir" {} + 2>/dev/null || true
	find "$dir" -mindepth 1 -type d -exec rm -rf {} + 2>/dev/null || true
	createrepo_c --quiet --update "$dir"
	sudo tee "/etc/yum.repos.d/faketorch-$name.repo" >/dev/null <<-EOF
		[faketorch-$name]
		name=faketorch test rig ($name)
		baseurl=file://$dir
		enabled=0
		gpgcheck=0
	EOF
	echo "  repo faketorch-$name -> $dir (disabled by default)"
}

echo "== faketorch variants =="
echo "-- prod: soname suppressed, rocm identity stripped"
build python-faketorch "$REPO_ROOT/prod"
build python-faketorch "$REPO_ROOT/prod" --with rocm
publish "$REPO_ROOT/prod" prod

echo "-- identity: both flavors provide python3dist(faketorch)"
build python-faketorch "$REPO_ROOT/identity"
build python-faketorch "$REPO_ROOT/identity" --with rocm --without distexclude
publish "$REPO_ROOT/identity" identity

echo "-- full: identity + soname exposed"
build python-faketorch "$REPO_ROOT/full" --without privlibs
build python-faketorch "$REPO_ROOT/full" --with rocm --without privlibs --without distexclude
publish "$REPO_ROOT/full" full

# The consumers need *a* faketorch installed to build: fakepure resolves
# python3dist(faketorch) in %generate_buildrequires, fakeext links -lfaketorch.
# The "full" CPU flavor is the only one that satisfies both, and the consumers'
# own metadata does not depend on which variant they were built against.
echo "== installing full/cpu faketorch as the consumers' build dependency =="
sudo dnf install -y "$REPO_ROOT/full"/python-faketorch-[0-9]*.rpm

echo "== consumers (variant-independent) =="
build python-fakepure     "$REPO_ROOT/common"
build python-fakeext      "$REPO_ROOT/common"
# --nodeps: fakerocmapp's BuildRequires are there to be chewed on by the OBS
# expander (test A2), not to be satisfied locally -- "needs the rocm flavor" and
# "was built against the cpu flavor" cannot both hold in one VM.  It compiles
# nothing, so skipping them locally costs nothing.
build python-fakerocmapp  "$REPO_ROOT/common" --nodeps
build python-fakerocmapp  "$REPO_ROOT/common-nameless" --nodeps --without byname
# The two fakerocmapp builds share an NVR, so they must never be visible to the
# same transaction.  Keep them in separate repos and give each repo its own copy
# of the other consumers, rather than enabling both at once.
find "$REPO_ROOT/common" -name 'python-fake[pe]*.rpm' -exec cp -t "$REPO_ROOT/common-nameless" {} +
publish "$REPO_ROOT/common" common
publish "$REPO_ROOT/common-nameless" common-nameless

echo
echo "Done. Run scripts/resolve-matrix.sh next."
