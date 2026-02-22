from typing import Literal, Self


class Generator:
    """Generator for creating a REClist."""
    def __init__(self, syllable_map: dict[str, tuple[str, str]]) -> None:
        self.syldict = SyllableDict().from_syllable_phoneme_map(syllable_map)

        _map = {}
        for left, right in self.syldict.get_syllable_map().values():
            _map.setdefault(right, []).append(left)
            self._rl_map: dict[str, list[str]] = _map

        self._syl_set: set[str] = {_ for _ in syllable_map.keys()}

        self._redu:int = 0
        self._perfect_fluent_num: int = 0
        self._in_turn_fluent_num: int = 0
        self._not_fluent_num:int = 0

    def generate(
            self, 
            mode: Literal["CVVC", "VCV", "VCV_WITH_VC"], 
            bmp: int, 
            max_length: int, 
            sss_first: bool,
            iter_depth: int,
            max_redu: int
    ) -> tuple[list[str], list[str]]:
        audio_syllable_map = self.create_reclist(mode=mode, max_length=max_length, sss_first=sss_first, iter_depth=iter_depth, max_redu=max_redu)
        oto = self.create_oto(bmp=bmp, audio_syllable_map=audio_syllable_map)
        return ([reclist for reclist in audio_syllable_map.keys()], oto)

    def create_reclist(
            self,
            mode: Literal["CVVC", "VCV", "VCV_WITH_VC"], 
            max_length: int,
            sss_first: bool,
            iter_depth: int,
            max_redu: int
    ) -> dict[str, list[str]]:
        pass

        
    def create_oto(
            self,
            audio_syllable_map: dict[str, list[str]],
            bmp: int
    ) -> list[str]:
        pass
    
    def _cvvc_perfect_fluent(self, max_length: int) -> dict[str, list[tuple[str, str]]]:
        syl_map = self.syldict.get_syllable_map()
        lr_to_syl = {phonemes: syl for syl, phonemes in syl_map.items()}

        right_order = list(self.syldict.get_right_syl_map().keys())

        result = {}
        line_num = 0

        for right in right_order:
            lefts = self._rl_map.get(right, [])
            if not lefts:
                continue

            total = len(lefts)
            full_chunks = total // max_length
            if full_chunks == 0:
                continue

            for i in range(full_chunks):
                chunk_lefts = lefts[i * max_length : (i + 1) * max_length]

                syllable_names = []
                phoneme_pairs = []

                first_syl = lr_to_syl[(chunk_lefts[0], right)]
                syllable_names.append(first_syl)
                phoneme_pairs.append(("-", first_syl))

                for left in chunk_lefts[1:]:
                    syl = lr_to_syl[(left, right)]
                    syllable_names.append(syl)
                    phoneme_pairs.append((right, left))
                    phoneme_pairs.append((syl, ""))

                phoneme_pairs.append((right, "-"))

                for syl in syllable_names:
                    self._syl_set.remove(syl)

                key = "_".join(syllable_names)
                result[key] = phoneme_pairs
                line_num += 1

            del lefts[:full_chunks * max_length]
            if not lefts:
                del self._rl_map[right]

        self._perfect_fluent_num = line_num
        return result

    def _cvvc_in_turn_fluent(self, max_length: int, iter_depth:int , max_redu:int) -> list[str, list[str]]:
        pass

    def _cvvc_not_fluent(self, max_length: int) -> list[str, list[str]]:
        pass

class SyllableDict:
    def __init__(self) -> None:
        self._syllable_map: dict[str, tuple[str, str]] = {}

        self._left_syl_map: dict[str, list[str]] = {}
        self._right_syl_map: dict[str, list[str]] = {}

    def from_syllable_phoneme_map(self, syllable_map: dict[str, tuple[str, str]]) -> Self:
        self._set_to_empty()
        self._syllable_map = syllable_map
        return self

    def from_phoneme_syllable_map(self, left_map: dict[str, list[str]], right_map: dict[str, list[str]]) -> Self:
        syl_to_left = {syl: left for left, syllables in left_map.items() for syl in syllables}
        syl_to_right = {syl: right for right, syllables in right_map.items() for syl in syllables}

        new_map = {syl: (syl_to_left[syl], syl_to_right[syl]) for syl in syl_to_left}

        self._set_to_empty()
        self._syllable_map = new_map
        return self

    def get_syllable_map(self) -> dict[str, tuple[str, str]]:
        self._check()
        return self._syllable_map

    def get_left_syl_map(self) -> dict[str, list[str]]:
        self._check()
        if not self._left_syl_map:
            _map = {}
            for syl, (left, _) in self._syllable_map.items():
                _map.setdefault(left, []).append(syl)
            self._left_syl_map = _map
        return self._left_syl_map

    def get_right_syl_map(self) -> dict[str, list[str]]:
        self._check()
        if not self._right_syl_map:
            _map = {}
            for syl, (_, right) in self._syllable_map.items():
                _map.setdefault(right, []).append(syl)
            self._right_syl_map = _map
        return self._right_syl_map
    
    def _check(self) -> None:
        if not self._syllable_map:
            raise ValueError("There is no internal data, please call the 'from' prefix method.")
        
    def _set_to_empty(self) -> None:
        self._left_syl_map = {}
        self._right_syl_map = {}
