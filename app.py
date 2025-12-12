import streamlit as st
import pandas as pd
import numpy as np

st.title("ロト7 予想アプリ（L7 Hybrid+Cycle スコアモデル Ver.1）")
st.write("アップロードしたロト7データから、頻度・周期・Hot/Cold を自動分析して予想を生成します。")

# -----------------------------------------
# データアップロード
# -----------------------------------------
uploaded = st.file_uploader("ロト7 CSVファイルをアップロード", type=["csv"])

if uploaded is not None:
    df = pd.read_csv(uploaded)

    st.subheader("📌 読み込んだデータ（先頭）")
    st.write(df.head())

    # ◆ 本数字を抽出（1〜7列目想定）
    main_cols = [c for c in df.columns if "数字" in c]
    data = df[main_cols].copy()

    # -----------------------------------------
    # ① 各数字の出現頻度
    # -----------------------------------------
    freq = data.apply(pd.value_counts).sum(axis=1).sort_index()

    # -----------------------------------------
    # ② 周期スコア（何回空いて出現したか）
    # -----------------------------------------
    last_pos = {n: None for n in range(1, 38)}
    cycle_score = {n: 0 for n in range(1, 38)}
    count = 0

    for _, row in data.iterrows():
        count += 1
        nums = set(row.values)
        for n in range(1, 38):
            if n in nums:
                if last_pos[n] is not None:
                    cycle_score[n] = count - last_pos[n]
                last_pos[n] = count

    # -----------------------------------------
    # ③ Hot / Cold スコア
    # -----------------------------------------
    avg_freq = freq.mean()
    hot_cold = freq - avg_freq  # 正ならHot、負ならCold

    # -----------------------------------------
    # ④ 総合スコア
    # -----------------------------------------
    score = freq.rank() + pd.Series(cycle_score).rank() + hot_cold.rank()

    st.subheader("🔍 スコア上位の数字（参考）")
    st.write(score.sort_values(ascending=False).head())

    # -----------------------------------------
    # ⑤ 予想10口を生成
    # -----------------------------------------
    def generate_one():
        return list(score.sort_values(ascending=False).sample(7, weights=score).index)

    predictions = [sorted(generate_one()) for _ in range(10)]

    st.subheader("🎯 予想（10口）")
    for i, pred in enumerate(predictions, 1):
        st.write(f"**{i}口目**：", " ".join(f"{n:02d}" for n in pred))

    # コピー用（まとめ）
    st.subheader("📋 コピー用まとめ（10口）")
    copy_text = "\n".join(
        " ".join(f"{n:02d}" for n in pred) for pred in predictions
    )
    st.code(copy_text)

else:
    st.info("CSV をアップロードすると予想が生成されます。")
