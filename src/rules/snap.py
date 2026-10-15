"""SNAP rules-as-code for gold labels (federal rules, 48 states + DC).

The rule packet shown to models (configs/rule_packet_fy2026.md) states every simplification below, so
gold is unambiguous *relative to the packet*:
- no broad-based categorical eligibility, no state options; actual utility costs (no SUA);
- amounts are exact (Fractions); the only rounding is 30% of net income rounded UP to a whole dollar;
- ABAWD: only paid work or an approved work program counts toward 80 hours/month; independent job
  search does not count.

Parameters: FY2026 official FNS tables (data/external/snap_params/*.pdf, effective 2025-10-01).
ABAWD rules: P.L. 119-21 as read by FNS (ages 18-64; dependent child under 14; homeless, veteran and
former-foster-youth exceptions removed). See lit/why_now_policy.md.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from math import ceil

FY2026 = dict(
    fy=2026,
    net_limit={1: 1305, 2: 1763, 3: 2221, 4: 2680, 5: 3138, 6: 3596, 7: 4055, 8: 4513}, net_add=459,
    gross_limit={1: 1696, 2: 2292, 3: 2888, 4: 3483, 5: 4079, 6: 4675, 7: 5271, 8: 5867}, gross_add=596,
    max_allot={1: 298, 2: 546, 3: 785, 4: 994, 5: 1183, 6: 1421, 7: 1571, 8: 1789}, allot_add=218,
    std_ded={1: 209, 2: 209, 3: 209, 4: 223, 5: 261}, std_ded_6plus=299,
    shelter_cap=744, asset_limit=3000, asset_limit_ed=4500, min_benefit=24,
    earned_ded_rate=Fraction(1, 5), medical_threshold=35, benefit_rate=Fraction(3, 10),
)


def _by_size(table: dict, add: int, n: int) -> int:
    return table[n] if n in table else table[8] + add * (n - 8)


@dataclass
class Member:
    age: int
    disabled: bool = False
    pregnant: bool = False
    medically_unfit: bool = False          # medically certified unfit for work
    cares_for_child_under_14: bool = False
    tribal_member: bool = False            # Indian / Urban Indian / California Indian (P.L. 119-21)
    work_hours_month: int = 0              # paid work + approved work program hours
    countable_months_used: int = 0         # ABAWD countable months already used in the 36-month period

    @property
    def elderly(self) -> bool:
        return self.age >= 60


@dataclass
class Household:
    members: list[Member]
    earned: int = 0                 # monthly gross earned income
    unearned: int = 0               # monthly gross unearned income
    dependent_care: int = 0
    medical_ed: int = 0             # out-of-pocket medical costs of elderly/disabled members
    child_support_paid: int = 0     # legally owed, paid to a non-household member
    shelter: int = 0                # rent/mortgage + property tax + insurance on the home
    utilities: int = 0              # actual heating/cooling, electricity, water, one phone (no internet)
    assets: int = 0
    params: dict = field(default_factory=lambda: FY2026)

    @property
    def size(self) -> int:
        return len(self.members)

    @property
    def has_ed(self) -> bool:
        return any(m.elderly or m.disabled for m in self.members)


def compute(h: Household) -> dict:
    """Full determination chain. Returns every intermediate so tests and prompts can cite steps."""
    p, n = h.params, h.size
    gross = Fraction(h.earned + h.unearned)
    gross_limit = _by_size(p["gross_limit"], p["gross_add"], n)
    gross_pass = True if h.has_ed else gross <= gross_limit

    earned_ded = p["earned_ded_rate"] * h.earned
    std = p["std_ded"].get(n, p["std_ded_6plus"])
    medical_ded = max(Fraction(0), Fraction(h.medical_ed - p["medical_threshold"])) if h.has_ed else Fraction(0)
    adjusted = max(Fraction(0), gross - earned_ded - std - h.dependent_care - medical_ded - h.child_support_paid)

    shelter_costs = Fraction(h.shelter + h.utilities)
    excess = max(Fraction(0), shelter_costs - adjusted / 2)
    shelter_ded = excess if h.has_ed else min(excess, Fraction(p["shelter_cap"]))
    net = max(Fraction(0), adjusted - shelter_ded)
    net_limit = _by_size(p["net_limit"], p["net_add"], n)
    net_pass = net <= net_limit

    asset_limit = p["asset_limit_ed"] if h.has_ed else p["asset_limit"]
    asset_pass = h.assets <= asset_limit

    eligible = gross_pass and net_pass and asset_pass
    max_allot = _by_size(p["max_allot"], p["allot_add"], n)
    contribution = ceil(p["benefit_rate"] * net)
    benefit = max_allot - contribution
    if eligible:
        if n <= 2:
            benefit = max(benefit, p["min_benefit"])
        elif benefit <= 0:
            eligible, benefit = False, 0
    else:
        benefit = 0
    return dict(
        size=n, has_elderly_disabled=h.has_ed,
        gross=gross, gross_limit=gross_limit, gross_pass=gross_pass,
        earned_ded=earned_ded, std_ded=std, dependent_care=h.dependent_care, medical_ded=medical_ded,
        child_support_ded=h.child_support_paid, adjusted=adjusted,
        shelter_costs=shelter_costs, excess_shelter=excess, shelter_ded=shelter_ded,
        net=net, net_limit=net_limit, net_pass=net_pass,
        asset_limit=asset_limit, asset_pass=asset_pass,
        eligible=eligible, max_allot=max_allot, contribution=contribution, benefit=int(benefit),
    )


def abawd(m: Member, household: Household) -> dict:
    """ABAWD time-limit determination for one member for the current month.

    Returns subject (bool), exemption (str|None), meets_work (bool), eligible_this_month (bool).
    A child under 14 must be in the household for the dependent-child exception.
    """
    if not (18 <= m.age <= 64):
        return dict(subject=False, exemption="age", meets_work=None, eligible_this_month=True)
    reasons = [
        ("medically_unfit", m.medically_unfit or m.disabled),
        ("pregnant", m.pregnant),
        ("child_under_14", m.cares_for_child_under_14
         and any(o.age < 14 for o in household.members)),
        ("tribal", m.tribal_member),
        ("works_30h_week", m.work_hours_month >= 130),  # general work-requirement exemption (30 h/week)
    ]
    ex = next((r for r, ok in reasons if ok), None)
    if ex is not None:
        return dict(subject=False, exemption=ex, meets_work=None, eligible_this_month=True)
    meets = m.work_hours_month >= 80
    ok = meets or m.countable_months_used < 3
    return dict(subject=True, exemption=None, meets_work=meets, eligible_this_month=ok)
