# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0
"""Compiled torch consumer stand-in (torchvision / torchaudio)."""

import ctypes
import os

__version__ = "1.0.0"

_lib = ctypes.CDLL(os.path.join(os.path.dirname(__file__), "_fakeext.so"))


def backend():
    """Report the backend seen through the compiled extension's own link."""
    return "rocm" if _lib.fakeext_backend_id() else "cpu"
