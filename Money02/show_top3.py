"""Decode top-3 HOF genomes: dominant families + risk genes."""
import json

import numpy as np

import config as C
import evolve as EV
import strategies as S

hof = json.loads(open(C.RESULTS_DIR / "halloffame.json", encoding="utf-8").read())
for k, e in enumerate(hof[:3]):
    gp = EV.decode(e["genome"])
    w = np.asarray(gp["w"])
    dom = [f"{S.FAMILIES[j]}({w[:, j].mean()*100:.0f}%)" for j in np.argsort(-w.mean(0))[:3]]
    print(f"#{k+1} 盲测{e['val_ret']*100:+.0f}%({e['window'][0]}~{e['window'][1]}) "
          f"主力={','.join(dom)} K={gp['K']} 止损{gp['stop']*100:.0f}% "
          f"跟踪{gp['trail']*100:.0f}% 持{gp['hold']}日")
