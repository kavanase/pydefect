# -*- coding: utf-8 -*-
#  Copyright (c) 2020. Distributed under the terms of the MIT License.

from monty.design_patterns import singleton
from pathlib import Path
from vise.input_set.datasets.potcar_set import PotcarSet
from vise.input_set.task import Task
from vise.input_set.xc import Xc
from vise.user_settings import UserSettings


@singleton
class Defaults:
    def __init__(self):
        self._symmetry_length_tolerance = 0.01
        self._symmetry_angle_tolerance = 5.0
        self._rhombohedral_angle = 70
        self._kpoint_density = 5.0
        self._band_gap_criterion = 0.2  # in eV
        self._integer_criterion = 0.1
        self._outcar = "OUTCAR"
        self._contcar = "CONTCAR"
        self._vasprun = "vasprun.xml"
        self._procar = "PROCAR"

        user_settings = UserSettings(yaml_filename="vise.yaml")
        self.yaml_files = user_settings.yaml_files_from_root_dir
        self.user_settings = user_settings.user_settings

        for k, v in self.user_settings.items():
            if hasattr(self, k):
                self.__setattr__("_" + k, v)

    @property
    def symmetry_length_tolerance(self):
        return self._symmetry_length_tolerance

    @property
    def symmetry_angle_tolerance(self):
        return self._symmetry_angle_tolerance

    @property
    def rhombohedral_angle(self):
        return self._rhombohedral_angle

    @property
    def kpoint_density(self):
        return self._kpoint_density

    @property
    def band_gap_criterion(self):
        return self._band_gap_criterion

    @property
    def integer_criterion(self):
        return self._integer_criterion

    @property
    def outcar(self):
        return Path(self._outcar)

    @property
    def contcar(self):
        return Path(self._contcar)

    @property
    def vasprun(self):
        return Path(self._vasprun)

    @property
    def procar(self):
        return Path(self._procar)


defaults = Defaults()
