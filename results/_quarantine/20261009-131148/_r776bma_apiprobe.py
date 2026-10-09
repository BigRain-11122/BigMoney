# -*- coding: utf-8 -*-
"""API check: segment_waves signature + event_metrics signature + constants."""
import inspect
import sys

sys.path.insert(0, "scripts")
import theme_wave_segmentation as tseg
import theme_event_library as tlib

print("seg funcs:", [x for x in dir(tseg) if not x.startswith("_")])
print("segment_waves sig:", inspect.signature(tseg.segment_waves))
print("event_metrics sig:", inspect.signature(tlib.event_metrics))
print("PEAK_SEARCH_TD:", tlib.PEAK_SEARCH_TD, "| MINUS20_LINE:", tlib.MINUS20_LINE,
      "| EARLY_WIN:", tlib.EARLY_WIN, "| BREADTH_PANEL:", str(tlib.BREADTH_PANEL)[:80])
print("load_series sig:", inspect.signature(tlib.load_series))
