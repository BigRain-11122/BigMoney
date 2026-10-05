{
 "gate": "r763 W151 band gate",
 "legs": {
  "leg0": {
   "rows": 148,
   "tail": "W150",
   "owner_rows": 140,
   "bma_rows": 66,
   "ordinal": 141,
   "bma_ordinal": 67
  },
  "leg0b": {
   "own_seat_on_origin": true,
   "other_seats": 0,
   "seat_commit": "f8e1306c8 published (r763 pre-seat push) + 351170f89 self-ack inbox->processed move (r763 same-window; zero behind-signal)"
  },
  "leg1": {
   "A": [
    347004,
    349003
   ],
   "hops_A": 1,
   "B": [
    349004,
    349203
   ],
   "hops_B": 1,
   "parity_with_probe": true,
   "B_hop_chain": [
    {
     "hop": 1,
     "window": [
      347004,
      347203
     ],
     "jump_to": 349004
    }
   ]
  },
  "leg2": {
   "conflicts": 0,
   "origin_vacancy": true
  },
  "leg3": {
   "W152p_A": "349004..351003",
   "hops_A": 0,
   "W152p_B": "349204..349403",
   "hops_B": 0,
   "W152p_B_lands_inside_W152p_A": true,
   "note": "naive-B-inside-naive-A; the registered W151 B band 349_004..349_203 will refuse the naive W152 A window; W152 freezer MUST re-derive on the post-W151 universe AND reserve the own-wave A window when deriving B (W141 precedent, leg2 law, E36 staircase card)"
  }
 },
 "verdict": "ADMIT",
 "bands": {
  "A": "347004_349003",
  "B": "349004_349203"
 }
}