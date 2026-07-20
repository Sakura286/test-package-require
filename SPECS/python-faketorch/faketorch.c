/*
 * SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
 * SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
 * SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
 *
 * SPDX-License-Identifier: MulanPSL-2.0
 *
 * Dependency-resolution test stand-in for libtorch.so.
 *
 * Nothing here is meant to compute anything.  The only thing that matters is
 * that a real ELF shared object with SONAME "libfaketorch.so" ends up in the
 * buildroot, so that RPM's ELF dependency generator emits a real
 * "libfaketorch.so()(64bit)" provide -- which is exactly the mechanism that
 * python-torch.spec:17-22 suppresses for libtorch/libc10.
 *
 * backend_id() lets an installed system report which flavor actually won the
 * dependency resolution, without needing a GPU or anything else.
 */

int faketorch_backend_id(void)
{
#ifdef FAKETORCH_ROCM
	return 1;
#else
	return 0;
#endif
}
