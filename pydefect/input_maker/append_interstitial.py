# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
from copy import copy
from typing import List, Union

import numpy as np
from numpy.linalg import inv
from pydefect.input_maker.supercell_info import SupercellInfo, Interstitial
from pydefect.util.error_classes import NotPrimitiveError
from pymatgen.core import Structure, Element
from vise.util.structure_symmetrizer import StructureSymmetrizer


def append_interstitial(supercell_info: SupercellInfo,
                        unitcell_structure: Structure,
                        frac_coords: Union[List[List[float]]],
                        infos: List[str]
                        ) -> SupercellInfo:
    """
    inv_trans_mat must be multiplied with coords from the right as the
    trans_mat is multiplied to the unitcell lattice vector from the left.
    see __mul__ of IStructure in pymatgen.
    x_u, x_s means the frac coordinates in unitcell and supercell,
    while a, b, c are the unitcell lattice vector.
    (a_u, b_u, c_u) . (a, b, c) = (a_s, b_s, c_s) . trans_mat . (a, b, c)
    (a_u, b_u, c_u) = (a_s, b_s, c_s) . trans_mat
    so, (a_s, b_s, c_s) = (a_u, b_u, c_u) . inv_trans_ma
    """
    if supercell_info.unitcell_structure and \
            supercell_info.unitcell_structure != unitcell_structure:
        raise NotPrimitiveError

    if isinstance(frac_coords[0], float):
        frac_coords = [frac_coords]

    for fcoord, info in zip(frac_coords, infos):
        us = copy(unitcell_structure)
        us.append(species=Element.H, coords=fcoord)
        symmetrizer = StructureSymmetrizer(unitcell_structure)
        wyckoff_letter = (symmetrizer.spglib_sym_data["wyckoffs"][-1])
        site_symmetry = (symmetrizer.spglib_sym_data["site_symmetry_symbols"][-1])

        inv_matrix = inv(np.array(supercell_info.transformation_matrix))
        new_coords = np.dot(fcoord, inv_matrix).tolist()

        supercell_info.interstitials.append(
            Interstitial(frac_coords=new_coords, wyckoff_letter=wyckoff_letter,
                         site_symmetry=site_symmetry, info=info))
    return supercell_info