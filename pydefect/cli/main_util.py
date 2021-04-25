# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.

import argparse
import sys
import warnings

from monty.serialization import loadfn
from pydefect.cli.main import description, epilog, add_sub_parser
from pydefect.cli.main_util_functions import make_gkfo_correction_from_vasp, \
    composition_energies_from_mp
from pymatgen.io.vasp.inputs import UnknownPotcarWarning

warnings.simplefilter('ignore', UnknownPotcarWarning)


def parse_args_main_util(args):
    parser = argparse.ArgumentParser(epilog=epilog,
                                     description=description + """                            
    This command provide some utilities related to the VASP calculations""")

    subparsers = parser.add_subparsers()
    unitcell_parser = add_sub_parser(argparse, name="unitcell")

    # -- composition energies from mp ------------------------------------------
    parser_comp_es_from_mp = subparsers.add_parser(
        name="composition_energies_from_mp",
        description="Retrieve composition energies from Materials Project.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        aliases=['cefm'])

    parser_comp_es_from_mp.add_argument(
        "-e", "--elements", type=str, nargs="+",
        help="Element names considered in chemical potential diagram. Used for "
             "creating the diagram from mp data with atom energy alignment.")
    parser_comp_es_from_mp.add_argument(
        "-a", "--atom_energy_yaml", type=str,
        help="Yaml file storing atom energies for energy alignment.")

    parser_comp_es_from_mp.set_defaults(func=composition_energies_from_mp)

    # -- gkfo correction ------------------------------------------------
    parser_gkfo = subparsers.add_parser(
        name="gkfo",
        description="Generate GKFO correction files.",
        parents=[unitcell_parser],
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        aliases=['gkfo'])

    parser_gkfo.add_argument(
        "-iefnv", "--initial_efnv_correction", required=True, type=loadfn,
        help="Path to the initial efnv correction.json file.")
    parser_gkfo.add_argument(
        "-icr", "--initial_calc_results", required=True, type=loadfn,
        help="Path to the initial calc_results.json file.")
    parser_gkfo.add_argument(
        "-fcr", "--final_calc_results", required=True, type=loadfn,
        help="Path to the final calc_results.json file.")
    parser_gkfo.add_argument(
        "-cd", "--charge_diff", required=True, type=int,
        help="Charge difference of final state from initial state.")

    parser_gkfo.set_defaults(func=make_gkfo_correction_from_vasp)
    # ------------------------------------------------------------------------
    return parser.parse_args(args)


def main():
    args = parse_args_main_util(sys.argv[1:])
    args.func(args)


if __name__ == "__main__":
    main()


