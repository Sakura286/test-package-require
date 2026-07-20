/*
 * SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
 * SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
 * SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
 *
 * SPDX-License-Identifier: MulanPSL-2.0
 *
 * Stand-in for torchvision's compiled operator .so.  It links against
 * libfaketorch so that RPM's ELF dependency generator emits an automatic
 * "Requires: libfaketorch.so()(64bit)" -- the requirement that Base's
 * python-torchvision carries and that rocm-specs' torch cannot satisfy.
 */

extern int faketorch_backend_id(void);

int fakeext_backend_id(void)
{
	return faketorch_backend_id();
}
