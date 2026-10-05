"""Build the FairFund need-only probe (D3): FairFund appeals whose material situation is
held fixed across causal framings, re-asked with our need/deservingness questions.

Within a scenario, framings change the cause paragraph only; savings/eviction wording is shared.
Caveat: no_cause/structural also contain "doing my best to bring in additional income",
which self_cause/stigma variants lack -> an effort cue co-varies with framing (report it).
"""
import json
import pandas as pd

SRC = "/workspace/welfare-need-naacl/data/external/fairfund-bench/data/stimuli.csv"
OUT = "/workspace/welfare-need-naacl/data/external/fairfund_need_probe.jsonl"

s = pd.read_csv(SRC)
# Two fixed name cells so name effects are held constant across framings.
keep = s[(s.name_rank == 1) & (((s.race == "White") & (s.gender == "Male")) | ((s.race == "Black") & (s.gender == "Female")))]
with open(OUT, "w") as f:
    for r in keep.itertuples():
        f.write(json.dumps(dict(profile_id=f"ff__{r.stimulus_id}", base_id=f"ff__{r.scenario_id}__{r.race}{r.gender}",
                                split="external", format="fairfund", framing=r.framing, category=r.category,
                                scenario_id=r.scenario_id, race=r.race, gender=r.gender, text=r.text,
                                source="FairFund-Bench v1.1.0 stimuli.csv (CC BY 4.0), unmodified")) + "\n")
print(len(keep), "rows ->", OUT)
