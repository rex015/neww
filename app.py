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
import colorsys
import hashlib
import os

# 使用相對路徑
def load_data_batter():
    file_path = "data/batting_stats_test.xlsx"
    df = pd.read_excel(file_path, sheet_name="工作表1")
    metrics = ["打擊率", "打點", "安打", "全壘打", "盜壘", "整體攻擊指數"]
    for metric in metrics:
        df[f"{metric}_PR"] = df[metric].rank(pct=True) * 99
        df[f"{metric}_PR"] = df[f"{metric}_PR"].round().astype(int)
    return df

def load_data_pitcher():
    file_path = "data/picter_stats5.xlsx"
    df = pd.read_excel(file_path, sheet_name="工作表1")
    metrics = {"防禦率": False, "每局被上壘率": False, "K9值": True, "B9值": False, "被局全壘打率": False}
    for metric, ascending in metrics.items():
        df[f"{metric}_PR"] = df[metric].rank(ascending=ascending, pct=True) * 99
        df[f"{metric}_PR"] = df[f"{metric}_PR"].round().astype(int)
    return df

def load_data_reliever():
    file_path = "data/picter_stats6.xlsx"
    df = pd.read_excel(file_path, sheet_name="工作表1")
    metrics = {"防禦率": False, "每局被上壘率": False, "K9值": True, "B9值": False, "被局全壘打率": False}
    for metric, ascending in metrics.items():
        df[f"{metric}_PR"] = df[metric].rank(ascending=ascending, pct=True) * 99
        df[f"{metric}_PR"] = df[f"{metric}_PR"].round().astype(int)
    return df

def plot_radar_chart(player_data, metrics, prop):
    values = player_data[[f"{m}_PR" for m in metrics]].values.flatten()
    labels = metrics
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    values = np.concatenate((values, [values[0]]))
    angles += angles[:1]
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    color = (0.4, 0.6, 0.8)  # 固定淺藍色
    ax.fill(angles, values, color=color, alpha=0.3)
    ax.plot(angles, values, color=color, linewidth=2)
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontproperties=prop)
    return fig

# 設定中文字體
def setup_chinese_font():
    # 嘗試加載Streamlit Cloud中可能有的中文字體
    font_paths = [
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",  # Ubuntu中的Noto字體
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",          # Ubuntu中的文泉驛字體
    ]
    
    # 檢查字體檔案是否存在
    for font_path in font_paths:
        if os.path.exists(font_path):
            return fm.FontProperties(fname=font_path)
    
    # 如果找不到特定的中文字體，嘗試使用matplotlib的默認字體
    try:
        return fm.FontProperties(family='sans-serif')
    except:
        return fm.FontProperties()

# 初始化中文字體
prop = setup_chinese_font()

st.title("2024中華職棒球員數據")
st.markdown("""
    本應用程式使用 PR 值 來評估球員的表現，  PR 值範圍從 0 到 99，數值越高代表球員該項數據表現越優異。  
    雷達圖的面積越大，表示該球員整體能力越強。這類似於遊戲中角色能力值的評比方式。
""")

st.sidebar.title("選擇球員類型")

player_type = st.sidebar.radio("選擇類型", ["打者", "先發投手", "後援投手"])

if player_type == "打者":
    df = load_data_batter()
    metrics = ["打擊率", "打點", "安打", "全壘打", "盜壘", "整體攻擊指數"]
elif player_type == "先發投手":
    df = load_data_pitcher()
    metrics = ["防禦率", "每局被上壘率", "K9值", "B9值", "被局全壘打率"]
elif player_type == "後援投手":
    df = load_data_reliever()
    metrics = ["防禦率", "每局被上壘率", "K9值", "B9值", "被局全壘打率"]

if player_type in ["打者", "先發投手", "後援投手"]:
    selected_player = st.selectbox("選擇球員", df["球員"].unique())
    player_data = df[df["球員"] == selected_player].iloc[0]
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.write("### 能力雷達圖")
        fig = plot_radar_chart(player_data, metrics, prop)
        st.pyplot(fig)
    with col2:
        st.write("### 球員 PR 值 ")
        pr_data = pd.DataFrame({
            "項目": metrics,
            "原始數據": player_data[metrics].values,
            "PR": player_data[[f"{m}_PR" for m in metrics]].values
        })
        st.dataframe(pr_data.set_index("項目"))
    
    st.write("### PR 值橫條圖")
    fig, ax = plt.subplots(figsize=(6, 4))
    colors = sns.color_palette("coolwarm", len(pr_data))
    sns.barplot(x="PR", y="項目", data=pr_data, hue="項目", palette=colors, ax=ax, orient='h', width=0.6, legend=False)
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