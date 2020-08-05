# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
from pathlib import Path

from pydefect.cli.vasp.recommend_interstitials import \
    interstitials_from_charge_density
from pymatgen.io.vasp import Chgcar, Locpot


def test_interstitials_from_charge_density():
    aeccar0 = Chgcar.from_file(str(Path(__file__).parent / "vasp_files" / "NaMgF3_AECCAR0"))
    aeccar2 = Chgcar.from_file(str(Path(__file__).parent / "vasp_files" / "NaMgF3_AECCAR2"))
    aeccar = aeccar0 + aeccar2
    aeccar.write_file("CHGCAR")
    interstitials_from_charge_density(aeccar)


def test_interstitials_from_potential():
    locpot = Locpot.from_file(str(Path(__file__).parent / "vasp_files" / "NaMgF3_LOCPOT"))
    interstitials_from_charge_density(locpot)

