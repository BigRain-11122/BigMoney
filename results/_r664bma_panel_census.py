import os, glob
import pandas as pd

files = sorted(glob.glob('data/daily/*.csv'))
print('daily panel files:', len(files))
rows = []
for f in files:
    try:
        df = pd.read_csv(f, usecols=[0, 1])
        n = len(df)
        code = os.path.basename(f).replace('.csv', '')
        rows.append((code, n, str(df.iloc[0, 0])[:10], str(df.iloc[-1, 0])[:10]))
    except Exception as e:
        print('ERR', f, e)
rows.sort(key=lambda r: -r[1])
print('top 15 by history length:')
for r in rows[:15]:
    print(' ', r)
print('short 5:', rows[-5:])
print('with >=500 bars:', sum(1 for r in rows if r[1] >= 500))
