# -*- coding: utf-8 -*-
"""
Created on Mon Mar 10 10:06:15 2025

@author: user
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.font_manager as fm
import seaborn as sns
import os

def load_data(file_path, metrics):
    df = pd.read_excel(file_path, sheet_name="工作表1")
    for metric, ascending in metrics.items():
        df[f"{metric}_PR"] = df[metric].rank(ascending=ascending, pct=True) * 99
        df[f"{metric}_PR"] = df[f"{metric}_PR"].round().astype(int)
    return df

def plot_radar_chart(player_data, metrics, prop):
    values = player_data[[f"{m}_PR" for m in metrics]].values.flatten()
    labels = metrics.keys()
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    values = np.concatenate((values, [values[0]]))
    angles += angles[:1]
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    color = (0.4, 0.6, 0.8)
    ax.fill(angles, values, color=color, alpha=0.3)
    ax.plot(angles, values, color=color, linewidth=2)
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontproperties=prop)
    return fig

def setup_chinese_font():
    font_path = "data/TaipeiSansTC-Regular.ttf"
    if os.path.exists(font_path):
        return fm.FontProperties(fname=font_path)
    return fm.FontProperties(family="sans-serif")

prop = setup_chinese_font()

st.title("2024中華職棒球員數據")
st.markdown("""
    本應用程式使用 PR 值 來評估球員的表現，PR 值範圍從 0 到 99，數值越高代表球員該項數據表現越優異。
""")

st.sidebar.title("選擇球員類型")
player_type = st.sidebar.radio("選擇類型", ["打者", "先發投手", "後援投手"])

data_files = {
    "打者": ("data/batting_stats_test.xlsx", {"打擊率": True, "打點": True, "安打": True, "全壘打": True, "盜壘": True, "整體攻擊指數": True}),
    "先發投手": ("data/picter_stats5.xlsx", {"防禦率": False, "每局被上壘率": False, "K9值": True, "B9值": False, "被局全壘打率": False}),
    "後援投手": ("data/picter_stats6.xlsx", {"防禦率": False, "每局被上壘率": False, "K9值": True, "B9值": False, "被局全壘打率": False})
}

if player_type in data_files:
    file_path, metrics = data_files[player_type]
    df = load_data(file_path, metrics)
    selected_player = st.selectbox("選擇球員", df["球員"].unique())
    player_data = df[df["球員"] == selected_player].iloc[0]
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.write("### 能力雷達圖")
        fig = plot_radar_chart(player_data, metrics, prop)
        st.pyplot(fig)
    
    with col2:
        st.write("### 球員 PR 值")
        pr_data = pd.DataFrame({
            "項目": metrics.keys(),
            "原始數據": player_data[list(metrics.keys())].values,
            "PR": player_data[[f"{m}_PR" for m in metrics.keys()]].values
        })
        st.dataframe(pr_data.set_index("項目"))
    
    st.write("### PR 值橫條圖")
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.barplot(x="PR", y="項目", data=pr_data, palette="coolwarm", ax=ax, orient='h', width=0.6)
    ax.set_xlim(0, 99)
    ax.set_xlabel("PR")
    ax.set_ylabel("")
    ax.grid(axis='x', linestyle='--', alpha=0.5)
    for index, value in enumerate(pr_data["PR"]):
        ax.text(value + 1, index, str(value), va='center', fontsize=10, fontproperties=prop, color='black')
    if prop:
        for label in ax.get_yticklabels():
            label.set_fontproperties(prop)
    st.pyplot(fig)
