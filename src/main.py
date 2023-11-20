import json
import math
import multiprocessing
import random
from collections import Counter, defaultdict, deque
from copy import deepcopy
from functools import cache, partial
from typing import Optional

from tqdm import tqdm


def read_word_list(file: str) -> list[str]:
    with open(file, mode="r", encoding="utf8") as fp:
        return [s.strip() for s in fp.readlines()]


def entropy(px: float) -> float:
    return -math.log2(px) * px


@cache
def match_pair_result(curr: str, other: str) -> tuple[int, ...]:
    res = [0 for _ in curr]
    char_pos = defaultdict(deque)
    for i, (cc, co) in enumerate(zip(curr, other)):
        if cc == co:
            res[i] = 2
        else:
            char_pos[cc].append(i)

    for i, co in enumerate(other):
        if res[i] != 2 and len(char_pos[co]) > 0:
            pos = char_pos[co].popleft()
            res[pos] = 1

    return tuple(res)


def information_gain(word: str, candidates: list[str]) -> float:
    bins = Counter(match_pair_result(word, candidate) for candidate in candidates)

    return sum(entropy(v / len(candidates)) for v in bins.values())


def best_guess(candidates: list[str], dictionary: list[str]) -> str:
    max_information = 0
    best_word = candidates[0]

    for word in dictionary:
        information = information_gain(word, candidates)
        if information > max_information:
            max_information = information
            best_word = word

    return best_word


def guess(
    word: str, information_pattern: tuple[int, ...], candidates: list[str]
) -> list[str]:
    new_candidates = []
    for candidate in candidates:
        if match_pair_result(word, candidate) == information_pattern:
            new_candidates.append(candidate)
    return new_candidates


def print_information_pattern(
    guess_word: str,
    information_pattern: tuple[int, ...],
    information: float,
):
    blocks = ["⬜", "🟧", "🟩"]
    print(
        *[blocks[i] for i in information_pattern],
        f"- {guess_word} - {information:0.2f}",
        sep="",
    )
    print("-" * len(guess_word))


def play_game(
    candidates: list[str],
    dictionary: list[str],
    secret: Optional[str] = None,
    *,
    verbose=True,
) -> int:
    if secret is None:
        secret = random.choice(candidates)
    # candidates = dictionary
    candidates = deepcopy(candidates)

    if verbose:
        print(secret)
        print("-" * len(secret))
    n = 0
    while candidates and n < 10:
        n += 1
        guess_word = best_guess(candidates, dictionary)
        information = information_gain(guess_word, candidates)
        information_pattern = match_pair_result(guess_word, secret)

        if verbose:
            print_information_pattern(guess_word, information_pattern, information)

        if secret == guess_word:
            break

        candidates = guess(guess_word, information_pattern, candidates)

    return n


def global_stats(candidates: list[str], dictionary: list[str]) -> dict[str, int]:
    # stats = {}
    play_game_p = partial(play_game, candidates, dictionary, verbose=False)
    with multiprocessing.Pool(8) as pool:
        scores = pool.imap(play_game_p, candidates)
        stats = dict(zip(candidates, list(tqdm(scores, total=len(candidates)))))
    return stats


def main():
    candidates = read_word_list("data/possible_words.txt")
    dictionary = read_word_list("data/allowed_words.txt")

    stats = global_stats(candidates, dictionary)

    with open("stats.json", "w") as fp:
        json.dump(stats, fp)

    print(stats)


if __name__ == "__main__":
    main()
