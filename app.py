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
    # 多路徑處理
    full_paths = [
        file_path,
        os.path.join(os.path.dirname(__file__), file_path),
        f"/app/{file_path}"
    ]
    
    # 嘗試不同路徑載入
    for path in full_paths:
        try:
            df = pd.read_excel(path, sheet_name="工作表1")
            break
        except FileNotFoundError:
            continue
    else:
        st.error(f"無法找到檔案: {file_path}")
        return None

    # 驗證資料和列
    if df is None or df.empty:
        st.warning("載入的數據為空")
        return None

    for metric, ascending in metrics.items():
        if metric not in df.columns:
            st.error(f"缺少列: {metric}")
            return None
        
        df[f"{metric}_PR"] = df[metric].rank(ascending=ascending, pct=True) * 99
        df[f"{metric}_PR"] = df[f"{metric}_PR"].round().astype(int)
    
    return df

def setup_chinese_font():
    # 多路徑嘗試
    font_paths = [
        "data/TaipeiSansTC-Regular.ttf",
        "/app/data/TaipeiSansTC-Regular.ttf",
        os.path.join(os.path.dirname(__file__), "TaipeiSansTC-Regular.ttf")
    ]
    
    for path in font_paths:
        if os.path.exists(path):
            return fm.FontProperties(fname=path)
    
    # 備選方案
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'Taipei Sans TC']
    return None

def plot_radar_chart(player_data, metrics, prop):
    values = player_data[[f"{m}_PR" for m in metrics]].values.flatten()
    labels = list(metrics.keys())
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    values = np.concatenate((values, [values[0]]))
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(polar=True))
    color = (0.4, 0.6, 0.8)
    ax.fill(angles, values, color=color, alpha=0.3)
    ax.plot(angles, values, color=color, linewidth=2)
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    
    if prop:
        ax.set_xticklabels(labels, fontproperties=prop)
    else:
        ax.set_xticklabels(labels)
    
    return fig

def main():
    st.set_page_config(page_title="2024中華職棒球員數據", layout="wide")
    
    prop = setup_chinese_font()
    
    st.title("2024中華職棒球員數據")
    st.markdown("""
        本應用程式使用 PR 值 來評估球員的表現，PR 值範圍從 0 到 99，數值越高代表球員該項數據表現越優異。
    """)
    
    # 初始化 session state
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = {}
    
    st.sidebar.title("選擇球員類型")
    player_type = st.sidebar.radio("選擇類型", ["打者", "先發投手", "後援投手"])
    
    data_files = {
        "打者": ("data/batting_stats_test.xlsx", {"打擊率": True, "打點": True, "安打": True, "全壘打": True, "盜壘": True, "整體攻擊指數": True}),
        "先發投手": ("data/picter_stats5.xlsx", {"防禦率": False, "每局被上壘率": False, "K9值": True, "B9值": False, "被局全壘打率": False}),
        "後援投手": ("data/picter_stats6.xlsx", {"防禦率": False, "每局被上壘率": False, "K9值": True, "B9值": False, "被局全壘打率": False})
    }
    
    try:
        # 緩存和載入資料
        if player_type not in st.session_state.data_loaded:
            df = load_data(*data_files[player_type])
            if df is not None:
                st.session_state.data_loaded[player_type] = df
            else:
                st.error("數據加載失敗")
                return

        df = st.session_state.data_loaded[player_type]
        file_path, metrics = data_files[player_type]

        selected_player = st.selectbox("選擇球員", df["球員"].unique())
        player_data = df[df["球員"] == selected_player].iloc[0]
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.write("### 能力雷達圖")
            fig = plot_radar_chart(player_data, metrics, prop)
            st.pyplot(fig)
            plt.close(fig)  # 關閉圖形釋放記憶體
        
        with col2:
            st.write("### 球員 PR 值")
            pr_data = pd.DataFrame({
                "項目": list(metrics.keys()),
                "原始數據": player_data[list(metrics.keys())].values,
                "PR": player_data[[f"{m}_PR" for m in metrics.keys()]].values
            })
            st.dataframe(pr_data.set_index("項目"))
        
        st.write("### PR 值橫條圖")
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.barplot(x="PR", y="項目", data=pr_data, hue="項目", palette="coolwarm", 
                    ax=ax, orient='h', width=0.6, legend=False)
        ax.set_xlim(0, 99)
        ax.set_xlabel("PR")
        ax.set_ylabel("")
        ax.grid(axis='x', linestyle='--', alpha=0.5)
        
        for index, value in enumerate(pr_data["PR"]):
            ax.text(value + 1, index, str(value), va='center', fontsize=10, color='black')
        
        if prop:
            for label in ax.get_yticklabels():
                label.set_fontproperties(prop)
        
        st.pyplot(fig)
        plt.close(fig)  # 關閉圖形釋放記憶體

    except Exception as e:
        st.error(f"處理數據時發生錯誤: {e}")

if __name__ == "__main__":
    main()
