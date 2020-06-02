# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.
from fractions import Fraction
from itertools import cycle
from typing import Optional, List

from matplotlib import pyplot as plt
from vise.util.matplotlib import float_to_int_formatter

from pydefect.analyzer.band_edge_states import BandEdgeEigenvalues
from pydefect.defaults import defaults


class EigenvalueMplSettings:
    def __init__(self,
                 colors: Optional[List[str]] = None,
                 line_width: float = 1.0,
                 band_edge_line_width: float = 1.0,
                 band_edge_line_color: str = "black",
                 band_edge_line_style: str = "-",
                 supercell_band_edge_line_width: float = 0.5,
                 supercell_band_edge_line_color: str = "black",
                 supercell_band_edge_line_style: str = "-.",
                 circle_size: int = 15,
                 tick_label_size: Optional[int] = 10,
                 title_font_size: Optional[int] = 15,
                 label_font_size: Optional[int] = 12):
        self.colors = cycle(colors) if colors else defaults.defect_energy_colors
        self.line_width = line_width
        self.circle_size = circle_size
        self.tick_label_size = tick_label_size
        self.title_font_size = title_font_size
        self.label_font_size = label_font_size

        self.vline = {"linewidth": band_edge_line_width,
                      "color": band_edge_line_color,
                      "linestyle": band_edge_line_style}

        self.svline = {"linewidth": supercell_band_edge_line_width,
                       "color": supercell_band_edge_line_color,
                       "linestyle": supercell_band_edge_line_style}


class EigenvaluePlotter:
    def __init__(self,
                 title: str,
                 band_edge_eigenvalues: BandEdgeEigenvalues,
                 supercell_vbm: float,
                 supercell_cbm: float,
                 y_range: Optional[List[float]] = None,
                 y_unit: Optional[str] = "eV",
                 mpl_defaults: Optional[EigenvalueMplSettings]
                 = EigenvalueMplSettings()
                 ):

        self._title = title
        self._energies_and_occupations = band_edge_eigenvalues.energies_and_occupations
        self._kpt_coords = band_edge_eigenvalues.kpt_coords
        self._supercell_vbm = supercell_vbm
        self._supercell_cbm = supercell_cbm
        self._y_range = y_range

        self._y_unit = y_unit

        self._mpl_defaults = mpl_defaults
        self.plt = plt

        num_figure = len(self._energies_and_occupations)
        self.fig, self.axs = plt.subplots(nrows=1, ncols=num_figure, sharey='all')

    def construct_plot(self):
        self._add_eigenvalues()
        self._add_xticks()
        self._add_band_edges()
        self._set_x_range()
        # self._set_y_range()
        self._set_labels()
        self._set_title()
        self._set_formatter()
        self.plt.tight_layout()

    def _add_eigenvalues(self):
        for spin_idx, (eo_by_spin, ax) in enumerate(zip(self._energies_and_occupations, self.axs)):
            for kpt_idx, eo_by_k_idx in enumerate(eo_by_spin):
                for eo_by_band in eo_by_k_idx:
                    energy, occup = eo_by_band
                    color = "r" if occup > 0.9 else "b" if occup < 0.1 else "g"
                    ax.scatter([kpt_idx], energy, marker="o", color=color)

    def _add_xticks(self):
        x_labels = []
        for k in self._kpt_coords:
            x_label = []
            for i in k:
                frac = Fraction(i).limit_denominator(10)
                if frac.numerator == 0:
                    x_label.append("0")
                else:
                    x_label.append(f"{frac.numerator}/{frac.denominator}")
            x_labels.append("\n".join(x_label))

        for ax in self.axs:
            ax.set_xticks(list(range(len(self._kpt_coords))))
            ax.set_xticklabels(x_labels, size=10)

    def _add_band_edges(self):
        for ax in self.axs:
            ax.axhline(y=self._supercell_vbm, **self._mpl_defaults.svline)
            ax.axhline(y=self._supercell_cbm, **self._mpl_defaults.svline)

    def _set_x_range(self):
        for ax in self.axs:
            ax.set_xlim(-0.5, len(self._kpt_coords) - 0.5)

    # def _set_y_range(self):
    #     if self._y_range:
    #         self.plt.ylim(self._y_range[0], self._y_range[1])

    def _set_labels(self):
        self.fig.text(0.5, 0, "K-point coords", ha='center',
                      size=self._mpl_defaults.label_font_size)
        self.axs[0].set_ylabel(f"Energy ({self._y_unit})",
                        size=self._mpl_defaults.label_font_size)

    def _set_title(self):
        for ax, spin in zip(self.axs, ["up", "down"]):
            ax.set_title(f"{spin}:")

    def _set_formatter(self):
        self.axs[0].yaxis.set_major_formatter(float_to_int_formatter)
        for ax in self.axs:
            ax.tick_params(labelsize=self._mpl_defaults.tick_label_size)