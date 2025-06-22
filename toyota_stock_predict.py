import pandas as pd
import numpy as np
import yfinance as yf
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

# 1. データ取得
ticker = "7203.T"
data = yf.download(ticker, period="5y")
data = data[['Close']]
data = data.fillna(data.mean())

# 2. 特徴量とラベルの作成
X = []
y = []
window_size = 60
for i in range(window_size, len(data)):
    X.append(data['Close'].values[i-window_size:i])
    y.append(data['Close'].values[i])
X = np.array(X)
y = np.array(y)

# 3. データ分割
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

# 4. モデル定義
models = {
    "線形回帰": LinearRegression(),
    "ランダムフォレスト": RandomForestRegressor(n_estimators=100, random_state=42),
    "サポートベクター回帰": SVR()
}

results = {}

# 5. 各モデルで学習・予測・評価
for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    latest_X = data['Close'].values[-window_size:].reshape(1, -1)
    predicted_price = model.predict(latest_X)[0]
    results[name] = {
        "MSE": mse,
        "予測値": predicted_price
    }
    print(f"{name}のテストMSE: {mse:.2f}")
    print(f"{name}による明日の予測終値: {predicted_price:.2f} 円\n")

# 6. 総合コメント
print("【総合コメント】")
preds = [v["予測値"] for v in results.values()]
avg_pred = np.mean(preds)
print(f"3モデルの平均予測終値: {avg_pred:.2f} 円")

diff = max(preds) - min(preds)
if diff < 10:
    print("→ 3つのモデルの予測値はほぼ一致しており、明日の株価は大きな変動がないと予想されます。")
else:
    print("→ モデル間で予測値に差が見られるため、明日の株価には不確実性があります。複数モデルの結果を参考に慎重な判断が必要です。") 