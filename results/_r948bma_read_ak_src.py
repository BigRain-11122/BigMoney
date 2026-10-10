import akshare as ak, inspect
src = inspect.getsource(ak.repo_rate_hist)
print(src[:2600])
print('=====INTERBANK=====')
src2 = inspect.getsource(ak.rate_interbank)
print(src2[:2200])
