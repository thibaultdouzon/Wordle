import pytest

from src.main import match_pair_result, read_word_list


@pytest.fixture
def dictionary():
    return read_word_list("../data/allowed_words.txt")


@pytest.fixture
def candidates():
    return read_word_list("../data/possible_words.txt")


def test_match_pair_result():
    assert match_pair_result("crane", "slave") == (0, 0, 2, 0, 2)
    assert match_pair_result("crave", "slave") == (0, 0, 2, 2, 2)
    assert match_pair_result("arane", "slave") == (0, 0, 2, 0, 2)
    assert match_pair_result("aahne", "slave") == (1, 0, 0, 0, 2)
    assert match_pair_result("aavne", "slave") == (1, 0, 1, 0, 2)
    assert match_pair_result("aahne", "slaae") == (1, 1, 0, 0, 2)
