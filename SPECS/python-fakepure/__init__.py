# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: CHEN Xuan <chenxuan@iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0
"""Pure-Python torch consumer stand-in (accelerate / timm / scikit-learn).

Imports faketorch but touches no compiled symbol of it, so it genuinely does
not care which backend flavor is installed -- the premise behind the shim.
"""

import faketorch

__version__ = "1.0.0"


def which_backend():
    return faketorch.backend()
