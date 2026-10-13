import sys, zipfile, io, glob
import pandas as pd, numpy as np
D = sys.argv[1]
def load(sym):
    fs = sorted(glob.glob(f"{D}/{sym}-1m-*.zip")); out = []
    for f in fs:
        with zipfile.ZipFile(f) as z:
            df = pd.read_csv(io.BytesIO(z.read(z.namelist()[0])), header=None)
        if not str(df.iloc[0, 0]).isdigit(): df = df.iloc[1:]
        df = df.iloc[:, :11].astype(float); df.columns = ["t","o","h","l","c","v","ct","qv","n","tbb","tbq"]
        df.index = pd.to_datetime(df.t.astype("int64"), unit="ms", utc=True); out.append(df)
    return pd.concat(out).sort_index()
trades = [("PIPPINUSDT","2025-11-24","2025-12-01"),("PIPPINUSDT","2025-12-08","2025-12-15"),("SIRENUSDT","2026-03-16","2026-03-23"),
          ("RIVERUSDT","2026-01-19","2026-01-26"),("LABUSDT","2026-05-25","2026-06-01"),("LABUSDT","2026-06-01","2026-06-08"),("ALPACAUSDT","2025-04-28","2025-05-05")]
for s, a, b in trades:
    k = load(s); A, B = pd.Timestamp(a, tz="UTC"), pd.Timestamp(b, tz="UTC")
    e = k.loc[A:A + pd.Timedelta("4min")]; x = k.loc[B:B + pd.Timedelta("4min")]
    p0 = k.loc[A].o if A in k.index else np.nan
    vw0 = e.qv.sum() / e.v.sum(); hl0 = (e.h.max() / e.l.min() - 1)
    if len(x):
        p1 = k.loc[B].o; vw1 = x.qv.sum() / x.v.sum()
    else:
        last = k.loc[:B].dropna(); last = last[last.v > 0].iloc[-5:]; p1 = last.c.iloc[-1]; vw1 = last.qv.sum() / last.v.sum()
        print("   last trade", last.index[-1], "last 5m range", round(last.l.min(),4), round(last.h.max(),4))
    print(f"{s} {a}: open {p0:.5g} vwap5m {vw0:.5g} ({vw0/p0-1:+.2%}) 5m hi/lo {hl0:.2%} 1m qv@00:00 {k.loc[A].qv:,.0f} | exit open {p1:.5g} vwap5m {vw1:.5g} | ret open {p1/p0-1:+.1%} ret vwap {vw1/vw0-1:+.1%}")
k = load("ALPACAUSDT"); print(k.loc["2025-04-30 20:00":"2025-05-02"].query("v>0").tail(8)[["o","h","l","c","qv"]])
