from typing import Literal


class Generator:
    def __init__(self, syllable_set: set, left_set: set, right_set: set) -> None:
        self._s_set = syllable_set
        self._l_set = left_set
        self._r_set = right_set

    def generate(
            self, 
            mode: Literal["CVVC", "VCV", "VCV_WIRH_VC"], 
            bmp: int, 
            max_length: int, 
            sss_first: bool,
            iter_depth: int,
            max_redu: int
    ) -> tuple[list[str], list[str]]:
        map = self._crate_reclist(mode=mode, max_length=max_length, sss_first=sss_first, iter_depth=iter_depth, max_redu=max_redu)
        self._crate_oto(bmp=bmp, audio_syllable_map=map)

    def _crate_reclist(
            self,
            mode: Literal["CVVC", "VCV", "VCV_WIRH_VC"], 
            max_length: int,
            sss_first: bool,
            iter_depth: int,
            max_redu: int
    ) -> dict[str, tuple[str]]:
        pass
        
    def _crate_oto(
            self,
            audio_syllable_map: dict[str, tuple[str]],
            bmp: int
    ) -> list[str]:
        pass

class Transformer:
    pass