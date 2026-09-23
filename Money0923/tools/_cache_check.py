import sqlite3

c = sqlite3.connect("data/eval_cache.db")
print("rows:", c.execute("SELECT COUNT(*) FROM eval_cache").fetchone()[0])
print("legacy(epoch=''):", c.execute(
    "SELECT COUNT(*) FROM eval_cache WHERE epoch IS NULL OR epoch=''").fetchone()[0])
print("by_epoch:", c.execute(
    "SELECT COALESCE(epoch,'<null>') e, COUNT(*) FROM eval_cache GROUP BY epoch").fetchall())
try:
    print("meta:", c.execute("SELECT v FROM cache_meta").fetchall())
except Exception as e:
    print("meta: none", e)
