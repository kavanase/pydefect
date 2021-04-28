# -*- coding: utf-8 -*-

import os
import sys
from math import sqrt
from pathlib import Path

import pytest
from pydefect.corrections.efnv_correction import PotentialSite, \
    ExtendedFnvCorrection
from pydefect.defaults import defaults
from pydefect.input_maker.local_extrema import VolumetricDataAnalyzeParams
from pydefect.input_maker.supercell_info import Site, SupercellInfo, \
    Interstitial
from pymatgen.core import Lattice, IStructure, Structure

sys.path.append(os.path.join(os.path.dirname(__file__), 'helpers'))
# Need the following the share the fixture


@pytest.fixture(scope="session")
def vasp_files():
    return Path(__file__).parent / "cli" / "vasp" / "vasp_files"


@pytest.fixture(scope="session")
def simple_cubic():
    lattice = Lattice.cubic(1.0)
    coords = [[0.0, 0.0, 0.0]]
    return IStructure(lattice=lattice, species=["H"], coords=coords)


@pytest.fixture(scope="session")
def simple_cubic_2x1x1():
    lattice = Lattice.orthorhombic(2.0, 1.0, 1.0)
    coords = [[0.0, 0.0, 0.0], [0.5, 0.0, 0.0]]
    return IStructure(lattice=lattice, species=["H", "H"], coords=coords)


@pytest.fixture(scope="session")
def simple_cubic_2x2x2():
    lattice = Lattice.cubic(2.0)
    coords = [[0.0, 0.0, 0.0],
              [0.5, 0.5, 0.0],
              [0.5, 0.0, 0.5],
              [0.0, 0.5, 0.5],
              [0.0, 0.0, 0.5],
              [0.0, 0.5, 0.0],
              [0.5, 0.0, 0.0],
              [0.5, 0.5, 0.5]]
    return IStructure(lattice=lattice, species=["H"] * 8, coords=coords)


@pytest.fixture(scope="session")
def monoclinic():
    lattice = Lattice.monoclinic(3, 4, 5, 100)
    coords = [[0.0, 0.0, 0.0]]
    return IStructure(lattice=lattice, species=["H"], coords=coords)


@pytest.fixture(scope="session")
def complex_monoclinic():
    lattice = Lattice.monoclinic(3, 4, 5, 100)
    coords = [[0.0, 0.0, 0.0],
              [0.1, 0.0, 0.0],
              [0.9, 0.0, 0.0],
              [0.2, 0.0, 0.0],
              [0.8, 0.0, 0.0]]
    return IStructure(lattice=lattice,
                      species=["H", "He", "He", "He", "He"],
                      coords=coords)


@pytest.fixture(scope="session")
def rhombohedral():
    lattice = Lattice.rhombohedral(a=1, alpha=45)
    coords = [[0.0, 0.0, 0.0]]
    return IStructure(lattice=lattice, species=["H"], coords=coords)


@pytest.fixture(scope="session")
def elongated_tetragonal():
    lattice = Lattice.tetragonal(a=1, c=3 * sqrt(2))
    coords = [[0.0, 0.0, 0.0]]
    return IStructure(lattice=lattice, species=["H"], coords=coords)


@pytest.fixture(scope="session")
def elongated_tetragonal():
    lattice = Lattice.tetragonal(a=1, c=3 * sqrt(2))
    coords = [[0.0, 0.0, 0.0]]
    return IStructure(lattice=lattice, species=["H"], coords=coords)


@pytest.fixture(scope="session")
def a_centered_orthorhombic():
    lattice = Lattice([[1,  0, 0],
                       [0,  2, 3],
                       [0, -2, 3]])
    coords = [[0.5, 0.8, 0.8],
              [0.0, 0.3, 0.0],
              [0.0, 0.0, 0.3]]

    return IStructure(lattice=lattice, species=["H"] * 3, coords=coords)


@pytest.fixture(scope="session")
def c_centered_monoclinic():
    lattice = Lattice.monoclinic(3, 4, 5, 100)
    coords = [[0.0, 0.0, 0.0], [0.5, 0.5, 0.0]]
    return IStructure(lattice=lattice, species=["H", "H"], coords=coords)


@pytest.fixture(scope="session")
def fcc():
    lattice = Lattice.cubic(1.0)
    coords = [[0.0, 0.0, 0.0], [0.5, 0.5, 0.0],
              [0.5, 0.0, 0.5], [0.0, 0.5, 0.5]]
    return IStructure(lattice=lattice, species=["H"] * 4, coords=coords)


@pytest.fixture(scope="session")
def bcc():
    lattice = Lattice.cubic(1.0)
    coords = [[0.0, 0.0, 0.0], [0.5, 0.5, 0.5]]
    return IStructure(lattice=lattice, species=["H"] * 2, coords=coords)


@pytest.fixture(scope="session")
def tetra_close_to_cubic():
    lattice = Lattice.tetragonal(1.001 * 10 / sqrt(2), 10)
    coords = [[0.0, 0.0, 0.0]]
    return IStructure(lattice=lattice, species=["H"], coords=coords)


@pytest.fixture(scope="session")
def ortho_conventional():
    lattice = Lattice.orthorhombic(5, 6, 7)
    coords = [
        [0.0, 0.0, 0.0],
        [0.5, 0.5, 0.0],
        [0.5, 0.0, 0.5],
        [0.0, 0.5, 0.5],

        [0.0, 0.0, 0.5],
        [0.0, 0.5, 0.0],
        [0.5, 0.0, 0.0],
        [0.5, 0.5, 0.5],
    ]
    return IStructure(lattice=lattice, species=["H"] * 4 + ["He"] * 4,
                      coords=coords)


@pytest.fixture(scope="session")
def cubic_supercell():
    lattice = Lattice.cubic(10)
    coords = [
       [0.00, 0.00, 0.00],
       [0.00, 0.00, 0.50],
       [0.00, 0.50, 0.00],
       [0.00, 0.50, 0.50],
       [0.50, 0.00, 0.00],
       [0.50, 0.00, 0.50],
       [0.50, 0.50, 0.00],
       [0.50, 0.50, 0.50],
       [0.00, 0.25, 0.25],
       [0.00, 0.25, 0.75],
       [0.00, 0.75, 0.25],
       [0.00, 0.75, 0.75],
       [0.50, 0.25, 0.25],
       [0.50, 0.25, 0.75],
       [0.50, 0.75, 0.25],
       [0.50, 0.75, 0.75],
       [0.25, 0.00, 0.25],
       [0.25, 0.00, 0.75],
       [0.25, 0.50, 0.25],
       [0.25, 0.50, 0.75],
       [0.75, 0.00, 0.25],
       [0.75, 0.00, 0.75],
       [0.75, 0.50, 0.25],
       [0.75, 0.50, 0.75],
       [0.25, 0.25, 0.00],
       [0.25, 0.25, 0.50],
       [0.25, 0.75, 0.00],
       [0.25, 0.75, 0.50],
       [0.75, 0.25, 0.00],
       [0.75, 0.25, 0.50],
       [0.75, 0.75, 0.00],
       [0.75, 0.75, 0.50],
       [0.25, 0.00, 0.00],
       [0.25, 0.00, 0.50],
       [0.25, 0.50, 0.00],
       [0.25, 0.50, 0.50],
       [0.75, 0.00, 0.00],
       [0.75, 0.00, 0.50],
       [0.75, 0.50, 0.00],
       [0.75, 0.50, 0.50],
       [0.25, 0.25, 0.25],
       [0.25, 0.25, 0.75],
       [0.25, 0.75, 0.25],
       [0.25, 0.75, 0.75],
       [0.75, 0.25, 0.25],
       [0.75, 0.25, 0.75],
       [0.75, 0.75, 0.25],
       [0.75, 0.75, 0.75],
       [0.00, 0.00, 0.25],
       [0.00, 0.00, 0.75],
       [0.00, 0.50, 0.25],
       [0.00, 0.50, 0.75],
       [0.50, 0.00, 0.25],
       [0.50, 0.00, 0.75],
       [0.50, 0.50, 0.25],
       [0.50, 0.50, 0.75],
       [0.00, 0.25, 0.00],
       [0.00, 0.25, 0.50],
       [0.00, 0.75, 0.00],
       [0.00, 0.75, 0.50],
       [0.50, 0.25, 0.00],
       [0.50, 0.25, 0.50],
       [0.50, 0.75, 0.00],
       [0.50, 0.75, 0.50],
    ]
    return Structure(lattice=lattice, species=["H"] * 32 + ["He"] * 32,
                     coords=coords)


@pytest.fixture(scope="session")
def cubic_supercell_w_vacancy(cubic_supercell):
    result = cubic_supercell.copy()
    result.remove_sites([0])
    return result


@pytest.fixture(scope="session")
def cubic_supercell_w_vacancy_w_perturb(cubic_supercell_w_vacancy):
    result = cubic_supercell_w_vacancy.copy()
    result.translate_sites([0], [0.0, 0.0, 0.1])
    return result


@pytest.fixture
def supercell_info(ortho_conventional):
    sites = {"H1": Site(element="H", wyckoff_letter="a", site_symmetry="mmm",
                        equivalent_atoms=[0, 1, 2, 3]),
             "He1": Site(element="He", wyckoff_letter="b", site_symmetry="mmm",
                         equivalent_atoms=[4, 5, 6, 7])}
    interstitial = Interstitial(frac_coords=[0.25]*3, wyckoff_letter="x",
                                site_symmetry="yy", info="test")
    return SupercellInfo(ortho_conventional,
                         "Fmmm",
                         [[1, 0, 0], [0, 1, 0], [0, 0, 1]], sites,
                         [interstitial])


@pytest.fixture
def cubic_supercell_info_wo_int(cubic_supercell):
    sites = {"H1": Site(element="H", wyckoff_letter="a", site_symmetry="m-3m",
                        equivalent_atoms=[0, 1, 2, 3]),
             "He1": Site(element="He", wyckoff_letter="b", site_symmetry="m-3m",
                         equivalent_atoms=[4, 5, 6, 7])}
    unitcell = Structure(Lattice.rhombohedral(7.071068, 60),
                         species=["H", "He"],
                         coords=[[0.0]*3, [0.5]*3])
    return SupercellInfo(cubic_supercell,
                         "Fm-3m", [[-2, 2, 2], [2, -2, 2], [2, 2, -2]], sites,
                         unitcell_structure=unitcell)


@pytest.fixture
def efnv_correction():
    s1 = PotentialSite(specie="H", distance=1.999, potential=1.0,
                       pc_potential=None)
    s2 = PotentialSite(specie="He", distance=2.0001, potential=1.5,
                       pc_potential=0.2)
    s3 = PotentialSite(specie="He", distance=3.0, potential=2.0,
                       pc_potential=0.3)

    return ExtendedFnvCorrection(charge=10,
                                 point_charge_correction=1.0,
                                 defect_region_radius=2.0,
                                 sites=[s1, s2, s3],
                                 defect_coords=(0.0, 0.0, 0.0))


@pytest.fixture(scope="session")
def before_refine():
    return Structure.from_str(fmt="POSCAR", input_string="""Mg4 O3
1.00000000000000
5 0 0
0 5 0
0 0 5
Mg   O
4     3
Direct
0.0051896248240553  0.9835077947659414  0.9945137498637422
0.0047282952713914  0.4827940046010823  0.4942929782542009
0.5040349492352973  0.9821499237428384  0.4944941755970405
0.5058945352747628  0.4828206016032297  0.9940420309511140
0.5045613848356609  0.4811103128264023  0.4933877756337353
0.0013796816599694  0.9829379087234287  0.4953360299212051
0.0083465288988691  0.4848714537370853  0.9941122597789658""")


# refine with anchor_atom_index=1, anchor_atom_coords=np.array([0.0, 0.5, 0.5])
@pytest.fixture(scope="session")
def after_refine():
    return Structure.from_str(fmt="POSCAR", input_string="""Mg4 O3
1.00000000000000
5 0 0
0 5 0
0 0 5
Mg   O
4     3
Direct
0.0 0.0 0.0
0.0 0.5 0.5
0.5 0.0 0.5
0.5 0.5 0.0
0.5 0.5 0.5
0.0 0.0 0.5
0.0 0.5 0.0""")


@pytest.fixture(scope="session")
def vol_params():
    return VolumetricDataAnalyzeParams(None, None, 0.5, 0.5, 0.4)
