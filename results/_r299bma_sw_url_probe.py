import akshare as ak, inspect, re
src = inspect.getsource(ak.sw_index_first_info)
print("first_info URLs:", re.findall(r'https?://[^"\']+', src))
src2 = inspect.getsource(ak.stock_industry_clf_hist_sw)
print("clf_hist URLs:", re.findall(r'https?://[^"\']+', src2))
