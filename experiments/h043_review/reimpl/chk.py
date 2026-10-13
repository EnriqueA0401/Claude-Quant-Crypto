import pickle,pandas as pd
bars,fund=pickle.load(open('panel.pkl','rb'))
def show(s,a,b):
    d=bars[s].loc[a:b]; print(s); print(d[['open','high','low','close','quote_volume']].to_string(float_format=lambda x:f'{x:.5g}'))
    f=fund[s].loc[a:b]; dt=f.index.to_series().diff().dt.total_seconds().div(3600)
    print(f'  funding n={len(f)} sum={f.sum():.4f} min={f.min():.4f} max={f.max():.4f} interval_h={sorted(dt.dropna().unique())[:5]}')
    print('  daily funding sums:', f.groupby(f.index.date).sum().round(4).to_dict())
show('PIPPINUSDT','2025-11-20','2025-12-22')
show('SIRENUSDT','2026-03-12','2026-03-24')
show('RIVERUSDT','2026-01-16','2026-02-02')
show('DEXEUSDT','2026-07-18','2026-07-28')
show('LABUSDT','2026-05-30','2026-06-09')
