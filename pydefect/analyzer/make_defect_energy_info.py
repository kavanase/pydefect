# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
from typing import Dict, Union

from pydefect.analyzer.band_edge_states import BandEdgeStates
from pydefect.analyzer.calc_results import CalcResults
from pydefect.analyzer.defect_energy import DefectEnergy, DefectEnergyInfo
from pydefect.corrections.abstract_correction import Correction
from pydefect.input_maker.defect_entry import DefectEntry
from pymatgen import Element, IStructure


def make_defect_energy_info(defect_entry: DefectEntry,
                            calc_results: CalcResults,
                            correction: Correction,
                            perfect_calc_results: CalcResults,
                            standard_energies: Dict[Element, float],
                            band_edge_states: BandEdgeStates = None
                            ) -> DefectEnergyInfo:
    atom_io = num_atom_differences(calc_results.structure,
                                   perfect_calc_results.structure)
    formation_energy = calc_results.energy - perfect_calc_results.energy
    for k, v in atom_io.items():
        formation_energy -= standard_energies[k] * v
    is_shallow = band_edge_states.is_shallow if band_edge_states else None
    energy = DefectEnergy(formation_energy=formation_energy,
                          energy_corrections=correction.correction_dict,
                          is_shallow=is_shallow)

    return DefectEnergyInfo(defect_entry.name, defect_entry.charge,
                            atom_io=atom_io, defect_energy=energy)


def num_atom_differences(structure: IStructure,
                         ref_structure: IStructure,
                         str_key: bool = False
                         ) -> Dict[Union[Element, str], int]:
    target_composition = structure.composition.as_dict()
    reference_composition = ref_structure.composition.as_dict()
    result = {}
    for k in set(target_composition.keys()) | set(reference_composition.keys()):
        n_atom_diff = int(target_composition[k] - reference_composition[k])
        if n_atom_diff:
            result[k if str_key else Element(k)] = n_atom_diff
    return result
