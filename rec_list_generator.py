from typing import Literal


class Generator:
    def __init__(self, syllable_set: set, left_set: set, right_set: set):
        self._s_set = syllable_set
        self._l_set = left_set
        self._r_set = right_set

    def generate(self, mode: Literal["CVVC", "VCV"], ):
        pass


class Transformer:
    pass