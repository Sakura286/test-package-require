# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0
"""Dependency-resolution test stand-in for torch."""

import ctypes

__version__ = "2.13.0"


def backend():
    """Return "cpu" or "rocm" -- which flavor's libfaketorch.so is installed.

    The point of this is to answer "which flavor did the solver actually pick?"
    on a live system, in one line, without a GPU.
    """
    lib = ctypes.CDLL("libfaketorch.so")
    return "rocm" if lib.faketorch_backend_id() else "cpu"
