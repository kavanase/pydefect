# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
import shutil

import fire
from monty.serialization import loadfn
from pydefect.analyzer.defect_structure_symmetrizer import \
    symmetrize_defect_structure
from pydefect.defaults import defaults as p_defaults
from vise.defaults import defaults as v_defaults
from pydefect.input_maker.defect_entry import DefectEntry
from pymatgen.core import Structure
from vise.util.logger import get_logger
from vise.util.structure_symmetrizer import StructureSymmetrizer

logger = get_logger(__name__)


def make_refined_structure():
    defect_entry: DefectEntry = loadfn("defect_entry.json")
    structure = Structure.from_file(v_defaults.contcar)
    symmetrizer = StructureSymmetrizer(structure,
                                       p_defaults.symmetry_length_tolerance,
                                       p_defaults.symmetry_angle_tolerance)
    if symmetrizer.point_group == "1":
        logger.info("The point group is 1, so the symmetry is not refined.")
        return

    shutil.move(v_defaults.contcar, str(v_defaults.contcar) + ".sym_1")
    shutil.move(v_defaults.outcar, str(v_defaults.outcar) + ".sym_1")
    shutil.move(v_defaults.vasprun, str(v_defaults.vasprun) + ".sym_1")

    refined_structure = symmetrize_defect_structure(
        symmetrizer,
        defect_entry.anchor_atom_index,
        defect_entry.anchor_atom_coords)

    logger.info(f"The point group is {symmetrizer.point_group}, "
                f"so the symmetry is refined and POSCAR is being created.")
    refined_structure.to(fmt="POSCAR", filename="POSCAR")


if __name__ == '__main__':
    fire.Fire(make_refined_structure)
