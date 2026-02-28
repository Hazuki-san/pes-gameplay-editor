from io import BytesIO
from struct import unpack

from pes_ai.utils import conv_from_bytes

# Required by editor for bool handling
one_byte_bools = []

def map_motivation(
    data: BytesIO, offset: int, length: int
) -> dict[str, float]:
    with open("pes_ai/mappings/21/player/motivation.txt", "r") as f:
        names = [n for n in f.read().split("\n") if n]
    data.seek(offset + 16)
    vals = [unpack("<f", data.read(4))[0] for _ in range(len(names))]
    return dict(zip(names, vals))


def map_playStyle(
    data: BytesIO, offset: int, length: int
) -> dict[str, int]:
    """
    Parse playStyle section using offset table format.
    """
    with open("pes_ai/mappings/21/player/playStyle.txt", "r") as f:
        names = [n for n in f.read().split("\n") if n]
    
    result = {}
    base = offset
    data.seek(offset)
    
    style_table_offset = unpack("<i", data.read(4))[0]
    data.seek(base + style_table_offset)
    style_offsets = [unpack("<i", data.read(4))[0] for _ in range(22)]
    
    name_idx = 0
    for i, style_offset in enumerate(style_offsets):
        data.seek(base + style_offset)
        for j in range(21):
            if name_idx < len(names):
                result[names[name_idx]] = unpack("<i", data.read(4))[0]
                name_idx += 1
    
    return result


def map_trap(
    data: BytesIO, offset: int, length: int
) -> dict[str, float | int | bool]:
    """
    Parse trap.o using ACTUAL verified offsets from binary analysis.
    
    Actual header (different from old doc!):
    - [0]->112, [4]->128, [8]->144, [12]->160 (autoR2)
    - [16]=1.0 (ballControlRate), [20]=20.0 (ballControlWeekFootDownLimit)
    - [24]->352 (ballForceDirect), [28]->400 (ballInAngle)
    - [32]->416 (busyTrapControl), [36]->464 (cancel)
    - [40]->496 (defenseTrap), [44]->544 (hitAfterCancel)
    - [48]->560 (reachOut), [52]->912 (reactionTrapBall)
    - [56]=0.4 (staggerTrapHeight), [60]->944 (stopTrap)
    - [64]=1 (throughCommandType), [68]->960 (touchAfterSec)
    - [72]=1 (trapChapeuAuto), [76]->992 (trapCutFrame)
    - [80]=257 (trapLoss packed bools)
    
    Values verified via pattern search:
    - autoR2 (0.33, 2.0, 100.0) at 160
    - defenseTrap (0.3, 0.5, 10.0, 1.75) at 496
    - reachOut (50.0, 1.0, 1) at 560
    - cancel.hitBefore.jumpStartFrame (6) at 448
    """
    result = {}
    base = offset
    
    # === Read header ===
    data.seek(base)
    h = [unpack("<i", data.read(4))[0] for _ in range(24)]  # 96 bytes header
    
    # Inline values from header
    data.seek(base + 16)
    result["ballControlRate"] = unpack("<f", data.read(4))[0]
    result["ballControlWeekFootDownLimit"] = unpack("<f", data.read(4))[0]
    data.seek(base + 56)
    result["staggerTrapHeight"] = unpack("<f", data.read(4))[0]
    data.seek(base + 64)
    result["throughCommandType"] = unpack("<i", data.read(4))[0]
    data.seek(base + 72)
    result["trapChapeuAuto"] = bool(unpack("<i", data.read(4))[0])
    
    # trapLoss at [80] - packed bools
    data.seek(base + 80)
    trap_loss_bytes = data.read(4)
    result["trapLoss"] = bool(trap_loss_bytes[0])
    result["trapLossDashOnly"] = bool(trap_loss_bytes[1])
    
    # === afterCollision @ [0]->112 ===
    data.seek(base + 112)
    result["afterCollision.hitAfterFrame"] = unpack("<i", data.read(4))[0]
    # noHit is at internal offset pointer [116]->96
    noHit_off = unpack("<i", data.read(4))[0]
    if 0 < noHit_off < length:
        noHit_bytes = data.read(0)  # don't read yet
        data.seek(base + noHit_off)
        noHit_data = data.read(3)
        result["afterCollision.noHit.foot"] = bool(noHit_data[0])
        result["afterCollision.noHit.reg"] = bool(noHit_data[1])
        result["afterCollision.noHit.thigh"] = bool(noHit_data[2])
    
    # === animeBlend @ [4]->128 ===
    data.seek(base + 128)
    result["animeBlend.changeAnimeBlendRate"] = unpack("<f", data.read(4))[0]
    result["animeBlend.defaultBlendRate"] = unpack("<f", data.read(4))[0]
    result["animeBlend.use"] = bool(unpack("<i", data.read(4))[0])
    
    # === animeCancelFrame @ [8]->144 ===
    data.seek(base + 144)
    result["animeCancelFrame.hitFrameBase"] = bool(unpack("<i", data.read(4))[0])
    result["animeCancelFrame.kickAddTime"] = unpack("<f", data.read(4))[0]
    result["animeCancelFrame.otherAddTime"] = unpack("<f", data.read(4))[0]
    result["animeCancelFrame.use"] = bool(unpack("<i", data.read(4))[0])
    
    # === autoR2 @ [12]->160 (VERIFIED: 0.33, 2.0, 100.0) ===
    data.seek(base + 160)
    result["autoR2.checkEnemyFutureFrame"] = unpack("<f", data.read(4))[0]
    result["autoR2.checkSectorDist"] = unpack("<f", data.read(4))[0]
    result["autoR2.checkSectorWidth"] = unpack("<f", data.read(4))[0]
    
    # === ballForceDirect @ [24]->352 ===
    data.seek(base + 352)
    result["ballForceDirect.blendStartAfterFrame"] = unpack("<i", data.read(4))[0]
    bsf_off = unpack("<i", data.read(4))[0]  # blendStartFrame offset
    bss_off = unpack("<i", data.read(4))[0]  # blendStartSpeed offset
    burst_off = unpack("<i", data.read(4))[0]  # burstSetting offset
    cf_off = unpack("<i", data.read(4))[0]  # cancelFrame offset
    result["ballForceDirect.cancelFrameOffsetPos"] = bool(unpack("<i", data.read(4))[0])
    kb_off = unpack("<i", data.read(4))[0]  # kickBasis offset
    result["ballForceDirect.rateCollisionSpin"] = unpack("<f", data.read(4))[0]
    rd_off = unpack("<i", data.read(4))[0]  # runDashSetting offset
    result["ballForceDirect.use"] = bool(unpack("<i", data.read(4))[0])
    
    # ballForceDirect sub-sections
    if 0 < bsf_off < 1008:
        data.seek(base + bsf_off)
        for suffix in ["offsetPos_Dash_Dash", "offsetPos_Dash_Idle", "offsetPos_Dash_Run",
                       "offsetPos_Idle_Dash", "offsetPos_Idle_Idle", "offsetPos_Idle_Run",
                       "offsetPos_Run_Idle", "offsetPos_Run_Run", "offsetPos_Run_dash"]:
            result[f"ballForceDirect.blendStartFrame.{suffix}"] = unpack("<f", data.read(4))[0]
    
    if 0 < bss_off < 1008:
        data.seek(base + bss_off)
        result["ballForceDirect.blendStartSpeed.burst"] = unpack("<f", data.read(4))[0]
        result["ballForceDirect.blendStartSpeed.dashOfRun"] = unpack("<f", data.read(4))[0]
        result["ballForceDirect.blendStartSpeed.speed_0"] = unpack("<f", data.read(4))[0]
        result["ballForceDirect.blendStartSpeed.speed_15"] = unpack("<f", data.read(4))[0]
        result["ballForceDirect.blendStartSpeed.speed_28"] = unpack("<f", data.read(4))[0]
        result["ballForceDirect.blendStartSpeed.use"] = bool(unpack("<i", data.read(4))[0])
    
    if 0 < burst_off < 1008:
        data.seek(base + burst_off)
        result["ballForceDirect.burstSetting.max"] = unpack("<f", data.read(4))[0]
        result["ballForceDirect.burstSetting.min"] = unpack("<f", data.read(4))[0]
        result["ballForceDirect.burstSetting.ratio"] = unpack("<f", data.read(4))[0]
    
    if 0 < cf_off < 1008:
        data.seek(base + cf_off)
        for suffix in ["offsetPos_Dash_Dash", "offsetPos_Dash_Idle", "offsetPos_Dash_Run",
                       "offsetPos_Idle_Dash", "offsetPos_Idle_Idle", "offsetPos_Idle_Run",
                       "offsetPos_Run_Idle", "offsetPos_Run_Run", "offsetPos_Run_dash"]:
            result[f"ballForceDirect.cancelFrame.{suffix}"] = unpack("<f", data.read(4))[0]
    
    if 0 < kb_off < 1008:
        data.seek(base + kb_off)
        result["ballForceDirect.kickBasis.offsetPos_Dash"] = unpack("<f", data.read(4))[0]
        result["ballForceDirect.kickBasis.offsetPos_Idle"] = unpack("<f", data.read(4))[0]
        result["ballForceDirect.kickBasis.offsetPos_Run"] = unpack("<f", data.read(4))[0]
    
    if 0 < rd_off < 1008:
        data.seek(base + rd_off)
        result["ballForceDirect.runDashSetting.max"] = unpack("<f", data.read(4))[0]
        result["ballForceDirect.runDashSetting.min"] = unpack("<f", data.read(4))[0]
        result["ballForceDirect.runDashSetting.ratio"] = unpack("<f", data.read(4))[0]
    
    # === ballInAngle @ [28]->400 ===
    data.seek(base + 400)
    result["ballInAngle.angleOpen"] = bool(unpack("<i", data.read(4))[0])
    result["ballInAngle.use"] = bool(unpack("<i", data.read(4))[0])
    
    # === busyTrapControl @ [32]->416 ===
    data.seek(base + 416)
    result["busyTrapControl.busyTime"] = unpack("<f", data.read(4))[0]
    result["busyTrapControl.checkMyBallPass"] = bool(unpack("<i", data.read(4))[0])
    result["busyTrapControl.runTrapStopTurnAngle"] = unpack("<f", data.read(4))[0]
    result["busyTrapControl.stopTrapStopTurnAngle"] = unpack("<f", data.read(4))[0]
    result["busyTrapControl.use"] = bool(unpack("<i", data.read(4))[0])
    
    # === cancel @ [36]->464->448 ===
    data.seek(base + 464)
    hitBefore_off = unpack("<i", data.read(4))[0]
    if 0 < hitBefore_off < 1008:
        data.seek(base + hitBefore_off)
        result["cancel.hitBefore.jumpStartFrame"] = unpack("<i", data.read(4))[0]
    
    # === defenseTrap @ [40]->496 (VERIFIED: 0.3, 0.5, 10.0, 1.75) ===
    data.seek(base + 496)
    result["defenseTrap.checkBallHeight"] = unpack("<f", data.read(4))[0]
    result["defenseTrap.checkBallLimitRange"] = unpack("<f", data.read(4))[0]
    result["defenseTrap.checkBallMoveVecY"] = unpack("<f", data.read(4))[0]
    result["defenseTrap.checkDistKeepPlayerToBall"] = unpack("<f", data.read(4))[0]
    custom_off = unpack("<i", data.read(4))[0]
    result["defenseTrap.use"] = bool(unpack("<i", data.read(4))[0])
    if 0 < custom_off < 1008:
        data.seek(base + custom_off)
        result["defenseTrap.custom.angleOut"] = unpack("<f", data.read(4))[0]
        result["defenseTrap.custom.speedOut"] = unpack("<i", data.read(4))[0]
        result["defenseTrap.custom.use"] = bool(unpack("<i", data.read(4))[0])
    
    # === hitAfterCancel @ [44]->544 ===
    data.seek(base + 544)
    result["hitAfterCancel.frameRange"] = unpack("<i", data.read(4))[0]
    result["hitAfterCancel.hitAfterCancelFrameLimit"] = unpack("<i", data.read(4))[0]
    param_off = unpack("<i", data.read(4))[0]
    if 0 < param_off < length:
        data.seek(base + param_off)
        result["hitAfterCancel.parameterRange.max"] = unpack("<i", data.read(4))[0]
        result["hitAfterCancel.parameterRange.min"] = unpack("<i", data.read(4))[0]
    
    # === reachOut @ [48]->560 (VERIFIED: 50.0, 1.0, 1) ===
    data.seek(base + 560)
    result["reachOut.ballSpeed"] = unpack("<f", data.read(4))[0]
    result["reachOut.reach"] = unpack("<f", data.read(4))[0]
    result["reachOut.use"] = bool(unpack("<i", data.read(4))[0])
    
    # === reactionTrapBall @ [52]->912 ===
    # Structure: checkTime, then offset pointers to sub-sections
    # [912]=checkTime, [916]->reactionBoundBall, [920]->reactionEnemyBall,
    # [924]=reactionIK, [928]->reactionOwnBall, [932]=use
    data.seek(base + 912)
    result["reactionTrapBall.checkTime"] = unpack("<f", data.read(4))[0]
    bound_off = unpack("<i", data.read(4))[0]   # 672
    enemy_off = unpack("<i", data.read(4))[0]   # 784
    result["reactionTrapBall.reactionIK"] = bool(unpack("<i", data.read(4))[0])
    own_off = unpack("<i", data.read(4))[0]     # 896
    result["reactionTrapBall.use"] = bool(unpack("<i", data.read(4))[0])
    
    # Helper to read a Ball section (airBall/groundBall -> paraMax/paraMin -> values)
    def read_ball_section(section_name, section_off):
        if not (0 < section_off < 1008):
            return
        # Section has: airBall offset, groundBall offset, use
        data.seek(base + section_off)
        air_off = unpack("<i", data.read(4))[0]
        ground_off = unpack("<i", data.read(4))[0]
        use_val = unpack("<i", data.read(4))[0]
        result[f"reactionTrapBall.{section_name}.use"] = bool(use_val)
        
        for ball_name, ball_off in [("airBall", air_off), ("groundBall", ground_off)]:
            if not (0 < ball_off < 1008):
                continue
            # Ball has: paraMax offset, paraMin offset
            data.seek(base + ball_off)
            max_off = unpack("<i", data.read(4))[0]
            min_off = unpack("<i", data.read(4))[0]
            
            for para_name, para_off in [("paraMax", max_off), ("paraMin", min_off)]:
                if not (0 < para_off < 1008):
                    continue
                # Para has: reactionBallSpeed, reactionTime
                data.seek(base + para_off)
                speed = unpack("<f", data.read(4))[0]
                time = unpack("<f", data.read(4))[0]
                result[f"reactionTrapBall.{section_name}.{ball_name}.{para_name}.reactionBallSpeed"] = speed
                result[f"reactionTrapBall.{section_name}.{ball_name}.{para_name}.reactionTime"] = time
    
    read_ball_section("reactionBoundBall", bound_off)
    read_ball_section("reactionEnemyBall", enemy_off)
    read_ball_section("reactionOwnBall", own_off)
    
    # === stopTrap @ [60]->944 ===
    data.seek(base + 944)
    result["stopTrap.inputTime"] = unpack("<f", data.read(4))[0]
    result["stopTrap.use"] = bool(unpack("<i", data.read(4))[0])
    
    # === touchAfterSec @ [68]->960 ===
    data.seek(base + 960)
    result["touchAfterSec.defence"] = unpack("<f", data.read(4))[0]
    result["touchAfterSec.defenceKeep"] = unpack("<f", data.read(4))[0]
    result["touchAfterSec.offence"] = unpack("<f", data.read(4))[0]
    result["touchAfterSec.shoot"] = unpack("<f", data.read(4))[0]
    result["touchAfterSec.shootSpeedBall"] = unpack("<f", data.read(4))[0]
    
    # === trapCutFrame @ [76]->992 ===
    data.seek(base + 992)
    result["trapCutFrame.default"] = unpack("<i", data.read(4))[0]
    result["trapCutFrame.fast"] = unpack("<i", data.read(4))[0]
    
    return result


def map_ballplayer(
    data: BytesIO, offset: int, length: int
) -> dict[str, float | int | bool]:
    """
    Parse ballplayer.o with large TurnData and touch0 arrays.
    """
    result = {}
    base = offset
    
    data.seek(base)
    feint_off = unpack("<i", data.read(4))[0]
    turn_off = unpack("<i", data.read(4))[0]
    touch_off = unpack("<i", data.read(4))[0]
    
    # Feint section
    data.seek(base + feint_off)
    result["Feint.DataUse"] = unpack("<i", data.read(4))[0]
    result["Feint.disp_area"] = unpack("<i", data.read(4))[0]
    result["Feint.rate"] = unpack("<f", data.read(4))[0]
    
    # TurnData array (1440 entries × 52 bytes)
    turn_fields = [
        ("input_angle", "f"), ("kind0", "i"), ("kind1", "i"),
        ("p0_length_max", "f"), ("p0_length_min", "f"), ("p0_length_mle", "f"),
        ("p0_speed_average", "f"), ("p1_angle_left", "f"), ("p1_angle_mle", "f"),
        ("p1_angle_rigth", "f"), ("p1_length_max", "f"), ("p1_length_min", "f"),
        ("p1_length_mle", "f")
    ]
    
    data.seek(base + turn_off)
    for i in range(1440):
        for name, typ in turn_fields:
            val = unpack(f"<{typ}", data.read(4))[0]
            result[f"TurnData[{i}].{name}"] = val
    
    # touch0 array (7 entries × 28 bytes)
    touch_fields = [
        ("frame_ave", "i"), ("frame_max", "i"), ("frame_min", "i"),
        ("length_ave", "f"), ("length_max", "f"), ("length_min", "f"),
        ("valid_data", "i")
    ]
    
    data.seek(base + touch_off)
    for i in range(7):
        for name, typ in touch_fields:
            val = unpack(f"<{typ}", data.read(4))[0]
            result[f"touch0[{i}].{name}"] = val
    
    return result


def map_ballplayerGk(
    data: BytesIO, offset: int, length: int
) -> dict[str, float]:
    """
    Parse ballplayerGk.o - GK specific ball handling parameters.
    """
    result = {}
    base = offset
    
    data.seek(base)
    clear_off = unpack("<i", data.read(4))[0]
    long_off = unpack("<i", data.read(4))[0]
    short_off = unpack("<i", data.read(4))[0]
    result["limitLineFromPenaltyLine"] = unpack("<f", data.read(4))[0]
    
    # ClearInfo
    data.seek(base + clear_off)
    result["ClearInfo.enemyDist"] = unpack("<f", data.read(4))[0]
    result["ClearInfo.forceKickTime"] = unpack("<f", data.read(4))[0]
    
    # LongPassInfo
    data.seek(base + long_off)
    result["LongPassInfo.forceEnemyDist"] = unpack("<f", data.read(4))[0]
    result["LongPassInfo.forceKickTime"] = unpack("<f", data.read(4))[0]
    result["LongPassInfo.limitLineFromPenaltyLine"] = unpack("<f", data.read(4))[0]
    result["LongPassInfo.rangeFar"] = unpack("<f", data.read(4))[0]
    result["LongPassInfo.rangeNear"] = unpack("<f", data.read(4))[0]
    
    # ShortPassInfo
    data.seek(base + short_off)
    result["ShortPassInfo.courseCheckWidth"] = unpack("<f", data.read(4))[0]
    result["ShortPassInfo.passAngleSubMax"] = unpack("<f", data.read(4))[0]
    result["ShortPassInfo.passDistMax"] = unpack("<f", data.read(4))[0]
    result["ShortPassInfo.rangeFar"] = unpack("<f", data.read(4))[0]
    result["ShortPassInfo.rangeNear"] = unpack("<f", data.read(4))[0]
    result["ShortPassInfo.targetFreeDist"] = unpack("<f", data.read(4))[0]
    
    return result


def map_shoot(
    data: BytesIO, offset: int, length: int
) -> dict[str, float | int | bool]:
    """
    Parse shoot.o - all 52 fields are floats.
    IDA: a1[2] to a1[53], flat float array in runtime.
    File: 10 header pointers -> data sections.
    
    Header layout:
    [0]->advanceLoop (6 floats)
    [4]->controlShootGageMax (6 floats)
    [8]->controlShootGageMid (6 floats)
    [12]->controlShootGageMin (6 floats)
    [16]->control_dy (3 floats)
    [20]->loop (4 floats)
    [24]->normalShootGageMax (6 floats)
    [28]->normalShootGageMid (6 floats)
    [32]->normalShootGageMin (6 floats)
    [36]->normal_dy (3 floats)
    """
    result = {}
    base = offset
    
    # Read header pointers
    data.seek(base)
    ptrs = [unpack("<i", data.read(4))[0] for _ in range(10)]
    
    # advanceLoop (6 floats)
    data.seek(base + ptrs[0])
    result["advanceLoop.distMax"] = unpack("<f", data.read(4))[0]
    result["advanceLoop.distMin"] = unpack("<f", data.read(4))[0]
    result["advanceLoop.heightMaxForGageMax"] = unpack("<f", data.read(4))[0]
    result["advanceLoop.heightMaxForGageMin"] = unpack("<f", data.read(4))[0]
    result["advanceLoop.heightMinForGageMax"] = unpack("<f", data.read(4))[0]
    result["advanceLoop.heightMinForGageMin"] = unpack("<f", data.read(4))[0]
    
    # controlShootGageMax (6 floats)
    data.seek(base + ptrs[1])
    for i in range(6):
        result[f"controlShootGageMax.{i}"] = unpack("<f", data.read(4))[0]
    
    # controlShootGageMid (6 floats)
    data.seek(base + ptrs[2])
    for i in range(6):
        result[f"controlShootGageMid.{i}"] = unpack("<f", data.read(4))[0]
    
    # controlShootGageMin (6 floats)
    data.seek(base + ptrs[3])
    for i in range(6):
        result[f"controlShootGageMin.{i}"] = unpack("<f", data.read(4))[0]
    
    # control_dy (3 floats)
    data.seek(base + ptrs[4])
    result["control_dy.gageMax"] = unpack("<f", data.read(4))[0]
    result["control_dy.gageMin"] = unpack("<f", data.read(4))[0]
    result["control_dy.interpolateRate"] = unpack("<f", data.read(4))[0]
    
    # loop (4 floats)
    data.seek(base + ptrs[5])
    result["loop.angleY"] = unpack("<f", data.read(4))[0]
    result["loop.manualRate"] = unpack("<f", data.read(4))[0]
    result["loop.speedForGageMax"] = unpack("<f", data.read(4))[0]
    result["loop.speedForGageMin"] = unpack("<f", data.read(4))[0]
    
    # normalShootGageMax (6 floats)
    data.seek(base + ptrs[6])
    for i in range(6):
        result[f"normalShootGageMax.{i}"] = unpack("<f", data.read(4))[0]
    
    # normalShootGageMid (6 floats)
    data.seek(base + ptrs[7])
    for i in range(6):
        result[f"normalShootGageMid.{i}"] = unpack("<f", data.read(4))[0]
    
    # normalShootGageMin (6 floats)
    data.seek(base + ptrs[8])
    for i in range(6):
        result[f"normalShootGageMin.{i}"] = unpack("<f", data.read(4))[0]
    
    # normal_dy (3 floats)
    data.seek(base + ptrs[9])
    result["normal_dy.gageMax"] = unpack("<f", data.read(4))[0]
    result["normal_dy.gageMin"] = unpack("<f", data.read(4))[0]
    result["normal_dy.interpolateRate"] = unpack("<f", data.read(4))[0]
    
    return result
