import json

hof = json.loads(open(r"E:\Money\results\halloffame.json", encoding="utf-8").read())
print(f"HOF entries: {len(hof)}")
for e in hof[:8]:
    print(f"  val_fit={e['val_fit']:+.3f} ret={e['val_ret']*100:+.1f}% "
          f"sharpe={e['val_sharpe']:+.2f} dd={e['val_maxdd']*100:.0f}% "
          f"trades={e['val_trades']} window={e['window'][0]}~{e['window'][1]}")
live = json.loads(open(r"E:\Money\results\live_genome.json", encoding="utf-8").read())
print("live champ: fit", live.get("fit"), "rounds", live.get("rounds"),
      "hof_best_val", live.get("hof_best_val"))
