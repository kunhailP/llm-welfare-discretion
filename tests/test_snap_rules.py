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
