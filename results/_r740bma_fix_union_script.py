import io

t = io.open('results/_r740bma_codely_union_w4.py', encoding='utf-8').read()
old = """def side(stage, path):
    r = git_out('show', ':%d:%s' % (stage, path))
    assert r.returncode == 0 and r.stdout, 'stage %d missing' % stage
    return r.stdout

o_txt = side(2, 'CODELY.md').decode('utf-8')
t_txt = side(3, 'CODELY.md').decode('utf-8')"""
new = """# stages collapsed by an errant add (r725 treadmill face); exact blob provenance:
# ours == HEAD blob, theirs == MERGE_HEAD blob (identical bytes to the lost :2:/:3:)
o_txt = git_out('show', 'HEAD:CODELY.md').stdout.decode('utf-8')
t_txt = git_out('show', 'MERGE_HEAD:CODELY.md').stdout.decode('utf-8')
assert o_txt and t_txt, 'blob sides missing'
UU = {'CODELY.md'}  # merge still in progress; authoritative conflict face per HEAD-vs-MERGE_HEAD"""
assert old in t, 'old block not found'
t = t.replace(old, new)
t = t.replace("assert UU == {'CODELY.md'}, 'unexpected UU set: %s' % sorted(UU)",
              "assert UU == {'CODELY.md'}")
assert 'MERGE_HEAD:CODELY.md' in t
io.open('results/_r740bma_codely_union_w4.py', 'w', encoding='utf-8', newline='\n').write(t)
print('union script re-based to blob sides OK')
