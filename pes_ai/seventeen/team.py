import io
from struct import unpack

from pes_ai.utils import conv_from_bytes

one_byte_bools = [
    "defenceFormationTest1",
    "defenceFormationTest2",
    "dfAdjustZ",
    "dfCoverAdjustX",
    "dfCoverEnable",
    "dfForceAverageZ",
]

def map_basePosition(
    data: io.BytesIO, offset: int, length: int
) -> dict[str, int | float | bool | None]:
    vals = []
    data.seek(offset)
    for i in range(int(length / 4)):
        match i:
            # 15: adjustGapDfLineAction
            # 18: adjustSetplay
            # 21: adjustSlideMoveSpeed
            # 42: changeDefenceNumberFromSituation
            # 73: dfAttackWidthForce
            # 94: dfUserPositionAdjustEnable
            # 132: isUseDashSituation
            # 167: numericalRelationDefenceLine
            # 170: offenceZposiAdjust
            # 172: onPassCourse
            # 181: returnControlSide
            # 188: slide
            # 197: slowDownFW
            # 207: teamToGroupAdjustEnable
            # 219: xposiRateCustom
            case 15 | 18 | 21 | 42 | 73 | 94 | 132 | 167 | 170 | 172 | 181 | 188 | 197 | 207 | 219:
                # 4 bytes boolean
                vals.append(bool(unpack("<i", data.read(4))[0]))
            # 64: defenceFormationTest1
            # 65: defenceFormationTest2
            # 66: dfAdjustZ
            # 77: dfCoverAdjustX
            # 78: dfCoverEnable
            # 79: dfForceAverageZ
            case 64 | 77:
                # 1 byte boolean
                vals += list(unpack("3?", data.read(3)))
                data.seek(data.tell() + 1)
                vals += [None]
            case _:
                vals.append(conv_from_bytes(data.read(4)))

    with open("pes_ai/mappings/17/team/basePosition.txt", "r") as f:
        return dict(zip(f.read().split("\n"), vals))
