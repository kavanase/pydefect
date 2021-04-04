# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.
from pathlib import Path

import pytest
from monty.serialization import loadfn
from pydefect.analyzer.band_edge_states import BandEdgeEigenvalues, \
    BandEdgeOrbitalInfos, OrbitalInfo
from pydefect.analyzer.eigenvalue_plotter import EigenvalueMplPlotter, \
    EigenvaluePlotlyPlotter
from vise.util.dash_helper import show_png

try:
    import psutil
    PSUTIL_NOT_PRESENT = False
except ModuleNotFoundError:
    PSUTIL_NOT_PRESENT = True


orbital_infos = BandEdgeOrbitalInfos(
    orbital_infos=[[[
        OrbitalInfo(energy=0.0, orbitals={}, occupation=1.0, participation_ratio=0.3),
        OrbitalInfo(energy=0.5, orbitals={}, occupation=0.5, participation_ratio=0.3),
        OrbitalInfo(energy=1.0, orbitals={}, occupation=0.0, participation_ratio=0.3)],
       [OrbitalInfo(energy=0.0, orbitals={}, occupation=1.0, participation_ratio=0.3),
        OrbitalInfo(energy=0.5, orbitals={}, occupation=0.5, participation_ratio=0.3),
        OrbitalInfo(energy=1.0, orbitals={}, occupation=0.0, participation_ratio=0.3)]],
      [[OrbitalInfo(energy=0.0, orbitals={}, occupation=1.0, participation_ratio=0.3),
        OrbitalInfo(energy=0.5, orbitals={}, occupation=0.5, participation_ratio=0.3),
        OrbitalInfo(energy=1.0, orbitals={}, occupation=0.0, participation_ratio=0.3)],
       [OrbitalInfo(energy=0.0, orbitals={}, occupation=1.0, participation_ratio=0.3),
        OrbitalInfo(energy=0.5, orbitals={}, occupation=0.5, participation_ratio=0.3),
        OrbitalInfo(energy=1.0, orbitals={}, occupation=0.0, participation_ratio=0.3)]]],
    kpt_coords=[(0.0, 0.0, 0.0), (0.25, 0.0, 0.0)],
    kpt_weights=[0.5, 0.5],
    lowest_band_index=10,
    fermi_level=0.5)


@pytest.fixture
def eigenvalue_mpl_plotter():
    return EigenvalueMplPlotter(title="test",
                                band_edge_orb_infos=orbital_infos,
                                supercell_vbm=0.1, supercell_cbm=0.9)


def test_plot(eigenvalue_mpl_plotter):
    eigenvalue_mpl_plotter.construct_plot()
    eigenvalue_mpl_plotter.plt.show()


# def test_plot_with_actual_file():
#     eig = loadfn(Path(__file__).parent / "band_edge_eigenvalues.json")
#     plotter = EigenvalueMplPlotter(title="test", band_edge_eigenvalues=eig,
#                                    supercell_vbm=0.5, supercell_cbm=2.6)
#     plotter.construct_plot()
#     plotter.plt.show()


# @pytest.mark.skipif(PSUTIL_NOT_PRESENT, reason="psutil does not exist")
# def test_plotly_with_actual_file():
#     eig = loadfn(Path(__file__).parent / "band_edge_eigenvalues.json")
#     plotter = EigenvaluePlotlyPlotter(title="test", band_edge_eigenvalues=eig,
#                                       supercell_vbm=0.5, supercell_cbm=2.6)
#     fig = plotter.create_figure()
#     # fig.show()
#     show_png(fig)
