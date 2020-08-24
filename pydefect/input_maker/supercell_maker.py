# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.

from typing import Optional, List

import numpy as np
from pydefect.input_maker.supercell import Supercell, TetragonalSupercells, \
    Supercells
from pydefect.input_maker.supercell_info import SupercellInfo
from pydefect.util.error_classes import NotPrimitiveError, SupercellError
from pymatgen import IStructure
from vise.util.centering import Centering
from vise.util.logger import get_logger
from vise.util.structure_symmetrizer import StructureSymmetrizer, create_sites

logger = get_logger(__name__)


class SupercellMaker:
    def __init__(self,
                 input_structure: IStructure,
                 matrix: Optional[List[List[int]]] = None,
                 **supercell_kwargs):

        symmetrizer = StructureSymmetrizer(input_structure)
        if input_structure.lattice != symmetrizer.primitive.lattice:
            logger.warning(
                f"Input structure: {input_structure}",
                f"Primitive structure:{symmetrizer.primitive}")
            raise NotPrimitiveError

        self.sg = symmetrizer.sg_number
        self.sg_symbol = symmetrizer.spglib_sym_data["international"]
        self.conv_structure = symmetrizer.conventional
        crystal_system, center = str(symmetrizer.bravais)

        centering = Centering(center)
        self.conv_multiplicity = centering.conv_multiplicity
        self.conv_trans_mat = centering.primitive_to_conv

        self._matrix = matrix
        self._supercell_kwargs = supercell_kwargs

        self._generate_supercell(crystal_system)
        self._generate_supercell_info()

    def _generate_supercell(self, crystal_system):
        if self._matrix:
            self.supercell = Supercell(self.conv_structure, self._matrix)
        else:
            if crystal_system == "t":
                supercells = TetragonalSupercells(self.conv_structure,
                                                  **self._supercell_kwargs)
            else:
                supercells = Supercells(self.conv_structure,
                                        **self._supercell_kwargs)

            self.supercell = supercells.most_isotropic_supercell

    def _generate_supercell_info(self):
        symmetrizer = StructureSymmetrizer(self.supercell.structure)
        if symmetrizer.sg_number != self.sg:
            raise SupercellError

        sites = create_sites(symmetrizer)

        self.supercell_info = SupercellInfo(self.supercell.structure,
                                            self.sg_symbol,
                                            self.transformation_matrix,
                                            sites)

    @property
    def transformation_matrix(self):
        matrix = np.dot(self.conv_trans_mat, self.supercell.matrix).astype(int)
        return matrix.tolist()

