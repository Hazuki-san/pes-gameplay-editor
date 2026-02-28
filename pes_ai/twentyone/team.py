from io import BytesIO
from struct import unpack

from pes_ai.utils import conv_from_bytes

one_byte_bools = [
    # basePosition - stored as individual bytes
    "adjustGapDfLineAction",
    "adjustSetplay",
    "adjustSlideMoveSpeed",
    "changeDefenceNumberFromSituation",
    "defenceFormationTest1",
    "defenceFormationTest2",
    "dfAdjustZ",
    "dfAttackWidthForce",
    "dfCoverAdjustX",
    "dfCoverEnable",
    "dfForceAverageZ",
    "dfUserPositionAdjustEnable",
    "isUseDashSituation",
    "numericalRelationDefenceLine",
    "offenceZposiAdjust",
    "onPassCourse",
    "returnControlSide",
    "slide",
    "slowDownFw",
    "teamToGroupAdjustEnable",
    "xposiRateCustom",
    # lineBreak
    "eyeOff",
    "lastLine",
    "lastLineEnemy",
    "pullAway",
    "pullAwaySide",
    # spaceRun
    "backwardCurve",
    "createPassCourse",
    "defenceGap",
    "inOut",
    "roundTest",
    "vitalSupportPrior",
]

# Field type definitions extracted from IDA:
# sub_140384750 -> float
# sub_140384810 -> int (DWORD)
# sub_1403846D0 -> bool (BYTE)
#
# Structure layout (offset from a1, starting at +8):
# Each entry: (offset, name, type) where type is 'f'=float, 'i'=int, 'b'=bool(byte)
BASEPOSITION_LAYOUT = [
    (8, "adjustAngle_FreeKickSupport", "f"),
    (12, "adjustBackOF", "f"),
    (16, "adjustCloseRate_stratagy_defensive", "f"),
    (20, "adjustCloseZRate_FreeKick", "f"),
    (24, "adjustDefenceLine_ForeCheck", "f"),
    (28, "adjustDefenceLine_Retreat", "f"),
    (32, "adjustDefenceLine_strategy_defensive", "f"),
    (36, "adjustDefenceLine_strategy_levelup", "f"),
    (40, "adjustDfLineWidth_GoalKick", "f"),
    (44, "adjustDistX_Throwin_CB", "f"),
    (48, "adjustDiv", "f"),
    (52, "adjustEnemyZ", "i"),
    (56, "adjustFrontOF", "f"),
    (60, "adjustFwLine", "f"),
    (64, "adjustGapDfLine", "i"),
    (68, "adjustGapDfLineAction", "b"),
    (72, "adjustMoveEnemySide", "i"),
    (76, "adjustReturnDist", "f"),
    (80, "adjustSetplay", "b"),
    (84, "adjustSideZ", "f"),
    (88, "adjustSideZ_concept_side", "f"),
    (92, "adjustSlideMoveSpeed", "b"),
    (96, "adjustSpaceCoverRate", "f"),
    (100, "adjustSupportDist_FreeKick", "f"),
    (104, "adjustWidth_strategy_defensive", "f"),
    (108, "adjustXCompactFW", "f"),
    (112, "adjustXFromAttackAwareness3", "f"),
    (116, "adjustXFromAttackAwareness4", "f"),
    (120, "adjustX_FreeKick", "f"),
    (124, "adjustZCompact", "f"),
    (128, "adjustZMinCompact", "f"),
    (132, "adjustZOneSideCut", "f"),
    (136, "adjustZRate_cover", "f"),
    (140, "adjustZ_FreeKick", "f"),
    (144, "attackLevel", "i"),
    (148, "attackLevelAdjustX", "f"),
    (152, "backOffsideLine", "i"),
    (156, "ballSideMaxRate_stratagy_defensive", "f"),
    (160, "ballSideOpen", "i"),
    (164, "baseCloseZRate_FreeKick", "f"),
    (168, "baseDist_FreeKick", "f"),
    (172, "baseMfTargetLineWidth", "f"),
    (176, "changeDefenceNumberFromSituation", "b"),
    (180, "changeWidthRate", "f"),
    (184, "checkAdjustDist", "f"),
    (188, "checkBaseDist", "f"),
    (192, "checkReturnDist", "f"),
    (196, "checkReturnDistX", "f"),
    (200, "checkReturnDistZ", "f"),
    (204, "checkZRate_cover", "f"),
    (208, "closePenetrateZRate", "f"),
    (212, "closeRate_DF_FW", "f"),
    (216, "closeRate_DF_FW_Retreat", "f"),
    (220, "closeRate_MF_adjustX", "f"),
    (224, "closeRate_MF_adjustX_stratagy_defensive", "f"),
    (228, "closeSideZRate", "f"),
    (232, "closeZRateThrowin", "f"),
    (236, "cornerKickOffencePlayerNumber", "i"),
    (240, "cornerKickType", "i"),
    (244, "cornerkickDefenceMFSide", "f"),
    (248, "cornerkickDefenceMFWidth", "f"),
    (252, "coverLimitXRate", "f"),
    (256, "coverRateZ", "f"),
    (260, "defenceCompact", "i"),
    (264, "defenceFormationTest1", "b"),
    (265, "defenceFormationTest2", "b"),
    (266, "dfAdjustZ", "b"),
    (268, "dfAdjustZCheckLenMax", "f"),
    (272, "dfAdjustZCheckLenMin", "f"),
    (276, "dfAdjustZCheckWidthMax", "f"),
    (280, "dfAdjustZCheckWidthMin", "f"),
    (284, "dfAdjustZRateMax", "f"),
    (288, "dfAttackWidthBack", "f"),
    (292, "dfAttackWidthForce", "b"),
    (296, "dfAttackWidthFront", "f"),
    (300, "dfAttackWidthMarginBack", "f"),
    (304, "dfAttackWidthMarginFront", "f"),
    (308, "dfCoverAdjustX", "b"),
    (309, "dfCoverEnable", "b"),
    (310, "dfForceAverageZ", "b"),
    (312, "dfGroupRate", "f"),
    (316, "dfLine", "i"),
    (320, "dfLineAdjustMax", "f"),
    (324, "dfLineAdjustMin", "f"),
    (328, "dfLineBack", "f"),
    (332, "dfLineCenterAdjustMax", "f"),
    (336, "dfLineCenterAdjustMin", "f"),
    (340, "dfLineCloseRate", "f"),
    (344, "dfLineRate", "f"),
    (348, "dfLineRate_goalKick", "f"),
    (352, "dfLineWidth_3", "f"),
    (356, "dfLineWidth_4", "f"),
    (360, "dfLineWidth_5", "f"),
    (364, "dfLineWidth_Corner", "f"),
    (368, "dfUserPositionAdjustEnable", "b"),
    (372, "dfUserPositionAdjustRate", "f"),
    (376, "dfUserPositionAdjustTime", "i"),
    (380, "diffRestartX_End", "f"),
    (384, "diffRestartX_Start", "f"),
    (388, "forceDashDistDefence", "f"),
    (392, "forceDashDistOffence", "f"),
    (396, "forceJogDist", "f"),
    (400, "forceWalkDist", "f"),
    (404, "freeKickAdjustRateX_MF", "f"),
    (408, "freeKickAdjustRateZ", "f"),
    (412, "freeKickAdjustRateZ_FW", "f"),
    (416, "freekickAttackAddNum", "i"),
    (420, "freekickAttackForce0", "i"),
    (424, "freekickAttackForce1", "i"),
    (428, "freekickAttackForce2", "i"),
    (432, "fwGroupRate", "f"),
    (436, "gklAdjustRateX", "f"),
    (440, "gklAdjustRateZ_DF", "f"),
    (444, "gklAdjustRateZ_FW", "f"),
    (448, "gklAdjustRateZ_MF", "f"),
    (452, "gklBaseX", "f"),
    (456, "gklBaseZRate", "f"),
    (460, "gklDefenceBackRate", "f"),
    (464, "gklSupportRate", "f"),
    (468, "gklWidthZ", "f"),
    (472, "gksAdjustRateX", "f"),
    (476, "gksAdjustRateZ_DF", "f"),
    (480, "gksAdjustRateZ_FW", "f"),
    (484, "gksAdjustRateZ_MF", "f"),
    (488, "gksBaseX", "f"),
    (492, "gksBaseZRate", "f"),
    (496, "gksDefenceBackRate", "f"),
    (500, "gksHalfLineRateX_SB", "f"),
    (504, "gksPenaltyLineRateX_DF", "f"),
    (508, "gksSideLineRateZ_SB", "f"),
    (512, "gksWidthZ", "f"),
    (516, "isAdverse", "i"),
    (520, "isUseDashSituation", "b"),
    (524, "jogMfLineScore", "f"),
    (528, "keepDfTargetLineX", "i"),
    (532, "kickoffDfLineX", "f"),
    (536, "lastLineCloseMaxRate", "f"),
    (540, "lengthDf", "f"),
    (544, "lengthDf_Retreat", "f"),
    (548, "lengthDf_SuperRetreat", "f"),
    (552, "lengthOf", "f"),
    (556, "limitBesideWidth", "f"),
    (560, "limitBesideWidth_df", "f"),
    (564, "lineControl", "i"),
    (568, "lowerConnectionParam", "f"),
    (572, "marginPredictionFrameAdjust", "i"),
    (576, "marginPredictionFrameBase", "i"),
    (580, "marginSide", "f"),
    (584, "marginTargetLineX", "f"),
    (588, "margin_restartX", "f"),
    (592, "matchUpContinueRate", "f"),
    (596, "matchUpContinueRate_FW_MF", "f"),
    (600, "maxCloseXRate_FreeKick", "f"),
    (604, "maxWaitTime", "f"),
    (608, "mfAdjustMaxRateX", "f"),
    (612, "mfGroupRate", "f"),
    (616, "mfLineRate", "f"),
    (620, "mfLineScore_adjustMax", "f"),
    (624, "mfPushUpRate", "f"),
    (628, "mfPushUpRate_offencive", "f"),
    (632, "minDistMF_DF", "f"),
    (636, "minDistMF_DF_stratagy_defensive", "f"),
    (640, "minDistMF_FW", "f"),
    (644, "minWidth", "f"),
    (648, "minWidth_GoalKick", "f"),
    (652, "minWidth_stratagy_defensive", "f"),
    (656, "moveStartDist", "f"),
    (660, "numericalRelationDefenceLine", "b"),
    (664, "offenceWideLength", "f"),
    (668, "offenceWideLength_concept_side", "f"),
    (672, "offenceZposiAdjust", "b"),
    (676, "offenceZposiAdjustDist", "f"),
    (680, "onPassCourse", "b"),
    (684, "openSideAdjustZRate", "f"),
    (688, "player_count_backDistX", "f"),
    (692, "player_count_frontDistX", "f"),
    (696, "player_count_height", "f"),
    (700, "pressRate", "f"),
    (704, "pushUpSide", "i"),
    (708, "pushUpSideBack", "i"),
    (712, "rangeX_Throwin_CB", "f"),
    (716, "returnControlSide", "b"),
    (720, "setPlayDeclineRate", "f"),
    (724, "setplayToInplayHeightMax", "f"),
    (728, "setplayToInplayHeightMin", "f"),
    (732, "sideBackPushUpRate", "f"),
    (736, "sideClose", "i"),
    (740, "sideCloseRate", "f"),
    (744, "slide", "b"),
    (748, "slideDistMax", "f"),
    (752, "slideDistMin", "f"),
    (756, "slideJudgeWidthBase", "f"),
    (760, "slideJudgeWidthMargin", "f"),
    (764, "slideKind", "i"),
    (768, "slideWidth", "f"),
    (772, "slowDownArrivalFrame", "i"),
    (776, "slowDownDefenceLine", "i"),
    (780, "slowDownFw", "b"),
    (784, "slowDownMySide", "i"),
    (788, "slowDownPassFrame", "i"),
    (792, "spaceCoverRate", "f"),
    (796, "speedDownRunDist", "f"),
    (800, "speedUpRunDist", "f"),
    (804, "speedUpTargetLine", "i"),
    (808, "supportDist_FreeKick", "f"),
    (812, "targetLineXVariation", "f"),
    (816, "targetLineZVariation", "f"),
    (820, "teamToGroupAdjustEnable", "b"),
    (824, "teamToGroupAdjustEnd", "f"),
    (828, "teamToGroupAdjustStart", "f"),
    (832, "throwinLengthDf", "f"),
    (836, "throwinWidthZ", "f"),
    (840, "transitionOpenZ", "i"),
    (844, "transitionPriorityX", "i"),
    (848, "transitionSec", "i"),
    (852, "transitionSmooth", "i"),
    (856, "upperConnectionParam", "f"),
    (860, "walkMfLineScore", "f"),
    (864, "wideRate", "f"),
    (868, "xposiRateCustom", "b"),
]


def map_basePosition(
    data: BytesIO, offset: int, length: int
) -> dict[str, float | int | bool | None]:
    vals = []
    data.seek(offset)
    for i in range(int(length / 4)):
        match i:
            case (
                15  # adjustGapDfLineAction
                | 18  # adjustSetplay
                | 21  # adjustSlideMoveSpeed
                | 42  # changeDefenceNumberFromSituation
                | 71  # dfAttackWidthForce
                | 90  # dfUserPositionAdjustEnable
                | 128  # isUseDashSituation
                | 163  # numericalRelationDefenceLine
                | 166  # offenceZposiAdjust
                | 168  # onPassCourse
                | 177  # returnControlSide
                | 184  # slide
                | 193  # slowDownFw
                | 203  # teamToGroupAdjustEnable
                | 215  # xposiRateCustom
            ):
                vals += [bool(unpack("<i", data.read(4))[0])]
            # Packed bools: defenceFormationTest1, defenceFormationTest2, dfAdjustZ (3 bytes + 1 padding)
            # Packed bools: dfCoverAdjustX, dfCoverEnable, dfForceAverageZ (3 bytes + 1 padding)
            case 64 | 75:
                vals += list(unpack("3?", data.read(3)))
                data.seek(data.tell() + 1)  # skip padding byte
            # Force int for fields that can be -1 (conv_from_bytes would interpret as NaN float)
            case 107 | 108 | 109:  # freekickAttackForce0/1/2
                vals += [unpack("<i", data.read(4))[0]]
            case _:
                vals += [conv_from_bytes(data.read(4))]

    with open("pes_ai/mappings/21/team/basePosition.txt", "r") as f:
        return dict(zip(f.read().split("\n"), vals))


# lineBreak bool indices (0-based) - stored as 4-byte ints in file, display as bool
LINEBREAK_BOOL_INDICES = [10, 11, 12, 13, 14]  # eyeOff, lastLine, lastLineEnemy, pullAway, pullAwaySide


def map_lineBreak(
    data: BytesIO, offset: int, length: int
) -> dict[str, float | int | bool]:
    """
    Parse lineBreak section.
    - Fields 0-9: 10 floats (4 bytes each)
    - Fields 10-14: 5 packed bools at offsets 48-52 (5 bytes + 3 padding)
    """
    vals = []
    data.seek(offset)
    
    for i in range(10):  # First 10 fields are 4-byte values
        vals.append(conv_from_bytes(data.read(4)))
    
    # 5 packed bools + 3 padding bytes
    vals += list(unpack("5?", data.read(5)))
    data.seek(data.tell() + 3)  # skip 3 padding bytes
    
    with open("pes_ai/mappings/21/team/lineBreak.txt", "r") as f:
        return dict(zip(f.read().split("\n"), vals))


# spaceRun bool indices (0-based) - these are stored as 4-byte ints but display as bool
# From IDA: backwardCurve(4), createPassCourse(51), defenceGap(52), inOut(53), roundTest(54), vitalSupportPrior(59)
SPACERUN_BOOL_INDICES = [4, 51, 52, 53, 54, 59]


def map_spaceRun(
    data: BytesIO, offset: int, length: int
) -> dict[str, float | int | bool]:
    """
    Parse spaceRun section.
    Based on IDA offsets:
    - offset 24: backwardCurve (single BYTE, 1 + 3 padding)
    - offsets 212-215: 4 packed BYTEs (createPassCourse, defenceGap, inOut, roundTest)
    - offset 232: vitalSupportPrior (single BYTE, 1 + 3 padding)
    """
    vals = []
    data.seek(offset)
    
    # Fields 0-3: 4 floats (offsets 8-20)
    for _ in range(4):
        vals.append(conv_from_bytes(data.read(4)))
    
    # Field 4: backwardCurve (single BYTE at offset 24 + 3 padding)
    vals.append(bool(unpack("B", data.read(1))[0]))
    data.seek(data.tell() + 3)
    
    # Fields 5-50: remaining 4-byte values (offsets 28-208)
    for _ in range(46):
        vals.append(conv_from_bytes(data.read(4)))
    
    # Fields 51-54: 4 packed BYTEs at offsets 212-215
    vals += list(unpack("4?", data.read(4)))
    
    # Fields 55-58: 4 ints (offsets 216-228)
    for _ in range(4):
        vals.append(conv_from_bytes(data.read(4)))
    
    # Field 59: vitalSupportPrior (single BYTE at offset 232 + 3 padding)
    vals.append(bool(unpack("B", data.read(1))[0]))
    data.seek(data.tell() + 3)
    
    with open("pes_ai/mappings/21/team/spaceRun.txt", "r") as f:
        return dict(zip(f.read().split("\n"), vals))


def map_defence(
    data: BytesIO, offset: int, length: int
) -> dict[str, float | int]:
    """
    Parse defence section - all 36 fields are 4-byte values (floats/ints).
    No packed bools.
    """
    vals = []
    data.seek(offset)
    
    for _ in range(int(length / 4)):
        vals.append(conv_from_bytes(data.read(4)))
    
    with open("pes_ai/mappings/21/team/defence.txt", "r") as f:
        return dict(zip(f.read().split("\n"), vals))


def map_defenceMark(
    data: BytesIO, offset: int, length: int
) -> dict[str, float | int | bool]:
    """
    Parse defenceMark section - 77 fields.
    Single bool at index 69 (useCoverMoveSpeed at offset 284, 1 byte + 3 padding).
    """
    vals = []
    data.seek(offset)
    
    # Fields 0-68: 69 x 4-byte values (offsets 8-280)
    for _ in range(69):
        vals.append(conv_from_bytes(data.read(4)))
    
    # Field 69: useCoverMoveSpeed (single BYTE at offset 284 + 3 padding)
    vals.append(bool(unpack("B", data.read(1))[0]))
    data.seek(data.tell() + 3)
    
    # Fields 70-76: 7 x 4-byte values (offsets 288-312)
    for _ in range(7):
        vals.append(conv_from_bytes(data.read(4)))
    
    with open("pes_ai/mappings/21/team/defenceMark.txt", "r") as f:
        return dict(zip(f.read().split("\n"), vals))


def map_defenceCover(
    data: BytesIO, offset: int, length: int
) -> dict[str, float | int | bool]:
    """
    Parse defenceCover section - 33 fields.
    Single bool at index 29 (isNearPlayerAssign at offset 124, 1 byte + 3 padding).
    """
    vals = []
    data.seek(offset)
    
    # Fields 0-28: 29 x 4-byte values (offsets 8-120)
    for _ in range(29):
        vals.append(conv_from_bytes(data.read(4)))
    
    # Field 29: isNearPlayerAssign (single BYTE at offset 124 + 3 padding)
    vals.append(bool(unpack("B", data.read(1))[0]))
    data.seek(data.tell() + 3)
    
    # Fields 30-32: 3 x 4-byte values (offsets 128-136)
    for _ in range(3):
        vals.append(conv_from_bytes(data.read(4)))
    
    with open("pes_ai/mappings/21/team/defenceCover.txt", "r") as f:
        return dict(zip(f.read().split("\n"), vals))


def map_support(
    data: BytesIO, offset: int, length: int
) -> dict[str, float | int | list]:
    """
    Parse support section with offset-based style array.
    style[0-19] is 20 ints, stored at offset pointed by 'style' position.
    """
    with open("pes_ai/mappings/21/team/support.txt", "r") as f:
        names = [n for n in f.read().split("\n") if n]
    
    result = {}
    base = offset
    data.seek(offset)
    
    for name in names:
        if name == "style":
            # This is an offset to 20-int array
            style_offset = unpack("<i", data.read(4))[0]
            # Save position, read array, restore
            saved_pos = data.tell()
            data.seek(base + style_offset)
            result["style"] = [unpack("<i", data.read(4))[0] for _ in range(20)]
            data.seek(saved_pos)
        else:
            # Default: float
            result[name] = unpack("<f", data.read(4))[0]
    
    return result


def map_pairAnime(
    data: BytesIO, offset: int, length: int
) -> dict[str, float | int | bool]:
    """
    Parse pairAnime section with offset-based nested structure.
    Main offsets at 0/8/24/28 point to decideTiming/moveContact/stamina/stopContact.
    """
    result = {}
    base = offset
    data.seek(offset)
    
    # Read main structure offsets
    decideTiming_off = unpack("<i", data.read(4))[0]  # [0] = 64
    data.read(4)  # padding
    moveContact_off = unpack("<i", data.read(4))[0]   # [8] = 176
    
    # Packed bools at [12]: bytes [0,1,1,1] and [16]: bytes [1,1,0,0]
    b12 = data.read(4)  # [12]
    b16 = data.read(4)  # [16]
    
    # [20] highballEnable
    result["highballEnable"] = bool(unpack("<i", data.read(4))[0])
    
    # [24] stamina offset, [28] stopContact offset
    stamina_off = unpack("<i", data.read(4))[0]       # [24] = 192
    stopContact_off = unpack("<i", data.read(4))[0]   # [28] = 208
    
    # [32] moveEnable
    result["moveEnable"] = bool(unpack("<i", data.read(4))[0])
    
    # [36-44] zeros/ints
    data.read(12)
    
    # [48] protectButton? or another bool
    result["protectButton"] = bool(unpack("<i", data.read(4))[0])
    
    # [52] protectDribbleTouchNum as float 0.8 - wait, IDA says int. Check again.
    val52 = unpack("<f", data.read(4))[0]  # 0.8
    
    # Remaining main fields
    data.read(8)  # [56-60]
    
    # === Read decideTiming at offset 64 ===
    data.seek(base + decideTiming_off)
    result["decideTiming.moveSec"] = unpack("<f", data.read(4))[0]  # [64] = 0.8
    pes15Test_off = unpack("<i", data.read(4))[0]  # [68] = 48 (relative offset)
    result["decideTiming.stopSec"] = unpack("<f", data.read(4))[0]  # [72] = 0.3
    data.read(8)  # padding
    result["protectDribbleTouchNum"] = unpack("<i", data.read(4))[0]  # [84] = 10
    
    # === Read stamina at offset 192 ===
    data.seek(base + stamina_off)
    result["stamina.effect"] = unpack("<f", data.read(4))[0]  # [192] = 0.5
    result["stamina.max"] = unpack("<f", data.read(4))[0]     # [196] = 0.8
    result["stamina.min"] = unpack("<f", data.read(4))[0]     # [200] = 0.2
    data.read(4)  # padding
    
    # === Read stopContact at offset 208 ===
    data.seek(base + stopContact_off)
    result["stopContact.keepBodyAngleSub"] = unpack("<f", data.read(4))[0]  # [208] = 110.0
    result["stopContact.myGoalAngleEnable"] = bool(unpack("<i", data.read(4))[0])  # [212] = 1
    result["stopEnable"] = bool(unpack("<i", data.read(4))[0])  # [216] = 0
    
    # === Read moveContact at offset 176 ===
    data.seek(base + moveContact_off)
    firstAttackEnd_off = unpack("<i", data.read(4))[0]  # [176] = 80
    pes15Move_off = unpack("<i", data.read(4))[0]       # [180] = 144
    
    # Read firstAttackEnd at offset 80
    data.seek(base + firstAttackEnd_off)
    result["moveContact.firstAttackEnd.enable"] = bool(unpack("<i", data.read(4))[0])
    result["moveContact.firstAttackEnd.paraDiff"] = unpack("<i", data.read(4))[0]
    
    # Read pes15TestMoveContact at offset 144
    data.seek(base + pes15Move_off)
    result["moveContact.pes15TestMoveContact.enable"] = bool(unpack("<i", data.read(4))[0])
    defRot_off = unpack("<i", data.read(4))[0]  # offset to defenceIdealRot
    dropOut_off = unpack("<i", data.read(4))[0]  # offset to dropOut
    packed = data.read(4)  # packed bools [1,1,0,0]
    result["moveContact.pes15TestMoveContact.neutralEnd"] = bool(packed[0])
    speedDiff_off = unpack("<i", data.read(4))[0]  # offset to speedDiff
    result["moveContact.pes15TestMoveContact.tackleResultSetAnime"] = bool(unpack("<i", data.read(4))[0])
    result["moveContact.pes15TestMoveContact.calcType"] = unpack("<i", data.read(4))[0]
    
    # Read pes15TestDecideTiming using relative offset from decideTiming
    data.seek(base + decideTiming_off + pes15Test_off)
    result["decideTiming.pes15TestDecideTiming.enable"] = bool(unpack("<i", data.read(4))[0])
    result["decideTiming.pes15TestDecideTiming.maxSec"] = unpack("<f", data.read(4))[0]
    result["decideTiming.pes15TestDecideTiming.minSec"] = unpack("<f", data.read(4))[0]
    
    # Read defenceIdealRot
    data.seek(base + defRot_off)
    result["moveContact.pes15TestMoveContact.defenceIdealRot.margin"] = unpack("<f", data.read(4))[0]
    result["moveContact.pes15TestMoveContact.defenceIdealRot.max"] = unpack("<f", data.read(4))[0]
    result["moveContact.pes15TestMoveContact.defenceIdealRot.min"] = unpack("<f", data.read(4))[0]
    result["moveContact.pes15TestMoveContact.defenceIdealRot.paraDown"] = unpack("<f", data.read(4))[0]
    
    # Read dropOut
    data.seek(base + dropOut_off)
    result["moveContact.pes15TestMoveContact.dropOut.enable"] = bool(unpack("<i", data.read(4))[0])
    result["moveContact.pes15TestMoveContact.dropOut.minSec"] = unpack("<f", data.read(4))[0]
    
    # Read speedDiff
    data.seek(base + speedDiff_off)
    result["moveContact.pes15TestMoveContact.speedDiff.paraDown"] = unpack("<f", data.read(4))[0]
    result["moveContact.pes15TestMoveContact.speedDiff.value"] = unpack("<f", data.read(4))[0]
    
    # protectAuto1-5 from packed bools at [12] and [16]
    result["protectAuto1"] = bool(b12[1])
    result["protectAuto2"] = bool(b12[2])
    result["protectAuto3"] = bool(b12[3])
    result["protectAuto4"] = bool(b16[0])
    result["protectAuto5"] = bool(b16[1])
    
    return result


def map_diagonalRun(
    data: BytesIO, offset: int, length: int
) -> dict[str, float | int]:
    """
    Parse diagonalRun section - 21 fields: 20 floats + 1 int (scoreMin).
    """
    with open("pes_ai/mappings/21/team/diagonalRun.txt", "r") as f:
        names = [n for n in f.read().split("\n") if n]
    
    vals = []
    data.seek(offset)
    
    for i in range(int(length / 4)):
        if i == 20:  # scoreMin is int
            vals.append(unpack("<i", data.read(4))[0])
        else:
            vals.append(unpack("<f", data.read(4))[0])
    
    return dict(zip(names, vals))


def map_overlap(
    data: BytesIO, offset: int, length: int
) -> dict[str, float | int]:
    """
    Parse overlap section - 7 fields: 2 ints, 4 floats, 1 int.
    """
    with open("pes_ai/mappings/21/team/overlap.txt", "r") as f:
        names = [n for n in f.read().split("\n") if n]
    
    vals = []
    data.seek(offset)
    
    for i in range(int(length / 4)):
        if i in [0, 1, 6]:  # addCount, addCount_adverse, style are ints
            vals.append(unpack("<i", data.read(4))[0])
        else:
            vals.append(unpack("<f", data.read(4))[0])
    
    return dict(zip(names, vals))
