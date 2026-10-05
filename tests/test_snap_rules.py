"""Hand-computed checks for src/rules/snap.py (FY2026, 48 states + DC)."""
from fractions import Fraction as F
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from rules.snap import Household, Member, compute, abawd

def test_single_worker_capped_shelter():
    # gross 1500 (earned) -> earned ded 300, std 209 -> adjusted 991
    # shelter 900+150=1050; excess = 1050-495.5 = 554.5 (< cap 744) -> net 436.5
    # 30% of 436.5 = 130.95 -> 131; benefit 298-131 = 167
    r = compute(Household([Member(35)], earned=1500, shelter=900, utilities=150))
    assert r["gross_pass"] and r["adjusted"] == 991 and r["excess_shelter"] == F(1109, 2)
    assert r["net"] == F(873, 2) and r["contribution"] == 131 and r["benefit"] == 167

def test_shelter_cap_applies_without_elderly():
    r = compute(Household([Member(30)], unearned=1000, shelter=1500))
    # adjusted 791; excess 1500-395.5=1104.5 -> capped 744; net 47 -> 30% = 14.1 -> 15; benefit 283
    assert r["shelter_ded"] == 744 and r["net"] == 47 and r["benefit"] == 283

def test_elderly_uncapped_and_gross_exempt():
    h = Household([Member(70)], unearned=1800, shelter=1600, medical_ed=135)
    r = compute(h)
    # gross 1800 > 1696 but elderly -> gross test waived; medical 100; adjusted 1800-209-100=1491
    # excess 1600-745.5 = 854.5 uncapped; net 636.5 <= 1305
    assert r["gross_pass"] and r["medical_ded"] == 100 and r["shelter_ded"] == F(1709, 2)
    assert r["net_pass"] and r["eligible"]

def test_gross_fail_boundary():
    assert compute(Household([Member(30)], earned=1696))["gross_pass"]
    assert not compute(Household([Member(30)], earned=1697))["gross_pass"]

def test_min_benefit_small_household():
    r = compute(Household([Member(30), Member(28)], earned=2200, shelter=300))
    # adjusted 2200-440-209=1551; excess 0; net 1551 <= 1763; 30% = 465.3->466; 546-466=80
    assert r["benefit"] == 80
    r = compute(Household([Member(30), Member(28)], earned=2280))
    # adjusted 1615; 30% = 484.5 -> 485; 546-485 = 61
    assert r["benefit"] == 61

def test_large_household_zero_benefit_ineligible():
    r = compute(Household([Member(40), Member(38), Member(10)], earned=3600, unearned=0))
    # gross 3600 > 2888 -> fail
    assert not r["eligible"] and r["benefit"] == 0

def test_abawd():
    hh = Household([Member(40), Member(8)])
    assert abawd(Member(40, cares_for_child_under_14=True), hh)["exemption"] == "child_under_14"
    alone = Household([Member(40)])
    assert abawd(Member(40, cares_for_child_under_14=True), alone)["subject"]   # no child in household
    assert abawd(Member(63), alone)["subject"]                                   # 18-64 now covered
    assert not abawd(Member(65), alone)["subject"]
    r = abawd(Member(40, work_hours_month=79, countable_months_used=3), alone)
    assert r["subject"] and not r["meets_work"] and not r["eligible_this_month"]
    assert abawd(Member(40, work_hours_month=80, countable_months_used=3), alone)["eligible_this_month"]
    assert abawd(Member(40, countable_months_used=2), alone)["eligible_this_month"]
    assert abawd(Member(40, pregnant=True, countable_months_used=5), alone)["eligible_this_month"]

# Decision table written by hand from the packet's ABAWD section (not derived from snap.py), 2026-10-05.
# Columns: status, child age in household (None = no child), hours, countable months used -> can receive.
ABAWD_TABLE = [
    ("none", None, 72, 3, False), ("none", None, 79, 3, False), ("none", None, 80, 3, True),
    ("none", None, 88, 3, True), ("none", None, 0, 2, True), ("none", None, 129, 3, True),
    ("pregnant", None, 72, 3, True), ("pregnant", None, 0, 3, True),
    ("medical", None, 72, 3, True), ("disabled", None, 0, 3, True),
    ("tribal", None, 0, 3, True),
    ("cares", 9, 72, 3, True), ("cares", 13, 0, 3, True),
    ("cares", 14, 72, 3, False), ("cares", 15, 72, 3, False), ("cares", 15, 88, 3, True),
    ("none", 9, 72, 3, False),          # child present but member not responsible for care
    ("none", None, 130, 3, True),       # 30 h/week exemption
]


def test_abawd_decision_table():
    for status, child, hours, used, want in ABAWD_TABLE:
        m = Member(30, work_hours_month=hours, countable_months_used=used, pregnant=status == "pregnant",
                   medically_unfit=status == "medical", disabled=status == "disabled",
                   tribal_member=status == "tribal", cares_for_child_under_14=status == "cares")
        h = Household([m] + ([Member(child)] if child is not None else []))
        assert abawd(m, h)["eligible_this_month"] == want, (status, child, hours, used)
    for age, want in ((17, True), (18, False), (64, False), (65, True)):   # outside 18-64 -> not subject
        m = Member(age, work_hours_month=0, countable_months_used=3)
        assert abawd(m, Household([m]))["eligible_this_month"] == want, age


def test_pilot_abawd_gold_matches_table():
    """Every ABAWD pilot item: gold equals the hand table rule; income identical across the hours pair."""
    import json
    root = pathlib.Path(__file__).resolve().parents[1]
    rows = [json.loads(l) for l in open(root / "data/rules_pilot/pilot.jsonl")]
    ab = [r for r in rows if r["task"] == "abawd"]
    for r in ab:
        exempt = r["status"] in ("pregnant", "child_under_14", "medical")
        assert r["gold"] == ("YES" if exempt or r["hours"] >= 80 else "NO"), r["item_id"]
        assert r["earned"] == 480 and r["paid_hours"] + r["program_hours"] == r["hours"]
        assert "March 2026" in r["text"] and "(complete)" in r["text"]
