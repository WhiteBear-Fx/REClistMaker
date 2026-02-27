from typing import Self


class SyllableView:
    """
    Phoneme table views from different perspectives.

    The values for these views must be explicitly set via member functions
    with a ``from`` prefix (e.g., ``from_syllable_phoneme_map()``).
    """

    def __init__(self) -> None:
        self._syllable_map: dict[str, tuple[str, str]] = {}

        self._syl_to_left_map: dict[str, list[str]] = {}
        self._syl_to_right: dict[str, list[str]] = {}

    def from_syllable_phoneme_map(self, syllable_map: dict[str, tuple[str, str]]) -> Self:
        """
        Build a mapping table from syllables to phonemes.

        :param syllable_map: Syllable mapping table in the format {syllable: (left, right)}.

        :return: self
        """
        self._set_to_empty()
        self._syllable_map = syllable_map
        return self

    def from_phoneme_syllable_map(self, left_map: dict[str, list[str]], right_map: dict[str, list[str]]) -> Self:
        """
        Build mapping tables from phonemes to syllables.

        :param left_map: Left phoneme table in the format {left: [syllable]}.
        :param right_map: Right phoneme table in the format {right: [syllable]}.

        :return: self
        """
        syl_to_left = {syl: left for left, syllables in left_map.items()
                       for syl in syllables}
        syl_to_right = {syl: right for right,
                        syllables in right_map.items() for syl in syllables}

        new_map = {syl: (syl_to_left[syl], syl_to_right[syl])
                   for syl in syl_to_left}

        self._set_to_empty()
        self._syllable_map = new_map
        return self

    def get_syllable_map(self) -> dict[str, tuple[str, str]]:
        """
        Get the syllable map.

        :return: {syllable: (left, right)}
        """
        self._check()
        return self._syllable_map

    def get_syl_to_left(self) -> dict[str, list[str]]:
        """
        Get the mapping table from left phonemes to syllables.

        :return: {left: [syllable]}
        """
        self._check()
        if not self._syl_to_left_map:
            _map = {}
            for syl, (left, _) in self._syllable_map.items():
                _map.setdefault(left, []).append(syl)
            self._syl_to_left_map = _map
        return self._syl_to_left_map

    def get_syl_to_right(self) -> dict[str, list[str]]:
        """
        Get the mapping table from right phonemes to syllables.

        :return: {right: [syllable]}
        """
        self._check()
        if not self._syl_to_right:
            _map = {}
            for syl, (_, right) in self._syllable_map.items():
                _map.setdefault(right, []).append(syl)
            self._syl_to_right = _map
        return self._syl_to_right

    def _check(self) -> None:
        """
        Check whether the instance is ready (whether data has been correctly read via a `from`-prefixed method).

        :raise ValueError: There is no internal data, please call the 'from' prefix method.
        """
        if not self._syllable_map:
            raise ValueError(
                "There is no internal data, please call the 'from' prefix method.")

    def _set_to_empty(self) -> None:
        """Clear the instance."""
        self._syl_to_left_map = {}
        self._syl_to_right = {}


class RLPairView:
    """
    Phoneme pair view that maintains uncombined phoneme pairs and can be operated from multiple perspectives.

    :param syllable_map: Syllable mapping table in the format {syllable: (left, right)}.
    """

    def __init__(self, syllable_map: dict[str, tuple[str, str]]):
        self._right_to_lefts = {}
        self._left_to_rights = {}

        for syl, (left, right) in syllable_map.items():
            self._right_to_lefts.setdefault(right, []).append(left)
            self._left_to_rights.setdefault(left, []).append(right)

    def get_lefts_for_right(self, right: str) -> list[str]:
        """
        Get the left phonemes that are not combined with the given right phoneme.

        :param right: Right phoneme.
        :return: List of left phonemes.
        """
        return self._right_to_lefts.get(right, []).copy()

    def get_rights_for_left(self, left: str) -> list[str]:
        """
        Get the right phonemes that are not combined with the given left phoneme.

        :param left: Left phoneme.
        :return: List of right phonemes.
        """
        return self._left_to_rights.get(left, []).copy()

    def all_rights(self) -> list[str]:
        """
        Get all currently uncombined right phonemes.

        :return: List of right phonemes.
        """
        return list(self._right_to_lefts.keys())

    def all_lefts(self) -> list[str]:
        """
        Get all currently uncombined left phonemes.

        :return: List of left phonemes.
        """
        return list(self._left_to_rights.keys())

    def pop_lefts_for_right(self, right: str, count: int) -> list[str]:
        """
        Remove left phonemes not combined with the specified right phoneme and return the removed list.

        :param right: Right phoneme.
        :param count: Number of left phonemes to remove.
        :return: List of removed left phonemes.
        """
        if right not in self._right_to_lefts:
            return []
        lefts = self._right_to_lefts[right]
        take = min(count, len(lefts))
        popped = lefts[:take]

        for left in popped:
            if left in self._left_to_rights:
                rights = self._left_to_rights[left]
                if right in rights:
                    rights.remove(right)
                    if not rights:
                        del self._left_to_rights[left]

        self._right_to_lefts[right] = lefts[take:]
        if not self._right_to_lefts[right]:
            del self._right_to_lefts[right]
        return popped

    def pop_rights_for_left(self, left: str, count: int) -> list[str]:
        """
        Remove right phonemes not combined with the specified left phoneme and return the removed list.

        :param left: Left phoneme.
        :param count: Number of right phonemes to remove.
        :return: List of removed right phonemes.
        """
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
