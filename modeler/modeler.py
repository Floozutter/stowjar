"""
transform a keylog file of a goblinstep process into a markov chain model
"""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from collections.abc import Iterable, Set
from pathlib import Path
from typing import NamedTuple, Self

Key = str

class KeyState(NamedTuple):
    held: frozenset[Key]
    @classmethod
    def empty(cls) -> Self:
        return cls(frozenset())
    def change(self: Self, key: str, push: bool) -> Self:
        return self.__class__(self.held | {key} if push else self.held - {key})

class KeyEvent(NamedTuple):
    timestamp: int
    key: Key
    push: bool
    @classmethod
    def parse_from_line(cls, line: str) -> Self:
        timestamp, key, push = line.strip().split()
        return cls(int(timestamp), key, bool(int(push)))
 
class KeystateChangeCounter:
    def __init__(self: Self) -> None:
        # mapping of keystates to keystate destinations, and...
        # the durations to those destinations, and...
        # the weights to the durations
        self.changes: dict[KeyState, dict[KeyState, dict[int, int]]] = (
            defaultdict(lambda: defaultdict(Counter))
        )
    def add(self: Self, src: KeyState, dest: KeyState, duration: int) -> None:
        self.changes[src][dest][duration] += 1

def keylog_into_chain(keylog: Iterable[KeyEvent]):
    counter = KeystateChangeCounter()
    # iterate over keylog and add in changes
    last_keystate = KeyState.empty()
    last_timestamp: int | None = None
    for e in keylog:
        # get current keystate and duration since last keystate
        keystate = last_keystate.change(e.key, e.push)
        if keystate == last_keystate:
            # something weird happened with the keylog, skip this event
            continue
        duration = e.timestamp - last_timestamp if last_timestamp is not None else 0
        counter.add(last_keystate, keystate, duration)
        # update last keystate and timestamp
        last_keystate = keystate
        last_timestamp = e.timestamp
    # fill in keystates with no changes leading out, in case insufficient data from keylog
    ...
    # transform counts into probabilities
    ...
    return None

def parse_args() -> tuple[Path, Path]:
    parser = ArgumentParser(description = __doc__)
    parser.add_argument("inputkeylog", type = Path)
    parser.add_argument("outputchain", type = Path)
    args = parser.parse_args()
    return args.inputkeylog, args.outputchain

def main(keylog_path: Path, chain_path: Path) -> None:
    keylog = map(KeyEvent.parse_from_line, keylog_path.read_text().strip().split())
    chain = keylog_into_chain(keylog)

if __name__ == "__main__":
    main(*parse_args())
