# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.
from pathlib import Path

from monty.serialization import loadfn
from pydefect.analyzer.eigenvalue_plotter import EigenvalueMplPlotter
from pydefect.chem_pot_diag.chem_pot_diag import CompositionEnergy, \
    CompositionEnergies
from pydefect.cli.vasp.make_band_edge_orbital_infos import \
    make_band_edge_orbital_infos
from pydefect.cli.vasp.make_calc_results import make_calc_results_from_vasp
from pydefect.cli.vasp.make_perfect_band_edge_state import \
    make_perfect_band_edge_state_from_vasp
from pydefect.cli.vasp.make_poscars_from_query import make_poscars_from_query
from pydefect.cli.vasp.make_unitcell import make_unitcell_from_vasp
from pydefect.input_maker.defect_entries_maker import DefectEntriesMaker
from pydefect.input_maker.defect_set import DefectSet
from pydefect.input_maker.supercell_info import SupercellInfo
from pydefect.util.mp_tools import MpQuery
from pymatgen.io.vasp import Vasprun, Outcar, Procar
from vise.defaults import defaults
from vise.util.logger import get_logger

logger = get_logger(__name__)


def make_unitcell(args):
    unitcell = make_unitcell_from_vasp(
        vasprun_band=args.vasprun_band,
        outcar_band=args.outcar_band,
        outcar_dielectric_clamped=args.outcar_dielectric_clamped,
        outcar_dielectric_ionic=args.outcar_dielectric_ionic)
    unitcell.to_yaml_file()


def make_competing_phase_dirs(args):
    query = MpQuery(element_list=args.elements, e_above_hull=args.e_above_hull)
    make_poscars_from_query(materials_query=query.materials, path=Path.cwd())


def make_composition_energies(args):
    if args.yaml_file:
        composition_energies = CompositionEnergies.from_yaml(args.yaml_file)
    else:
        composition_energies = CompositionEnergies()

    for d in args.dirs:
        vasprun = Vasprun(d / defaults.vasprun)
        composition = vasprun.final_structure.composition
        energy = float(vasprun.final_energy)  # original type is FloatWithUnit
        composition_energies[composition] = CompositionEnergy(energy, "local")
    composition_energies.to_yaml_file()


def make_defect_entries(args):
    supercell_info: SupercellInfo = loadfn("supercell_info.json")
    perfect = Path("perfect")

    try:
        perfect.mkdir()
        logger.info("Making perfect dir...")
        supercell_info.structure.to(filename=perfect / "POSCAR")
    except FileExistsError:
        logger.info(f"perfect dir exists, so skipped...")

    defect_set = DefectSet.from_yaml()
    maker = DefectEntriesMaker(supercell_info, defect_set)

    for defect_entry in maker.defect_entries:
        dir_path = Path(defect_entry.full_name)
        try:
            dir_path.mkdir()
            logger.info(f"Making {dir_path} dir...")
            defect_entry.perturbed_structure.to(filename=dir_path / "POSCAR")
            defect_entry.to_json_file(filename=dir_path / "defect_entry.json")
            defect_entry.to_prior_info(filename=dir_path / "prior_info.yaml")
        except FileExistsError:
            logger.info(f"{dir_path} dir exists, so skipped...")


def make_calc_results(args):
    for d in args.dirs:
        logger.info(f"Parsing data in {d} ...")
        calc_results = make_calc_results_from_vasp(
            vasprun=Vasprun(d / defaults.vasprun),
            outcar=Outcar(d / defaults.outcar))
        calc_results.to_json_file(str(Path(d) / "calc_results.json"))


def make_band_edge_orb_infos_and_eigval_plot(args):
    supercell_vbm = args.perfect_calc_results.vbm
    supercell_cbm = args.perfect_calc_results.cbm
    for d in args.dirs:
        logger.info(f"Parsing data in {d} ...")
        try:
            defect_entry = loadfn(d / "defect_entry.json")
            title = defect_entry.name
        except FileNotFoundError:
            title = "No name"
        procar = Procar(d / defaults.procar)
        vasprun = Vasprun(d / defaults.vasprun)
        str_info = loadfn(d / "defect_structure_info.json")
        band_edge_orb_chars = make_band_edge_orbital_infos(
            procar, vasprun, supercell_vbm, supercell_cbm, str_info)
        band_edge_orb_chars.to_json_file(d / "band_edge_orbital_infos.json")
        plotter = EigenvalueMplPlotter(
            title=title, band_edge_orb_infos=band_edge_orb_chars,
            supercell_vbm=supercell_vbm, supercell_cbm=supercell_cbm)
        plotter.construct_plot()
        plotter.plt.savefig(fname=d / "eigenvalues.pdf")
        plotter.plt.clf()


def make_perfect_band_edge_state(args):
    procar = Procar(args.dir / defaults.procar)
    vasprun = Vasprun(args.dir / defaults.vasprun)
    outcar = Outcar(args.dir / defaults.outcar)
    perfect_band_edge_state = \
        make_perfect_band_edge_state_from_vasp(procar, vasprun, outcar)
    perfect_band_edge_state.to_json_file(
        args.dir / "perfect_band_edge_state.json")
