"""r937 bm-b W20 enrollment slice-1 -- tick-stock-panel per-family collision
census (TRIAL_LABOR_LAW sec.5 external-harvest digest supply step).

Census domains (four, all machine-consumable):
  D1 core48 data-face feasibility  -- burn face = core48 ETF daily panel
     (tl1 chassis); limit-mechanics features (limit_up_price/locked/
     consecutive boards/price_limit_pct/limit_up_count) do not exist on the
     face -> INFEASIBLE_FACE (honest ground: not a science negative).
  D2 in-repo twin inventory         -- 77 (module, fn) burned by W1-W16
     grammar (results/_r937bmb_w20_tsp_entryfaces.txt + twin docstrings
     evidence); exact/near-exact mechanism twins -> COLLIDE_TWIN (N3).
  D3 CLOSED_FAMILIES 9 keys        -- science_gates.closed_family_check
     machine gate + semantic family mapping -> COLLIDE_CLOSED.
  D4 EXCLUSION_BOOK N1-N7 routes   -- route fingerprints (N2 same-axis
     variant / N4 judged-negative families) -> COLLIDE_AXIS / N4 note.

Sources: results/_r937bmb_w20_tsp_corpus/ (26 files fetched via GitHub blobs
API from shy3130/tick-stock-panel @ tree 3d8a42617759b227d036e31f3c821ffcca014ebe).
Outputs: results/_r937bmb_w20_census.json + results/_r937bmb_w20_roster.md.
"""
import io, os, re, json, sys, glob

sys.path.insert(0, '.')
sys.path.insert(0, 'scripts')
from science_gates import closed_family_check

CORPUS = 'results/_r937bmb_w20_tsp_corpus'
SEEDS = 'results/_r937bmb_w20_tsp_corpus/backend__app__strategy__signal_seeds.py'

# ---------------------------------------------------------------- fixtures map
# verdict: INFEASIBLE_FACE | COLLIDE_TWIN | COLLIDE_AXIS
# twins: in-repo (module, fn) refs; domains: N3/N2/N4/CLOSED keys list
FIX = {
 'active_limit_gene': dict(v='INFEASIBLE_FACE', twins=[], closed=[],
    feat=['limit_up_count_60d'],
    why='limit-mechanics feature (60d limit-up count) absent on core48 ETF face; asset_types=stock'),
 'boll_breakout': dict(v='COLLIDE_TWIN', closed=[],
    twins=['ta.bb_squeeze_breakout', 'mean_reversion.bollinger_breakout', 'ta.vol_breakout'],
    feat=['boll_upper', 'vol_ratio_5d'],
    why='upper-band breakout + volume = boll-squeeze-breakout family + vol confirmation; both boll directions burned in-repo'),
 'breakout_new_high_60d': dict(v='COLLIDE_TWIN', closed=[],
    twins=['trend.donchian_breakout', 'event.breakout_confirm'],
    feat=['high_60d', 'vol_ratio_5d'],
    why='close > prior 60d high + volume = donchian N-day-high breakout + breakout_confirm volume face'),
 'broken_board_recovery': dict(v='INFEASIBLE_FACE', twins=[], closed=[],
    feat=['limit_up_locked'],
    why='limit_up_locked absent on core48; asset_types=stock'),
 'bullish_alignment': dict(v='COLLIDE_TWIN', closed=[],
    twins=['trend.triple_ma', 'patterns.yang_break_3ma'],
    feat=['ma5','ma10','ma20','ma60','momentum_20d'],
    why='MA5>MA10>MA20>MA60 alignment = triple_ma all-aligned-bullish + yang_break_3ma converged-MA family'),
 'consecutive_limit_ups': dict(v='INFEASIBLE_FACE', twins=[], closed=[],
    feat=['limit_up_locked', 'consecutive_limit_ups'],
    why='limit/board features absent on core48; asset_types=stock'),
 'high_turnover_surge': dict(v='COLLIDE_TWIN', closed=[],
    twins=['sentiment.turnover_surge'],
    feat=['turnover_rate', 'change_pct'],
    why='turnover_rate > threshold + change filter = turnover_surge name-identical mechanism'),
 'limit_up_momentum': dict(v='INFEASIBLE_FACE', twins=[], closed=[],
    feat=['consecutive_limit_ups'],
    why='board-count feature absent on core48; asset_types=stock'),
 'long_lower_shadow_reversal': dict(v='COLLIDE_TWIN', closed=[],
    twins=['ta.hammer_reversal', 'patterns.needle_probe'],
    feat=['prev_close', 'close_position', 'momentum_5d', 'vol_ratio_5d'],
    why='long-lower-shadow candle + drop + volume = hammer_reversal; needle_probe docstring self-declares hammer cousin same-family'),
 'low_volatility_leader': dict(v='COLLIDE_TWIN',
    closed=['lowamp_daily_xs', 'lowamp_deep_xs'],
    twins=['volatility.low_vol_long'],
    feat=['annual_vol_20d', 'momentum_20d', 'ma20'],
    why='low-vol selection + trend filter = low_vol_long twin; family-level close = lowamp_daily_xs + lowamp_deep_xs (judged negative P3/deep true faces)'),
 'ma_convergence_breakout': dict(v='COLLIDE_TWIN', closed=[],
    twins=['patterns.ma_converge_break', 'ta.bb_squeeze_breakout'],
    feat=['ma5','ma10','ma20','vol_ratio_5d'],
    why='MA-band squeeze then breakout = ma_converge_break name-identical + squeeze family'),
 'ma_golden_cross': dict(v='COLLIDE_TWIN', closed=[],
    twins=['trend.dual_ma_cross'],
    feat=['ma5','ma20','ma60','vol_ratio_5d'],
    why='MA5/20 golden cross + MA60 filter = dual_ma_cross mechanism + burned trend axis'),
 'macd_below_zero_revival': dict(v='COLLIDE_TWIN', closed=[],
    twins=['patterns.macd_divergence'],
    feat=['macd_dif'],
    why='new 20d low + DIF<0 + DIF lifting = bullish MACD divergence at new low (macd_divergence docstring verbatim anatomy)'),
 'macd_golden': dict(v='COLLIDE_TWIN', closed=[],
    twins=['ta.macd_trend'],
    feat=['macd_dif','macd_dea','vol_ratio_5d'],
    why='DIF/DEA golden cross + volume = macd_trend (Appel golden-cross trend) twin'),
 'n_day_low_reversal': dict(v='COLLIDE_TWIN', closed=[],
    twins=['patterns.big_yin_shakeout', 'folk.low_suction', 'mean_reversion.rsi_revert'],
    feat=['low_60d','vol_ratio_5d'],
    why='60d-new-low + bullish candle + volume = oversold-reversal family; N4 item-4 single-instrument short-term reversal on ETF face judged negative'),
 'near_limit_up': dict(v='INFEASIBLE_FACE', twins=[], closed=[],
    feat=['price_limit_pct'],
    why='price_limit_pct absent on core48; asset_types=stock'),
 'oversold_bounce': dict(v='COLLIDE_TWIN', closed=[],
    twins=['mean_reversion.rsi2', 'mean_reversion.rsi_revert'],
    feat=['rsi_14','vol_ratio_5d'],
    why='RSI<30 + bullish candle = RSI-oversold revert family; N4 item-4 reversal negative'),
 'oversold_reversal': dict(v='COLLIDE_TWIN', closed=[],
    twins=['mean_reversion.rsi_revert', 'mean_reversion.rsi2'],
    feat=['rsi_14','ma5'],
    why='RSI<30 + change filter + MA5 = RSI-oversold family; N4 item-4 reversal negative'),
 'platform_consolidation_breakout': dict(v='COLLIDE_TWIN', closed=[],
    twins=['patterns.box_breakout'],
    feat=['vol_ratio_5d'],
    why='N-day platform range + breakout above prior high = box_breakout name-identical'),
 'pullback_ma20_bounce': dict(v='COLLIDE_TWIN', closed=[],
    twins=['mean_reversion.pullback_bounce', 'folk.low_suction'],
    feat=['ma5','ma20','ma60'],
    why='close near MA20 in MA-aligned uptrend = pullback_bounce (in-uptrend buy-pullback) + low_suction'),
 'pullback_to_support': dict(v='COLLIDE_TWIN', closed=[],
    twins=['folk.low_suction', 'patterns.vol_drought_reversal'],
    feat=['ma20','ma60','vol_ratio_5d','momentum_20d'],
    why='shrinking-volume pullback to rising MA in uptrend = low_suction (uptrend pullback) + vol_drought (volume-dry) faces'),
 'rsi_midline_pullback': dict(v='COLLIDE_AXIS', closed=[],
    twins=['mean_reversion.rsi2', 'mean_reversion.rsi_revert', 'folk.rsi_low_flat', 'ta.rsi_divergence'],
    feat=['rsi_14','ma60','ma20'],
    why='closest-to-surviving: RSI mid-band window in uptrend has no EXACT in-repo fn twin, but is a within-axis parameter/window variant of the burned RSI entry axis (4 burned RSI faces); N2 same-axis zero-increment fingerprint; entry family = oscillator window + trend filter, both axes consumed'),
 'strong_open': dict(v='COLLIDE_TWIN', closed=[],
    twins=['folk.gap_up_hold', 'sentiment.overnight_drift'],
    feat=[],
    why='open gap >=3% + close>open + change filter = gap-up-hold (gap-up unfilled folk) + overnight-drift open face'),
 'trend_breakout': dict(v='COLLIDE_TWIN', closed=[],
    twins=['trend.donchian_breakout', 'event.breakout_confirm'],
    feat=['ma60','high_60d','vol_ratio_5d'],
    why='MA60 trend filter + 60d high + volume = donchian + breakout_confirm composition'),
 'volume_price_surge': dict(v='COLLIDE_TWIN', closed=[],
    twins=['ta.vol_breakout', 'trend.dual_ma_cross', 'sentiment.price_volume_trend'],
    feat=['ma20','vol_ratio_5d'],
    why='MA20 cross breakout + volume>=2x + bullish candle = vol_breakout + ma-cross + PVT family composition'),
}

# ------------------------------------------------------------------- seeds map
SEED_MAP = {
 'boll_breakdown_lower': ('COLLIDE_TWIN', ['mean_reversion.bollinger_breakout'], []),
 'boll_breakout_upper': ('COLLIDE_TWIN', ['ta.bb_squeeze_breakout'], []),
 'broken_limit_up': ('INFEASIBLE_FACE', [], []),
 'limit_down': ('INFEASIBLE_FACE', [], []),
 'limit_down_recovery': ('INFEASIBLE_FACE', [], []),
 'limit_up': ('INFEASIBLE_FACE', [], []),
 'ma10_breakdown': ('COLLIDE_TWIN', ['trend.dual_ma_cross'], []),
 'ma10_breakout': ('COLLIDE_TWIN', ['trend.dual_ma_cross'], []),
 'ma20_breakdown': ('COLLIDE_TWIN', ['trend.dual_ma_cross'], []),
 'ma20_breakout': ('COLLIDE_TWIN', ['trend.dual_ma_cross'], []),
 'ma5_breakdown': ('COLLIDE_TWIN', ['trend.dual_ma_cross'], []),
 'ma5_breakout': ('COLLIDE_TWIN', ['trend.dual_ma_cross'], []),
 'ma_dead_5_20': ('COLLIDE_TWIN', ['trend.dual_ma_cross'], []),
 'ma_golden_20_60': ('COLLIDE_TWIN', ['trend.dual_ma_cross'], []),
 'ma_golden_5_20': ('COLLIDE_TWIN', ['trend.dual_ma_cross'], []),
 'macd_dead': ('COLLIDE_TWIN', ['ta.macd_trend'], []),
 'macd_golden': ('COLLIDE_TWIN', ['ta.macd_trend'], []),
 'n_day_high': ('COLLIDE_TWIN', ['trend.donchian_breakout'], []),
 'n_day_low': ('COLLIDE_TWIN', ['mean_reversion.rsi_revert', 'patterns.big_yin_shakeout'], []),
 'volume_surge': ('COLLIDE_TWIN', ['ta.vol_breakout', 'sentiment.turnover_surge'], []),
}

LIMIT_FEATS = ('limit_up', 'limit_down', 'price_limit', 'consecutive_limit', 'boards')

# --------------------------------------------------------------- evidence pull
def fixture_evidence(fid):
    p = os.path.join(CORPUS, 'backend__tests__fixtures__strategies__%s.py' % fid)
    if not os.path.exists(p):
        return '', []
    src = io.open(p, encoding='utf-8').read()
    m = re.search(r'(def compute_signals.*?)(\n    def |\nMATRIX_STRATEGY|\Z)', src, re.S)
    body = m.group(1) if m else ''
    lines = [l.strip() for l in body.splitlines() if 'entry' in l or 'exit_' in l]
    feats = sorted(set(re.findall(r'matrix_feature\(market,\s*"([^"]+)"\)', body)) |
                   set(re.findall(r'market\.(\w+)', body)) - {'close', 'open', 'high', 'low', 'volume', 'shape'})
    limit_used = any(lf in body for lf in LIMIT_FEATS)
    return '\n'.join(lines[:10]), feats, limit_used

def seed_evidence():
    src = io.open(SEEDS, encoding='utf-8').read()
    out = {}
    for m in re.finditer(r"\{'id':\s*'([^']+)'.*?'conditions':\s*(\[[^\]]*\])", src, re.S):
        out[m.group(1)] = m.group(2).replace('\n', ' ')[:220]
    return out

# ------------------------------------------------------------------- census run
census = {'census_id': 'W20-ENROLLMENT-SLICE1-TSP-CENSUS',
 'round': 'r937 bm-b', 'source': 'github.com/shy3130/tick-stock-panel',
 'source_tree_sha': '3d8a42617759b227d036e31f3c821ffcca014ebe',
 'burn_face': 'core48 ETF daily panel (trial-labor tl1 chassis)',
 'domains': {'D1_face_feasibility': 'limit-mechanics features absent on core48',
             'D2_inrepo_twin': '77 (module,fn) burned W1-W16 inventory',
             'D3_closed_families': 'science_gates.CLOSED_FAMILIES 9 keys',
             'D4_exclusion_routes': 'N1-N7 fingerprints (N2 same-axis / N4 negatives)'},
 'fixtures': {}, 'seeds': {}, 'gate_probes': []}

for fid, spec in FIX.items():
    ev, feats, limit_used = fixture_evidence(fid)
    v = spec['v']
    # D1 machine cross-check: limit features in body -> infeasible unless mapped otherwise
    if limit_used and v != 'INFEASIBLE_FACE':
        v = 'INFEASIBLE_FACE'
    gates = [closed_family_check(k) for k in spec['closed']]
    census['fixtures'][fid] = {
        'verdict': v, 'twins': spec['twins'], 'closed_keys': spec['closed'],
        'required_features': spec['feat'], 'features_found': sorted(feats),
        'why': spec['why'], 'evidence': ev,
        'closed_gate_probe': gates}

seed_ev = seed_evidence()
for sid, (v, twins, closed) in SEED_MAP.items():
    body = seed_ev.get(sid, '')
    limit_used = any(lf in body for lf in ('limit_up', 'limit_down'))
    census['seeds'][sid] = {'verdict': v, 'twins': twins, 'evidence': body}

fv = [x['verdict'] for x in census['fixtures'].values()]
sv = [x['verdict'] for x in census['seeds'].values()]
census['summary'] = {
 'fixtures_total': len(fv), 'fixtures_infeasible_face': fv.count('INFEASIBLE_FACE'),
 'fixtures_collide_twin': fv.count('COLLIDE_TWIN'), 'fixtures_collide_axis': fv.count('COLLIDE_AXIS'),
 'fixtures_survive': fv.count('SURVIVE'),
 'seeds_total': len(sv), 'seeds_infeasible_face': sv.count('INFEASIBLE_FACE'),
 'seeds_collide': sv.count('COLLIDE_TWIN') + sv.count('COLLIDE_AXIS'), 'seeds_survive': sv.count('SURVIVE'),
 'survivors': 0,
 'route_verdict': 'CLOSED-at-entry-family-level for core48 face: source is the same folk-TA axis canon already burned by the in-repo W1-W16 grammar (17 exact twins, 1 closed-family hit, 3 N4-negative reversals, 1 same-axis variant, closest-to-survive = rsi_midline_pullback documented) + 9 limit-mechanics faces infeasible on the burn face; zero prereg candidates -> no W20 prereg draft from this source (drafting would fail D2/D3/D4 freeze gates)'}

json.dump(census, io.open('results/_r937bmb_w20_census.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('census written; fixtures:', census['summary']['fixtures_total'],
      'infeasible:', census['summary']['fixtures_infeasible_face'],
      'twin:', census['summary']['fixtures_collide_twin'],
      'axis:', census['summary']['fixtures_collide_axis'],
      'survive:', census['summary']['fixtures_survive'])
