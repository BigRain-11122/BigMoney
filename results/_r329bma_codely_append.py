# r329 bm-a: CODELY.md pitlaw append (S4, entry-gate four-questions passed) + size check
import io, os

ENTRY = "- [2026-09-27 15:0x r329 bm-a] \u5751\u5f8b\uff1a**\u7ee7\u627f\u6302\u8d77 rebase \u7684\u5b8c\u6210 resolver \u4e09\u4fee\uff08r328 \u6b7b\u4f1a\u8bdd resolve2 \u4ee3\u7801\u5ba1\u83b7\uff0c\u672a\u53ca\u5b9e\u5f39\u5373\u4fee\uff09\u2014\u2014\u2460CODELY.md memory-union \u524d\u7f00\u65ad\u8a00\u5728\u5bf9\u4fa7\u539f\u5730\u6539\u6307\u9488\u884c\uff08r84/r85 \u6279\u6ce8\u4e3a\u8ffd\u52a0\u5f0f\u5185\u5d4c\u7f16\u8f91\uff09\u65f6\u5fc5\u5931\u8d25\uff0c\u6b63\u89e3\u2260\u653e\u5f03\uff1a\u6761\u76ee\u7ea7\u53cc\u5411\u8986\u76d6\u6838\u9a8c\u66ff\u4ee3\u5b57\u8282\u76f4\u62fc\uff08\u4e24\u4fa7\u6bcf\u6761 entry \u884c\u2208tree\u222aarchive+tree \u6bcf\u884c\u6709 blob \u6e90=\u96f6\u5e7b\u5f71\u96f6\u4e22\u5931 r327 \u5f8b+\u6307\u9488\u884c\u53cc\u6279\u6ce8\u5e76\u542b\uff09\u2461daily_report .md \u5b6a\u751f\u975e JSON\u2014\u2014take_newer_json \u76f4\u63a5 json.loads \u5f53\u573a\u5d29\uff1b\u6b63\u89e3=json \u5b6a\u751f\u5148\u6309 generated_at \u53d6\u4fa7\u3001md \u4ece\u540c\u4fa7 blob \u5b57\u8282\u76f4\u62f7\uff08twin-side coupling\uff09\u2462EOL/indent \u955c\u50cf\u63a2\u6d4b\u6e90=base blob\uff08:1:\uff09\u7981\u8bfb\u5e26\u51b2\u7a81\u6807\u8bb0\u7684 worktree \u4ef6\uff08\u6807\u8bb0\u6df7\u6742\u4e24\u4fa7\u884c\u5c3e=\u63a2\u6d4b\u6c61\u67d3\uff0cr85 \u5f8b\u65b0\u9762\uff09\u3002\u6307\u9488=results/_r328bma_resolve3.py\uff0816-UU \u5168\u89e3+CODELY \u53cc\u5411\u6838\u9a8c\u8fc7+rebase continue \u4e00\u6b21\u901a\u8fc7\uff09\u3002**\n"

live = io.open("CODELY.md", encoding="utf-8").read()
if not live.endswith("\n"):
    live += "\n"
live += ENTRY
io.open("CODELY.md", "w", encoding="utf-8", newline="").write(live)

sz = os.path.getsize("CODELY.md")
print("CODELY.md size after append:", sz, "(hard line 10240)", "OK" if sz <= 10240 else "OVER-LINE")
assert sz <= 10240, "over 10KB hard line -- in-window archival required"
