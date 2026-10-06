"""r781 bm-b: dump current V entry block (shared + lane) for surgery anchoring."""
import json

def dump_block(path):
    raw = open(path, encoding='utf-8', newline='').read()
    i = raw.find('"FUND-VALUE-P1-NULLS"')
    assert i > 0, f"V entry id not found in {path}"
    j = raw.rfind('{', 0, i)
    depth = 0; k = j
    while k < len(raw):
        if raw[k] == '{':
            depth += 1
        elif raw[k] == '}':
            depth -= 1
            if depth == 0:
                break
        k += 1
    block = raw[j:k+1]
    print(f"=== {path}: CRLF={block.count(chr(13)+chr(10))} "
          f"LF-only={block.count(chr(10))-block.count(chr(13))} ===")
    print(block)
    print()

dump_block('results/runnable_pool.json')
dump_block('results/runnable_pool.bm-b.json')
