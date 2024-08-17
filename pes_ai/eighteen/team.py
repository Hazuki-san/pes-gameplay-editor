import io
from struct import unpack

from pes_ai.utils import conv_from_bytes


def map_basePosition(
    data: io.BytesIO, offset: int, length: int
) -> dict[str, int | float | bool | None]:
    vals = []
    data.seek(offset)
    for i in range(int(length / 4)):
        match i:
            case 64 | 75:
                vals += list(unpack("3?", data.read(3)))
                data.seek(data.tell() + 1)
                vals += [None]
            case _:
                vals.append(conv_from_bytes(data.read(4)))

    with open("pes_ai/mappings/18/team/basePosition.txt", "r") as f:
        return dict(zip(f.read().split("\n"), vals))
