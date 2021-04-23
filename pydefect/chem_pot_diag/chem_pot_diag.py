# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.
import string
from copy import copy
from dataclasses import dataclass
from itertools import product
from typing import Dict, Optional, Union, List, Set, Tuple

import numpy as np
import yaml
from monty.json import MSONable
from monty.serialization import loadfn
from pydefect.error import PydefectError
from pymatgen.core import Composition
from scipy.spatial.qhull import HalfspaceIntersection
from vise.util.mix_in import ToYamlFileMixIn

AtoZ = list(string.ascii_uppercase)
LargeMinusNumber = -1e5


@dataclass
class CompositionEnergy(MSONable):
    energy: float
    source: str = None


class CompositionEnergies(ToYamlFileMixIn, dict):
    """
    keys: Composition
    values: CompositionEnergy
    """
    def to_yaml(self) -> str:
        d = {}
        for k, v in self.items():
            key = str(k.iupac_formula).replace(" ", "")
            val = {"energy": v.energy, "source": str(v.source)}
            d[key] = val
        return yaml.dump(d)

    @classmethod
    def from_yaml(cls, filename: str = None):
        name = filename or cls._yaml_filename()
        d = loadfn(name)
        composition_energies = {}
        for k, v in d.items():
            source = v.get('source', None)
            key = Composition(k)
            composition_energies[key] = CompositionEnergy(v["energy"], source)
        return cls(composition_energies)

    @property
    def elements(self):
        result = set()
        for c in self:
            result.update(set([str(e) for e in c.elements]))
        return sorted(result)

    @property
    def std_rel_energies(self) -> Tuple["StandardEnergies", "RelativeEnergies"]:
        std, rel = StandardEnergies(), RelativeEnergies()
        abs_energies_per_atom = {k.reduced_formula: v.energy / k.num_atoms
                                 for k, v in self.items()}
        std_energies_list = []
        for vertex_element in self.elements:
            # This target is needed as some reduced formulas shows molecule
            # ones such as H2 and O2.
            reduced_formula = Composition({vertex_element: 1.0}).reduced_formula
            candidates = filter(lambda x: x[0] == reduced_formula,
                                abs_energies_per_atom.items())
            try:
                min_abs_energy = min([abs_energy_per_atom[1]
                                      for abs_energy_per_atom in candidates])
            except ValueError:
                print(f"Element {vertex_element} does not exist in "
                      f"CompositionEnergies.")
                raise NoElementEnergyError
            std[vertex_element] = min_abs_energy
            std_energies_list.append(min_abs_energy)

        for reduced_formula, abs_energy_per_atom in abs_energies_per_atom.items():
            if Composition(reduced_formula).is_element:
                continue
            frac = atomic_fractions(reduced_formula, self.elements)
            offset = sum([a * b for a, b in zip(frac, std_energies_list)])
            rel[reduced_formula] = abs_energy_per_atom - offset

        return std, rel


class CpdAbstractEnergies(ToYamlFileMixIn, dict):
    """
    keys: str (composition name)
    values: float (energy per atom)
    """
    def to_yaml(self) -> str:
        return yaml.dump(dict(self))

    @classmethod
    def from_yaml(cls, filename: str = None):
        return cls(loadfn(filename or cls._yaml_filename()))


class StandardEnergies(CpdAbstractEnergies):
    pass


def atomic_fractions(comp: Union[Composition, str], elements: List[str]
                     ) -> List[float]:
    return [Composition(comp).fractional_composition[e] for e in elements]


def comp_to_element_set(comp: Union[Composition, str]) -> Set[str]:
    return {str(e) for e in Composition(comp).elements}


def target_element_chem_pot(comp: Union[Composition, str],
                            energy_per_atom: float,
                            target_element: str,
                            other_elem_chem_pot: Dict[str, float]) -> float:
    assert comp_to_element_set(comp) \
           <= set(other_elem_chem_pot) | {target_element}
    other_element_val = 0.0
    for element, frac in Composition(comp).fractional_composition.items():
        if target_element == str(element):
            target_frac = frac
            continue
        other_element_val += other_elem_chem_pot[str(element)] * frac
    return (energy_per_atom - other_element_val) / target_frac


class RelativeEnergies(CpdAbstractEnergies):
    #TODO: add stability
    @property
    def all_element_set(self) -> Set[str]:
        return set().union(*[comp_to_element_set(c) for c in self])

    def host_composition_energies(self, elements: List[str]
                                  ) -> Dict[str, float]:
        return {formula: energy for formula, energy in self.items()
                if comp_to_element_set(formula).issubset(elements)}

    def comp_energies_with_element(self,
                                   element: str) -> Dict[str, float]:
        return {formula: energy for formula, energy in self.items()
                if element in comp_to_element_set(formula)}

    def impurity_chem_pot(self, impurity_element: str,
                          host_elements_chem_pot: Dict[str, float]
                          ) -> Tuple[float, str]:
        impurity_chem_pot = {impurity_element: 0.0}
        comp_energies = self.comp_energies_with_element(impurity_element)

        for formula, energy_per_atom in comp_energies.items():
            impurity_chem_pot[formula] = target_element_chem_pot(
                formula, energy_per_atom, impurity_element,
                host_elements_chem_pot)

        competing_phase_formula = min(impurity_chem_pot,
                                      key=impurity_chem_pot.get)
        chem_pot = impurity_chem_pot[competing_phase_formula]
        return chem_pot, competing_phase_formula


class ChemPotDiagMaker:
    def __init__(self,
                 relative_energies: RelativeEnergies,
                 elements: List[str],
                 target: str = None):
        self.relative_energies = relative_energies
        self.host_composition_energies = \
            relative_energies.host_composition_energies(elements)
        self.elements = elements
        self.impurity_elements = \
            relative_energies.all_element_set.difference(elements)
        self.dim = len(elements)

        if target:
            try:
                assert target in relative_energies.keys()
            except AssertionError:
                print(f"Target {target} is not in relative energy compounds.")
                raise
        self.target = target

    def _calc_vertices(self):
        half_spaces = []

        for formula, energy in self.host_composition_energies.items():
            half_spaces.append(
                atomic_fractions(formula, self.elements) + [-energy])

        for i in range(self.dim):
            upper_boundary, lower_boundary = [0.0] * self.dim, [0.0] * self.dim
            upper_boundary[i], lower_boundary[i] = 1.0, -1.0

            upper_boundary.append(0.0)
            lower_boundary.append(LargeMinusNumber)
            half_spaces.extend([upper_boundary, lower_boundary])

        feasible_point = np.array([LargeMinusNumber + 1.0] * self.dim,
                                  dtype=float)
        hs = HalfspaceIntersection(np.array(half_spaces), feasible_point)
        self.vertices = hs.intersections.tolist()

    def _is_composition_involved(self,
                                 coord: List[float],
                                 composition: str,
                                 energy: float) -> bool:
        atom_frac = atomic_fractions(composition, self.elements)
        diff = sum([x * y for x, y in zip(atom_frac, coord)]) - energy
        return abs(diff) < 1e-8

    def _min_energy_range(self, mul: float = 1.1):
        vertex_values = [x for x in sum(self.vertices, [])
                         if x != LargeMinusNumber]
        return min(vertex_values) * mul

    def _polygons(self):
        self._calc_vertices()
        min_val = self._min_energy_range()

        result = {}
        target_coords = None
        if self.target:
            target_coords = [[round(j, ndigits=5) for j in i]
                             for i in self.vertices
                             if self._is_composition_involved(i, self.target,
                                                              self.host_composition_energies[self.target])]
            competing_phases = [[] for i in target_coords]

        # elements
        for _idx, element in enumerate(self.elements):
            coords = [[round(j, ndigits=5) for j in i]
                      for i in self.vertices if round(i[_idx], ndigits=5) == 0.0]
            coords = [[c if c != LargeMinusNumber else min_val for c in cc] for cc in coords]
            result[element] = coords

            if self.target:
                for c in coords:
                    if c in target_coords:
                        _idx = target_coords.index(c)
                        competing_phases[_idx].append(element)

        # compounds
        for comp, energy in self.host_composition_energies.items():
            coords = [[round(j, ndigits=5) for j in i]
                      for i in self.vertices if self._is_composition_involved(i, comp, energy)]
            if coords:
                result[comp] = coords
                if self.target and comp != self.target:
                    for c in coords:
                        if c in target_coords:
                            _idx = target_coords.index(c)
                            competing_phases[_idx].append(comp)

        x = []
        if self.target:
            for v, w in zip(target_coords, competing_phases):
                impurity_phases = []
                host_chem_pot = dict(zip(self.elements, v))
                i = {imp: self.relative_energies.impurity_chem_pot(imp, host_chem_pot)
                     for imp in self.impurity_elements}
                d = dict(zip(self.elements, v))
                for k, (chem_pot, formula) in i.items():
                    d[k] = chem_pot
                    impurity_phases.append(formula)
                x.append(TargetVertex(d, w, impurity_phases))
        return result, x or None, target_coords

    @property
    def chem_pot_diag_and_target_vertex(self):
        polygons, target_vertices, target_coords = self._polygons()
        if self.target:
            AtoZZ = product([""] + AtoZ, AtoZ)
            t_vertices = TargetVertices(self.target, {"".join(next(AtoZZ)): v for v in target_vertices})
            AtoZZ = product([""] + AtoZ, AtoZ)
            v_coords = {"".join(next(AtoZZ)): v for v in target_coords}
        else:
            t_vertices, v_coords = None, None

        cpd = ChemPotDiag(vertex_elements=self.elements,
                          polygons=polygons,
                          target=self.target,
                          target_vertices=v_coords)
        return cpd, t_vertices


@dataclass
class TargetVertex(MSONable):
    chem_pot: Dict[str, float]
    competing_phases: Optional[List[str]] = None
    impurity_phases: Optional[List[str]] = None


# To yaml
@dataclass
class TargetVertices:
    target: str
    vertices: Dict[str, TargetVertex]

    @property
    def chem_pots(self) -> Dict[str, List[float]]:
        return {k: v.chem_pot for k, v in self.vertices.items()}

    # def to_yaml(self) -> str:
    #     d = {}
    #     for k, v in self.items():
    #         key = str(k.iupac_formula).replace(" ", "")
    #         val = {"energy": v.energy, "source": str(v.source)}
    #         d[key] = val
    #     return yaml.dump(d)

    # @classmethod
    # def from_yaml(cls, filename: str = None):
    #     name = filename or cls._yaml_filename()
    #     d = loadfn(name)
    #     composition_energies = {}
    #     for k, v in d.items():
    #         source = v.get('source', None)
    #         key = Composition(k)
    #         composition_energies[key] = CompositionEnergy(v["energy"], source)
    #     return cls(composition_energies)


@dataclass
class ChemPotDiag(MSONable):
    vertex_elements: List[str]
    polygons: Dict[str, List[List[float]]]
    target: str = None
    target_vertices: Dict[str, List[float]] = None

    @property
    def min_value(self):
        return np.min(sum(self.polygons.values(), []))

    @property
    def dim(self):
        return len(self.vertex_elements)

    @property
    def comp_centers(self):
        _polygons = {}
        return {c: np.average(np.array(v), axis=0).tolist()
                for c, v in self.polygons.items()}

    def atomic_fractions(self, composition: str):
        return [Composition(composition).get_atomic_fraction(e)
                for e in self.vertex_elements]


# def replace_comp_energy(chem_pot_diag: ChemPotDiag,
#                         replaced_comp_energies: List[CompositionEnergy]):
#     new_comp_energies = []
#     for ce in chem_pot_diag.comp_energies:
#         for replaced_comp_energy in replaced_comp_energies:
#             if (ce.composition.reduced_composition
#                     == replaced_comp_energy.composition.reduced_composition):
#                 new_comp_energies.append(replaced_comp_energy)
#                 break
#         else:
#             new_comp_energies.append(ce)
#     chem_pot_diag.comp_energies = new_comp_energies


class NoElementEnergyError(PydefectError):
    pass
