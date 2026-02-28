from io import BytesIO
from struct import unpack

from pes_ai.utils import conv_from_bytes

one_byte_bools = []


def map_pesSmart(
    data: BytesIO, offset: int, length: int
) -> dict[str, float | int | bool]:
    """
    Parse pesSmart section with nested offset structure.
    [0] = InplayTapPassCheckSec
    [4-56] = offsets to nested sections, each may contain sub-offsets
    """
    result = {}
    base = offset
    
    data.seek(offset)
    result["InplayTapPassCheckSec"] = unpack("<f", data.read(4))[0]
    
    # === UEFAShootFreekick (offset pointer at [4] -> 208) ===
    # UEFAShootFreekick container at 208 has sub-offsets:
    # [208]=64 (clickArea), [212]=80 (curve), [216]=enable bool, [220]=144 (shootHeightFromSwipeSpeed), [224]=176 (speed)
    
    # clickArea at offset 64
    data.seek(base + 64)
    result["UEFAShootFreekick.clickArea.h"] = unpack("<f", data.read(4))[0]  # 240
    result["UEFAShootFreekick.clickArea.up"] = unpack("<f", data.read(4))[0]  # -70
    result["UEFAShootFreekick.clickArea.w"] = unpack("<f", data.read(4))[0]  # 240
    
    # curve at offset 80
    data.seek(base + 80)
    result["UEFAShootFreekick.curve.addKickRot"] = unpack("<f", data.read(4))[0]  # 4.0
    result["UEFAShootFreekick.curve.multiply"] = unpack("<f", data.read(4))[0]  # 1.3
    result["UEFAShootFreekick.curve.reverseCuveRate"] = unpack("<f", data.read(4))[0]  # 0.85
    result["UEFAShootFreekick.curve.swipeDistMax"] = unpack("<f", data.read(4))[0]  # 200
    result["UEFAShootFreekick.curve.swipeDistMin"] = unpack("<f", data.read(4))[0]  # 10
    
    # enable at 216 (inline bool)
    data.seek(base + 216)
    result["UEFAShootFreekick.enable"] = bool(unpack("<i", data.read(4))[0])
    
    # shootHeightFromSwipeSpeed at offset 144
    data.seek(base + 144)
    result["UEFAShootFreekick.shootHeightFromSwipeSpeed.enable"] = bool(unpack("<i", data.read(4))[0])
    result["UEFAShootFreekick.shootHeightFromSwipeSpeed.goalMouseDown"] = unpack("<f", data.read(4))[0]  # 25
    result["UEFAShootFreekick.shootHeightFromSwipeSpeed.goalMouseOver"] = unpack("<f", data.read(4))[0]  # 190
    result["UEFAShootFreekick.shootHeightFromSwipeSpeed.goalMouseUpMax"] = unpack("<f", data.read(4))[0]  # 160
    result["UEFAShootFreekick.shootHeightFromSwipeSpeed.goalMouseUpMin"] = unpack("<f", data.read(4))[0]  # 140
    result["UEFAShootFreekick.shootHeightFromSwipeSpeed.mouseOverValue"] = unpack("<f", data.read(4))[0]  # 0.8
    result["UEFAShootFreekick.shootHeightFromSwipeSpeed.nearStrongEnable"] = bool(unpack("<i", data.read(4))[0])
    # pixcelDist sub-offset at [172]=112
    data.seek(base + 112)
    result["UEFAShootFreekick.shootHeightFromSwipeSpeed.pixcelDist.enable"] = bool(unpack("<i", data.read(4))[0])
    result["UEFAShootFreekick.shootHeightFromSwipeSpeed.pixcelDist.far"] = unpack("<f", data.read(4))[0]
    result["UEFAShootFreekick.shootHeightFromSwipeSpeed.pixcelDist.near"] = unpack("<f", data.read(4))[0]
    result["UEFAShootFreekick.shootHeightFromSwipeSpeed.pixcelDist.nearStrong"] = unpack("<f", data.read(4))[0]
    result["UEFAShootFreekick.shootHeightFromSwipeSpeed.pixcelDist.normalMax"] = unpack("<f", data.read(4))[0]
    result["UEFAShootFreekick.shootHeightFromSwipeSpeed.pixcelDist.normalMin"] = unpack("<f", data.read(4))[0]
    
    # speed at offset 176
    data.seek(base + 176)
    result["UEFAShootFreekick.speed.kickNormal"] = unpack("<f", data.read(4))[0]  # 0.45
    result["UEFAShootFreekick.speed.kickStrong"] = unpack("<f", data.read(4))[0]  # 0.7
    result["UEFAShootFreekick.speed.kickWeak"] = unpack("<f", data.read(4))[0]  # 0.15
    result["UEFAShootFreekick.speed.swipeFastMax"] = unpack("<f", data.read(4))[0]  # 60
    result["UEFAShootFreekick.speed.swipeFastMin"] = unpack("<f", data.read(4))[0]  # 45
    result["UEFAShootFreekick.speed.swipeSlowMax"] = unpack("<f", data.read(4))[0]  # 25
    result["UEFAShootFreekick.speed.swipeSlowMin"] = unpack("<f", data.read(4))[0]  # 10
    
    # === defenceMarkCalcApproachRate at offset 240 (inline data) ===
    data.seek(base + 240)
    result["defenceMarkCalcApproachRate.custom"] = bool(unpack("<i", data.read(4))[0])  # 1
    result["defenceMarkCalcApproachRate.rate"] = unpack("<f", data.read(4))[0]  # 0.5
    
    # === foul at offset 288: [288]=256 (action), [292]=272 (area) ===
    # action at 256
    data.seek(base + 256)
    result["foul.action.custom"] = bool(unpack("<i", data.read(4))[0])  # 1
    result["foul.action.time"] = unpack("<i", data.read(4))[0]  # 25
    # area at 272
    data.seek(base + 272)
    result["foul.area.custom"] = bool(unpack("<i", data.read(4))[0])  # 1
    result["foul.area.mode"] = unpack("<i", data.read(4))[0]  # 1
    
    # === freekick at offset 336: [336]=304 (adjustedTargetSetplay) ===
    data.seek(base + 304)
    result["freekick.adjustedTargetSetplay.adjustRateMax"] = unpack("<f", data.read(4))[0]
    result["freekick.adjustedTargetSetplay.adjustRateMin"] = unpack("<f", data.read(4))[0]
    result["freekick.adjustedTargetSetplay.custom"] = bool(unpack("<i", data.read(4))[0])
    result["freekick.adjustedTargetSetplay.paraMax"] = unpack("<f", data.read(4))[0]
    result["freekick.adjustedTargetSetplay.paraMin"] = unpack("<f", data.read(4))[0]
    result["freekick.adjustedTargetSetplay.specialist"] = unpack("<f", data.read(4))[0]
    
    # === gk at offset 400: [400]=352 (catchable), [404]=384 (gkPress) ===
    data.seek(base + 352)
    result["gk.catchable.catchableSpeedDefaultMax"] = unpack("<f", data.read(4))[0]
    result["gk.catchable.catchableSpeedDefaultMin"] = unpack("<f", data.read(4))[0]
    result["gk.catchable.catchableSpeedMin"] = unpack("<f", data.read(4))[0]
    result["gk.catchable.custom"] = bool(unpack("<i", data.read(4))[0])
    result["gk.catchable.frontAdjustRate"] = unpack("<f", data.read(4))[0]
    result["gk.catchable.punchableSpeedMax"] = unpack("<f", data.read(4))[0]
    result["gk.catchable.punchableSpeedMin"] = unpack("<f", data.read(4))[0]
    result["gk.catchable.tooNearDist"] = unpack("<f", data.read(4))[0]
    
    data.seek(base + 384)
    result["gk.gkPress.advantageousRateClassical"] = unpack("<f", data.read(4))[0]
    result["gk.gkPress.advantageousRateNormal"] = unpack("<f", data.read(4))[0]
    result["gk.gkPress.advantageousRateOffensive"] = unpack("<f", data.read(4))[0]
    result["gk.gkPress.custom"] = bool(unpack("<i", data.read(4))[0])
    
    # === isAutoKickAfterRun at offset 416 (inline bool) ===
    data.seek(base + 416)
    result["isAutoKickAfterRun.custom"] = bool(unpack("<i", data.read(4))[0])
    
    # === isShouldTurnBeforePass at offset 464: [464]=432 (angle), [468]=1.0 (checkKickPointDist), [472]=448 (dist) ===
    data.seek(base + 432)
    result["isShouldTurnBeforePass.angle.custom"] = bool(unpack("<i", data.read(4))[0])
    result["isShouldTurnBeforePass.angle.max"] = unpack("<f", data.read(4))[0]
    result["isShouldTurnBeforePass.angle.min"] = unpack("<f", data.read(4))[0]
    
    data.seek(base + 468)
    result["isShouldTurnBeforePass.checkKickPointDist"] = unpack("<f", data.read(4))[0]
    
    data.seek(base + 448)
    result["isShouldTurnBeforePass.dist.checkDistMiddle"] = unpack("<f", data.read(4))[0]
    result["isShouldTurnBeforePass.dist.checkDistShort"] = unpack("<f", data.read(4))[0]
    result["isShouldTurnBeforePass.dist.custom"] = bool(unpack("<i", data.read(4))[0])
    
    # === stamina at offset 624: many sub-offsets ===
    # Read stamina container for sub-offsets
    data.seek(base + 624)
    contact_off = unpack("<i", data.read(4))[0]  # 480
    dash_off = unpack("<i", data.read(4))[0]  # 496
    defence_off = unpack("<i", data.read(4))[0]  # 512
    dribble_off = unpack("<i", data.read(4))[0]  # 528
    falldown_off = unpack("<i", data.read(4))[0]  # 544
    jostle_off = unpack("<i", data.read(4))[0]  # 560
    metab_off = unpack("<i", data.read(4))[0]  # 576
    speed_off = unpack("<i", data.read(4))[0]  # 592
    stagger_off = unpack("<i", data.read(4))[0]  # 608
    
    data.seek(base + contact_off)
    result["stamina.contactTired.custom"] = bool(unpack("<i", data.read(4))[0])
    result["stamina.contactTired.value"] = unpack("<f", data.read(4))[0]
    
    data.seek(base + dash_off)
    result["stamina.dashTired.custom"] = bool(unpack("<i", data.read(4))[0])
    result["stamina.dashTired.value"] = unpack("<f", data.read(4))[0]
    
    data.seek(base + defence_off)
    result["stamina.defenceTired.custom"] = bool(unpack("<i", data.read(4))[0])
    result["stamina.defenceTired.value"] = unpack("<f", data.read(4))[0]
    result["stamina.defenceTired.valueOwnSide"] = unpack("<f", data.read(4))[0]
    
    data.seek(base + dribble_off)
    result["stamina.dribbleTired.custom"] = bool(unpack("<i", data.read(4))[0])
    result["stamina.dribbleTired.value"] = unpack("<f", data.read(4))[0]
    
    data.seek(base + falldown_off)
    result["stamina.fallDownTired.custom"] = bool(unpack("<i", data.read(4))[0])
    result["stamina.fallDownTired.value"] = unpack("<f", data.read(4))[0]
    
    data.seek(base + jostle_off)
    result["stamina.jostleTired.custom"] = bool(unpack("<i", data.read(4))[0])
    result["stamina.jostleTired.value"] = unpack("<f", data.read(4))[0]
    
    data.seek(base + metab_off)
    result["stamina.metabolism.custom"] = bool(unpack("<i", data.read(4))[0])
    result["stamina.metabolism.value"] = unpack("<f", data.read(4))[0]
    
    data.seek(base + speed_off)
    result["stamina.speedTired.custom"] = bool(unpack("<i", data.read(4))[0])
    result["stamina.speedTired.value"] = unpack("<f", data.read(4))[0]
    
    data.seek(base + stagger_off)
    result["stamina.staggerTired.custom"] = bool(unpack("<i", data.read(4))[0])
    result["stamina.staggerTired.value"] = unpack("<f", data.read(4))[0]
    
    # === subConcept at offset 688: [688]=672 (longPassLayOff) ===
    data.seek(base + 672)
    result["subConcept.longPassLayOffAndBreakthroughToDefenceLine.checkRot"] = unpack("<f", data.read(4))[0]
    result["subConcept.longPassLayOffAndBreakthroughToDefenceLine.custom"] = bool(unpack("<i", data.read(4))[0])
    
    # === thinkUnitDribbleBreakThrough at offset 704 (inline bool) ===
    data.seek(base + 704)
    result["thinkUnitDribbleBreakThrough.custom"] = bool(unpack("<i", data.read(4))[0])
    
    # === thinkUnitPassCross at offset 752: [752]=720 (buildUpShort), [756]=736 (getTarget) ===
    data.seek(base + 720)
    result["thinkUnitPassCross.buildUpShort.custom"] = bool(unpack("<i", data.read(4))[0])
    result["thinkUnitPassCross.buildUpShort.mode"] = unpack("<i", data.read(4))[0]
    
    data.seek(base + 736)
    result["thinkUnitPassCross.getTarget.custom"] = bool(unpack("<i", data.read(4))[0])
    result["thinkUnitPassCross.getTarget.reverseSideShootRangeAngleSub"] = unpack("<f", data.read(4))[0]
    
    # === thinkUnitPassTarget at offset 768 (inline bool) ===
    data.seek(base + 768)
    result["thinkUnitPassTarget.custom"] = bool(unpack("<i", data.read(4))[0])
    
    # === updateIntention at offset 784 (inline bool) ===
    data.seek(base + 784)
    result["updateIntention.custom"] = bool(unpack("<i", data.read(4))[0])
    
    # === updateThinkList at offset 832: [832]=800 (execSubConcept), [836]=816 (intentionChallenge) ===
    data.seek(base + 800)
    result["updateThinkList.execSubConcept.custom"] = bool(unpack("<i", data.read(4))[0])
    result["updateThinkList.execSubConcept.enemyDist"] = unpack("<f", data.read(4))[0]
    
    data.seek(base + 816)
    result["updateThinkList.intentionChallengeAttackSideCenter.custom"] = bool(unpack("<i", data.read(4))[0])
    
    return result


def map_teamEmotion(
    data: BytesIO, offset: int, length: int
) -> dict[str, float | int | bool | str]:
    """
    Parse teamEmotion.o - has STRING fields (category names).
    
    IDA: 21 categorys[i] with .name (string) and .retry (int),
    plus downPointMin (int) and gage struct (6 ints).
    
    File layout:
    [0] -> categorys_array_offset (16)
    [4] = downPointMin (inline int)
    [8] -> gage_offset (192)
    Categorys: 21 entries × 8 bytes = [name_ptr, retry]
    Gage: 6 consecutive ints (away_lmt, away_max, away_mid, home_lmt, home_max, home_mid)
    """
    result = {}
    base = offset
    
    # Root header
    data.seek(base)
    categorys_off = unpack("<i", data.read(4))[0]
    result["downPointMin"] = unpack("<i", data.read(4))[0]
    gage_off = unpack("<i", data.read(4))[0]
    
    # Read raw bytes for string resolution
    data.seek(base)
    raw = data.read(length)
    
    # Categories: 21 entries, each 8 bytes (name_ptr + retry)
    for i in range(21):
        entry_off = categorys_off + i * 8
        name_ptr = unpack("<i", raw[entry_off:entry_off+4])[0]
        retry = unpack("<i", raw[entry_off+4:entry_off+8])[0]
        
        # Read null-terminated string at name_ptr
        if 0 < name_ptr < len(raw):
            end = raw.index(0, name_ptr)
            name = raw[name_ptr:end].decode('ascii', errors='replace')
        else:
            name = ""
        
        result[f"categorys.{i}.name"] = name
        result[f"categorys.{i}.retry"] = retry
    
    # Gage struct: 6 ints
    gage_data = raw[gage_off:gage_off+24]
    result["gage.away_lmt"] = unpack("<i", gage_data[0:4])[0]
    result["gage.away_max"] = unpack("<i", gage_data[4:8])[0]
    result["gage.away_mid"] = unpack("<i", gage_data[8:12])[0]
    result["gage.home_lmt"] = unpack("<i", gage_data[12:16])[0]
    result["gage.home_max"] = unpack("<i", gage_data[16:20])[0]
    result["gage.home_mid"] = unpack("<i", gage_data[20:24])[0]
    
    return result


def map_pes15Test(
    data: BytesIO, offset: int, length: int
) -> dict[str, float | int | bool | str]:
    """
    Parse pes15Test.o - mixed types with string, packed bytes.
    
    File layout:
    [0]: header  [4]: forceKickMirror  [8]->112: string
    [12]: forceKickCommand  [16]->32: project1vs1  [20]->96: projectKick
    [24]: pad  [28]: stopConcept
    project1vs1@32: [0]=decelThresh, [4]=enable(byte), [5]=loseNoDodge(byte), [8]=pressCheckDist
    projectKick@96: [0]=gageDisp(byte), [4]->48: gageSpeed (9 floats)
    """
    result = {}
    base = offset

    data.seek(base)
    raw = data.read(length)
    n = len(raw)

    # Root inline values
    result["forceKickCommand"] = unpack("<i", raw[0:4])[0]
    result["forceKickMirror"] = bool(raw[4])

    # String at ptr [8]
    str_off = unpack("<i", raw[8:12])[0]
    if 0 < str_off < n:
        end = raw.index(0, str_off) if 0 in raw[str_off:] else n
        result["forceKickanimeName"] = raw[str_off:end].decode('ascii', errors='replace')
    else:
        result["forceKickanimeName"] = ""

    result["pad"] = bool(raw[12])
    result["stopConcept"] = bool(raw[24])

    # project1vs1 section at ptr [16]
    p1v1_off = unpack("<i", raw[16:20])[0]
    if 0 < p1v1_off < n - 12:
        result["project1vs1.decelerateThreshold"] = unpack("<f", raw[p1v1_off:p1v1_off+4])[0]
        result["project1vs1.enable"] = bool(raw[p1v1_off + 4])
        result["project1vs1.loseNoDodgeFlag"] = bool(raw[p1v1_off + 5])
        result["project1vs1.pressCheckStepMoveDistance"] = unpack("<f", raw[p1v1_off+8:p1v1_off+12])[0]
    else:
        result["project1vs1.decelerateThreshold"] = 0.0
        result["project1vs1.enable"] = False
        result["project1vs1.loseNoDodgeFlag"] = False
        result["project1vs1.pressCheckStepMoveDistance"] = 0.0

    # projectKick section at ptr [20]
    pk_off = unpack("<i", raw[20:24])[0]
    if 0 < pk_off < n - 8:
        result["projectKick.gageDisp"] = bool(raw[pk_off])

        # gageSpeed at ptr within projectKick
        gs_off = unpack("<i", raw[pk_off+4:pk_off+8])[0]
        gage_names = ["cross", "fkLongPass", "fkShoot", "fkShortPass", "fkThroughPass",
                      "longPass", "shoot", "shortPass", "throughPass"]
        if 0 < gs_off < n - 36:
            for i, name in enumerate(gage_names):
                result[f"projectKick.gageSpeed.{name}"] = unpack("<f", raw[gs_off+i*4:gs_off+i*4+4])[0]
        else:
            for name in gage_names:
                result[f"projectKick.gageSpeed.{name}"] = 0.0
    else:
        result["projectKick.gageDisp"] = False
        gage_names = ["cross", "fkLongPass", "fkShoot", "fkShortPass", "fkThroughPass",
                      "longPass", "shoot", "shortPass", "throughPass"]
        for name in gage_names:
            result[f"projectKick.gageSpeed.{name}"] = 0.0

    return result


