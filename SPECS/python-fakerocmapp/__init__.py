# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0
"""ROCm-side application stand-in (vllm-rocm)."""

import fakepure

__version__ = "1.0.0"


def report():
    """Assert the whole chain ended up on one backend."""
    return fakepure.which_backend()
