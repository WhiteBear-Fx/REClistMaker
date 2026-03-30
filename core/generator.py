from typing import Literal
from .views import RLPairView, SyllableView


class Generator:
    """Generator for creating a REClist.

    :param syllable_map: A syllable mapping table in the format {syllable: (right, left)}.
    """

    def __init__(self, syllable_map: dict[str, tuple[str, str]]) -> None:
        self.syllable_map = syllable_map

    def reset(self) -> None:
        self._syllable_view = SyllableView().from_syllable_phoneme_map(self.syllable_map)
        self._pair_view = RLPairView(self.syllable_map)

        self._syl_unused_as_start: set[str] = set(
            self._syllable_view.get_syllable_map().keys())

        self._right_unused_as_end: set[str] = set(self._pair_view.all_rights())

        self._syl_unused_as_nonstart: set[str] = set(
            self._syllable_view.get_syllable_map().keys())

        self._redu: int = 0

        self._perfect_fluent_num: int = 0
        self._in_turn_fluent_num: int = 0
        self._not_fluent_num: int = 0

    def generate(
            self,
            mode: Literal["CVVC", "VCV", "VCV_WITH_VC"],
            policy: Literal["DEFAULT", "NO_IN_TURN"],
            bmp: int,
            max_length: int,
            sss_first: bool,
            iter_depth: int,
            max_redu: int,
    ) -> tuple[list[str], list[str]]:
        """
        Generate a reclist.

        :param mode: Generation mode, can be 'CVVC', 'VCV', or 'VCV_WITH_VC'.
        :param policy: Policy for generation, either 'DEFAULT' or 'NO_IN_TURN'. The 'NO_IN_TURN' policy disables smooth in-turn generation.
        :param bmp: Tempo (BPM) for recording guidance BGM.
        :param max_length: Maximum line length.
        :param sss_first: Whether to use SSS mode (see readme.md for details).
        :param iter_depth: Maximum number of iterations to search for smooth in-turn mode.
        :param max_redu: Maximum redundancy allowed for constructing smooth in-turn sequences; ignored under NO_IN_TURN policy.

        :return: A pair, where the first element is an array of REClist lines, and the second element is an array of oto.ini template lines.
        """

        audio_phoneme_map = self.create_reclist(
            mode=mode,
            max_length=max_length,
            sss_first=sss_first,
            iter_depth=iter_depth,
            max_redu=max_redu
        )
        oto = self.create_oto(bmp=bmp, audio_phoneme_map=audio_phoneme_map)
        return ([reclist for reclist in audio_phoneme_map.keys()], oto)

    def create_reclist(
            self,
            mode: Literal["CVVC", "VCV", "VCV_WITH_VC"],
            max_length: int,
            sss_first: bool,
            iter_depth: int,
            max_redu: int
    ) -> dict[str, list[str]]:
        self.reset()

    def create_oto(
            self,
            audio_phoneme_map: dict[str, list[str]],
            bmp: int
    ) -> list[str]:
        pass

    def _cvvc_perfect_fluent(self, max_length: int, use_right_view: bool) -> dict[str, list[tuple[str, str]]]:
        """
        Generate a perfectly smooth CVVC reclist.

        :param max_length: Maximum line length.
        :param use_right_view: After initial generation, some phonemes may remain because they are insufficient to form a full line. If this flag is set, attempt again from the perspective of right phonemes.

        :return: A reclist dictionary where keys are lines and values are lists of phoneme pairs for that line, i.e., {line: [(left, right)]}.
        """
        syl_map = self._syllable_view.get_syllable_map()
        lr_to_syl = {phonemes: syl for syl, phonemes in syl_map.items()}
        result = {}
        line_num = 0

        # TODO: Pop should not be used, but should be removed one by one based on the results.

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

                self._syl_unused_as_start.remove(syllable_names[0])
                for syl in syllable_names[1:]:
                    self._syl_unused_as_nonstart.remove(syl)

                if use_right_view:
                    last_right = key
                else:
                    last_right = chunk[-1]
                phoneme_pairs.append((last_right, "-"))

                last_syl = syllable_names[-1]
                self._right_unused_as_end.remove(syl_map[last_syl][1])

                key_str = "_".join(syllable_names)
                result[key_str] = phoneme_pairs
                line_num += 1

        self._perfect_fluent_num += line_num
        return result

    def _create_pattern(self, p: int, m: int) -> list[tuple[list[int], int]]:
        """
        Generate all possible integer sequence patterns.

        :param p: Maximum sequence length (inclusive).
        :param m: Divisor condition for filtering valid lengths r.
        :return: A list of tuples (sequence, num_labels), where sequence is a list of integers of length r, and num_labels is the number of distinct integers in the sequence (i.e., max_label + 1, at least 2). The list is sorted in ascending order of num_labels.
        """
        patterns: list[tuple[list[int], int]] = []
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

    def _cvvc_in_turn_fluent(self, pattrens: list[tuple[list[int], int]], max_length: int, use_right_view: bool) -> dict[str, list[tuple[str, str]]]:
        syl_map = self._syllable_view.get_syllable_map()
        lr_to_syl = {phonemes: syl for syl, phonemes in syl_map.items()}
        result: dict[str, list[tuple[str, str]]] = {}
        line_num = 0

        if use_right_view:
            get_all_phonemes = self._pair_view.all_rights
            get_list = self._pair_view.get_lefts_for_right
        else:
            get_all_phonemes = self._pair_view.all_lefts
            get_list = self._pair_view.get_rights_for_left

        for pattren in pattrens:
            all_phonemes = get_all_phonemes()
            pattern_len = len(pattren[0])

            # TODO: Use while to manually process the index, as the contents of the iterating container will be deleted inside the loop.
            for i in range(len(all_phonemes) - pattern_len + 1):
                phonemes = all_phonemes[i:i + pattern_len]

                # TODO: Inline nested functions.

                def _build_by_phonemes(phonemes, pattern_len) -> tuple[bool, dict[str, list[tuple[str, str]]]]:
                    line_result: dict[str, list[tuple[str, str]]] = {}

                    if len(phonemes) < pattern_len:
                        return (False, {})

                    # TODO: Remove unnecessary rotations.
                    for offset in range(pattern_len):
                        phonemes_pattren: list[str] = []

                        for label in pattren[0]:
                            index = (label + offset) % pattern_len
                            phonemes_pattren.append(phonemes[index])

                        phonemes_pattren = phonemes_pattren * \
                            (max_length // pattern_len)

                        syllable_names = []
                        phoneme_pairs = []
                        available: dict[str, list[str]] = {}

                        first = True

                        for p in phonemes_pattren:

                            if first:
                                first = False

                                if p not in available.keys():
                                    if get_list(p):
                                        available[p] = get_list(p)
                                    else:
                                        all_phonemes.remove(p)
                                        return (False, {})

                                partner = available[p][0]
                                available[p].pop()

                                if use_right_view:
                                    first_syl = lr_to_syl[(partner, p)]
                                else:
                                    first_syl = lr_to_syl[(p, partner)]

                                syllable_names.append(first_syl)
                                phoneme_pairs.append(("-", first_syl))
                                continue

                            partners = available[p]

                            if not partners:
                                return (False, {})

                            partner = partners[0]
                            available[p].pop()

                            if use_right_view:
                                syl = lr_to_syl[(partner, p)]
                            else:
                                syl = lr_to_syl[(p, partner)]
                            syllable_names.append(syl)

                            if use_right_view:
                                phoneme_pairs.append((p, partner))
                            else:
                                phoneme_pairs.append((partner, p))

                            phoneme_pairs.append((syl, ""))

                        if len(syllable_names) == max_length:
                            self._syl_unused_as_start.remove(syllable_names[0])

                            for syl in syllable_names[1:]:
                                self._syl_unused_as_nonstart.remove(syl)

                            if use_right_view:
                                last_right = phonemes_pattren[-1]
                            else:
                                last_right = phoneme_pairs[-1][1]
                            phoneme_pairs.append((last_right, "-"))

                            self._right_unused_as_end.remove(last_right)

                            reclist_line_str = "_".join(syllable_names)
                            line_result[reclist_line_str] = phoneme_pairs

                            for left, right in phoneme_pairs:
                                if left != "-" and right != "-":
                                    if right != "":
                                        self._pair_view.remove_pair(
                                            left, right)
                            return (True, line_result)
                        else:
                            return (False, {})
                    return (False, {})

                success, line_result = _build_by_phonemes(
                    phonemes, pattern_len)
                if success:
                    line_num += 1
                    result.update(line_result)

    def _cvvc_not_fluent(self, max_length: int) -> dict[str, list[tuple[str, str]]]:
        pass
