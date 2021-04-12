# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.
from pydefect.analyzer.calc_results import CalcResults
from pydefect.defaults import defaults
from pymatgen.io.vasp import Vasprun, Outcar

from vise.util.structure_symmetrizer import StructureSymmetrizer
from vise.defaults import defaults as v_defaults


def make_calc_results_from_vasp(vasprun: Vasprun,
                                outcar: Outcar) -> CalcResults:
    magnetization = outcar.total_mag or 0.0
    symmetrizer = StructureSymmetrizer(
        vasprun.final_structure,
        symprec=defaults.symmetry_length_tolerance,
        angle_tolerance=defaults.symmetry_angle_tolerance,
        time_reversal=abs(magnetization) > v_defaults.integer_criterion)

    return CalcResults(structure=vasprun.final_structure,
                       site_symmetry=symmetrizer.point_group,
                       energy=outcar.final_energy,
                       magnetization=magnetization,
                       potentials=[-p for p in outcar.electrostatic_potential],
                       fermi_level=vasprun.efermi,
                       electronic_conv=vasprun.converged_electronic,
                       ionic_conv=vasprun.converged_ionic)
