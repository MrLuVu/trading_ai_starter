import argparse, joblib
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import roc_auc_score
from ..features.make_features import add_basic_features

def main(csv_path: str, out_model: str = "models/model.pkl", out_scaler: str = "models/scaler.pkl"):
    df = pd.read_csv(csv_path)
    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"])
    df = add_basic_features(df).dropna()
    # Label binaria semplice: segno del ritorno a 10 barre
    H = 10
    df["y"] = (df["Close"].shift(-H) > df["Close"]).astype(int)
    df = df.dropna()

    X = df[["ret1","ret5","rsi14","atr14","%b","tod"]].values
    y = df["y"].values

    tss = TimeSeriesSplit(n_splits=5)
    aucs = []
    for tr, te in tss.split(X):
        from sklearn.exceptions import ConvergenceWarning
        import warnings
        warnings.filterwarnings("ignore", category=ConvergenceWarning)

        scaler = StandardScaler().fit(X[tr])
        Xt, Xe = scaler.transform(X[tr]), scaler.transform(X[te])
        model = LogisticRegression(max_iter=1000).fit(Xt, y[tr])
        p = model.predict_proba(Xe)[:,1]
        from sklearn.metrics import roc_auc_score
        aucs.append(roc_auc_score(y[te], p))
    print("AUC media:", sum(aucs)/len(aucs))

    scaler = StandardScaler().fit(X)
    model = LogisticRegression(max_iter=1000).fit(scaler.transform(X), y)
    joblib.dump(model, out_model)
    joblib.dump(scaler, out_scaler)
    print("Salvato", out_model, out_scaler)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="data/EURUSD_M5.csv")
    ap.add_argument("--out_model", default="models/model.pkl")
    ap.add_argument("--out_scaler", default="models/scaler.pkl")
    args = ap.parse_args()
    main(args.csv, args.out_model, args.out_scaler)
