from typing import Literal, Self


class Generator:
    """Generator for creating a REClist."""
    def __init__(self, syllable_map: dict[str, tuple[str, str]]) -> None:
        self.syllable_view = SyllableView().from_syllable_phoneme_map(syllable_map)
        self._pair_view = RLPairView(syllable_map)

        self._syl_used_as_start: set[str] = set()
        self._right_used_as_end: set[str] = set()
        self._syl_used_as_nonstart: set[str] = set()

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
        self._syl_used_as_start.clear()
        self._right_used_as_end.clear()
        self._syl_used_as_nonstart.clear()

        self._perfect_fluent_num = 0
        self._in_turn_fluent_num = 0
        self._not_fluent_num = 0
        self._redu = 0

        self._pair_view = RLPairView(self.syllable_view.get_syllable_map())
        
        audio_syllable_map = self.create_reclist(
            mode=mode, 
            max_length=max_length, 
            sss_first=sss_first, 
            iter_depth=iter_depth, 
            max_redu=max_redu
        )
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
    
    def _cvvc_perfect_fluent(self, max_length: int, use_right_view: bool) -> dict[str, list[tuple[str, str]]]:
        syl_map = self.syllable_view.get_syllable_map()
        lr_to_syl = {phonemes: syl for syl, phonemes in syl_map.items()}
        result = {}
        line_num = 0

        if use_right_view:
            primary_keys = self._pair_view.all_rights()
            get_list = self._pair_view.get_lefts_for_right
            pop_chunk = self._pair_view.pop_lefts_for_right
        else:
            primary_keys = self._pair_view.all_lefts()
            get_list = self._pair_view.get_rights_for_left
            pop_chunk = self._pair_view.pop_rights_for_left

        for key in primary_keys:
            while True:
                items = get_list(key)
                if len(items) < max_length:
                    break
                chunk = pop_chunk(key, max_length)
                if not chunk:
                    break

                syllable_names = []
                phoneme_pairs = []

                if use_right_view:
                    first_syl = lr_to_syl[(chunk[0], key)]
                else:
                    first_syl = lr_to_syl[(key, chunk[0])]
                syllable_names.append(first_syl)
                phoneme_pairs.append(("-", first_syl))

                for item in chunk[1:]:
                    if use_right_view:
                        syl = lr_to_syl[(item, key)]
                    else:
                        syl = lr_to_syl[(key, item)]
                    syllable_names.append(syl)

                    if use_right_view:
                        phoneme_pairs.append((key, item))
                    else:
                        phoneme_pairs.append((item, key))

                    phoneme_pairs.append((syl, ""))

                self._syl_used_as_start.add(syllable_names[0])
                for syl in syllable_names[1:]:
                    self._syl_used_as_nonstart.add(syl)

                if use_right_view:
                    last_right = key
                else:
                    last_right = chunk[-1]
                phoneme_pairs.append((last_right, "-"))

                self._syl_used_as_start.add(syllable_names[0])
                last_syl = syllable_names[-1]
                self._right_used_as_end.add(syl_map[last_syl][1])

                key_str = "_".join(syllable_names)
                result[key_str] = phoneme_pairs
                line_num += 1

        self._perfect_fluent_num += line_num
        return result
    
    def _create_pattern(self, p: int, m: int) -> list[tuple[list[int], int]]:
        patterns = []
        for r in range(2, p + 1):
            if m % r != 0:
                continue

            def backtrack(labels: list[int], max_label: int):
                if len(labels) == r:
                    if max_label >= 1:
                        patterns.append((labels[:], max_label + 1))
                    return
                for label in range(max_label + 1):
                    labels.append(label)
                    backtrack(labels, max_label)
                    labels.pop()
                labels.append(max_label + 1)
                backtrack(labels, max_label + 1)
                labels.pop()

            backtrack([0], 0)

        patterns.sort(key=lambda x: x[1])
        return patterns

    def _try_build_in_turn(self, pattren, counts, right) -> tuple[dict[str, list[tuple[str, str]]], set[str]]:
        pass

    def _cvvc_in_turn_fluent(self, max_length: int, iter_depth: int, max_redu: int) -> dict[str, list[tuple[str, str]]]:
        pass

    def _cvvc_not_fluent(self, max_length: int) -> dict[str, list[tuple[str, str]]]:
        pass

class SyllableView:
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

class RLPairView:
    def __init__(self, syllable_map: dict[str, tuple[str, str]]):
        self._right_to_lefts = {}
        self._left_to_rights = {}
        
        for syl, (left, right) in syllable_map.items():
            self._right_to_lefts.setdefault(right, []).append(left)
            self._left_to_rights.setdefault(left, []).append(right)
    
    def get_lefts_for_right(self, right: str) -> list[str]:
        return self._right_to_lefts.get(right, []).copy()
    
    def get_rights_for_left(self, left: str) -> list[str]:
        return self._left_to_rights.get(left, []).copy()
    
    def all_rights(self) -> list[str]:
        return list(self._right_to_lefts.keys())
    
    def all_lefts(self) -> list[str]:
        return list(self._left_to_rights.keys())
    
    def pop_lefts_for_right(self, right: str, count: int) -> list[str]:
        if right not in self._right_to_lefts:
            return []
        lefts = self._right_to_lefts[right]
        take = min(count, len(lefts))
        popped = lefts[:take]
        # 更新左元视角
        for left in popped:
            if left in self._left_to_rights:
                rights = self._left_to_rights[left]
                if right in rights:
                    rights.remove(right)
                    if not rights:
                        del self._left_to_rights[left]
        # 更新右元视角
        self._right_to_lefts[right] = lefts[take:]
        if not self._right_to_lefts[right]:
            del self._right_to_lefts[right]
        return popped
    
    def pop_rights_for_left(self, left: str, count: int) -> list[str]:
        if left not in self._left_to_rights:
            return []
        rights = self._left_to_rights[left]
        take = min(count, len(rights))
        popped = rights[:take]
        for right in popped:
            if right in self._right_to_lefts:
                lefts = self._right_to_lefts[right]
                if left in lefts:
                    lefts.remove(left)
                    if not lefts:
                        del self._right_to_lefts[right]
        self._left_to_rights[left] = rights[take:]
        if not self._left_to_rights[left]:
            del self._left_to_rights[left]
        return popped