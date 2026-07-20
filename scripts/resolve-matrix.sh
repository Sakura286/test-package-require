#!/bin/bash
# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0
#
# Install-time (libsolv) resolution matrix for the faketorch test rig.
#
# Every scenario is a dry run -- dnf resolves and then aborts, so nothing is
# ever installed and the whole matrix takes seconds.  For each scenario we
# report whether the transaction resolved and, if it did, which faketorch
# flavor libsolv picked.
#
# Run scripts/build-local.sh first.

set -uo pipefail

run() {
	local label="$1" repos="$2"
	shift 2
	local args=()
	for r in $repos; do args+=(--enable-repo="faketorch-$r"); done

	local out
	out=$(sudo dnf install --assumeno "${args[@]}" "$@" 2>&1)

	local verdict flavor=""
	if grep -q "Transaction Summary" <<<"$out"; then
		verdict="RESOLVED"
		if grep -qE '^ python-faketorch-rocm ' <<<"$out"; then
			flavor="rocm"
		elif grep -qE '^ python-faketorch ' <<<"$out"; then
			flavor="cpu"
		else
			flavor="(none pulled)"
		fi
	else
		verdict="UNRESOLVED"
		flavor=$(grep -oE 'requires [^,]+, but none of the providers' <<<"$out" |
			head -1 | sed 's/, but none of the providers//')
	fi
	printf '%-34s %-11s %s\n' "$label" "$verdict" "$flavor"
	[ -n "${VERBOSE:-}" ] && sed 's/^/      | /' <<<"$out"
	return 0
}

echo "scenario                           verdict     detail"
echo "-------------------------------------------------------------------------"

# --- prod: what rocm-specs ships today ------------------------------------
run "prod: fakepure alone"          "prod common" python-fakepure
run "prod: rocm + fakepure"         "prod common" python-faketorch-rocm python-fakepure
run "prod: rocm + fakeext"          "prod common" python-faketorch-rocm python-fakeext

# --- identity: both flavors carry python3dist(faketorch) (proposal B) -----
run "identity: fakepure alone"      "identity common" python-fakepure
run "identity: rocm + fakepure"     "identity common" python-faketorch-rocm python-fakepure
run "identity: rocm + fakeext"      "identity common" python-faketorch-rocm python-fakeext

# --- full: proposal B plus the soname fix ---------------------------------
run "full: fakepure alone"          "full common" python-fakepure
run "full: rocm + fakepure"         "full common" python-fakepure python-faketorch-rocm
run "full: rocm + fakeext"          "full common" python-faketorch-rocm python-fakeext
run "full: rocmapp (by name)"       "full common" python-fakerocmapp
run "full: rocmapp (name-free)"     "full common-nameless" python-fakerocmapp

echo
echo "Set VERBOSE=1 to dump each dnf transcript."
