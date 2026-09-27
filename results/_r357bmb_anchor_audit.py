import json, hashlib
r = json.load(open(r'results\census_fusion_s2\w2b_roster.json', encoding='utf-8'))
paths = {
    'w2_roster.json': r'results\census_fusion_s2\w2_roster.json',
    'sina_construct_p1.json': r'results\shortline\sina_construct_p1.json',
    'SINA_MF_PREREG.md': r'research\shortline\SINA_MF_PREREG.md',
    'HEAT_ATTENTION_SPEC.md': r'research\shortline\HEAT_ATTENTION_SPEC.md',
}
for rel, spec in r['artifact_anchors'].items():
    raw = open(paths[rel], 'rb').read()
    lf = hashlib.sha256(raw.replace(b'\r\n', b'\n')).hexdigest()[:12]
    crlf = hashlib.sha256(raw.replace(b'\n', b'\r\n')).hexdigest()[:12]
    specv = spec['sha256_12']
    m = 'LF' if specv == lf else ('CRLF' if specv == crlf else 'NONE')
    print(rel, '| spec=', specv, '| tree-LF=', lf, '| tree-CRLF=', crlf, '| caliber-match:', m)
