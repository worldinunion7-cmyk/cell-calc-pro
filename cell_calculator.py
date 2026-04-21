import streamlit as st
import math

# --- 1. アプリ基本設定 ---
st.set_page_config(page_title="Cell Stock & Seeding Manager", layout="centered", page_icon="🔬")

# --- 2. カスタムCSS（視認性・ハイコントラスト設計） ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono:wght@500&display=swap');

    /* 全体のダークトーン設定 */
    .stApp {
        background-color: #0d1117;
        color: #e6edf3 !important;
    }

    /* タイトル：境界線を引いたソリッドなデザイン */
    h1 {
        color: #58a6ff !important;
        font-family: 'Inter', sans-serif;
        font-weight: 800 !important;
        letter-spacing: -0.05em;
        padding-bottom: 15px;
        border-bottom: 2px solid #58a6ff;
        margin-bottom: 40px !important;
    }

    /* セクションヘッダー：視認性向上のための枠線 */
    h2, h3 {
        color: #f0f6fc !important;
        font-size: 1.15rem !important;
        font-weight: 700 !important;
        margin-top: 15px !important;
        padding: 5px 12px !important;
        background: rgba(88, 166, 255, 0.1);
        border-radius: 4px;
        border-left: 5px solid #58a6ff;
    }

    /* 【重要】入力ボックス：文字を黒にして視認性を確保 */
    input {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 600 !important;
    }
    
    /* 入力エリアの背景（少し明るいグレーに固定） */
    div[data-baseweb="input"] {
        background-color: #f0f6fc !important;
        border: 2px solid #30363d !important;
        border-radius: 8px !important;
    }

    /* ラベルの視認性向上 */
    label p {
        color: #c9d1d9 !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        margin-bottom: 8px !important;
    }

    /* セクションごとの囲み（カード）をより明確に */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #161b22 !important;
        border: 1px solid #444c56 !important;
        border-radius: 12px !important;
        padding: 30px !important;
        margin-bottom: 30px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.5) !important;
    }

    /* 数値表示（Metric） */
    [data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace !important;
        color: #58a6ff !important;
    }

    /* 指示バー（ハイコントラスト設定） */
    .instruction-blue {
        background-color: #00f2fe !important;
        color: #000000 !important;
        padding: 15px;
        border-radius: 8px;
        font-weight: 800;
        margin: 10px 0;
        border-left: 8px solid #00c6ff;
    }
    .instruction-yellow {
        background-color: #fce38a !important;
        color: #000000 !important;
        padding: 15px;
        border-radius: 8px;
        font-weight: 800;
        margin: 10px 0;
        border-left: 8px solid #f39c12;
    }

    /* ボタン */
    .stButton>button {
        background-color: #238636 !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        height: 3em !important;
        border: none !important;
    }

    /* LaTeX（数式）の背景を少し明るくして読みやすく */
    .stLatex {
        background-color: #0d1117 !important;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #30363d;
        color: #f0f6fc !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 補助関数 ---
def format_sci_latex(val):
    if val <= 0: return "0"
    exponent = int(math.floor(math.log10(abs(val))))
    coeff = val / (10**exponent)
    return f"{coeff:.2f} \\times 10^{{{exponent}}}"

def label_vol(v_ml):
    return f"{v_ml*1000:.1f} μL" if v_ml < 1 else f"{v_ml:.3f} mL"

# --- 4. メインコンテンツ ---
st.title("🔬 Cell Seeding & Stock Manager")

# --- 1. カウント結果 ---
with st.container(border=True):
    st.subheader("1. カウント結果")
    col_a, col_b = st.columns(2)
    with col_a:
        count_val = st.number_input("カウント数 (個/0.1mm³)", value=50, min_value=0, step=1)
    with col_b:
        vol_val = st.number_input("回収溶液量 (mL)", value=5, min_value=1, step=1)
    
    total_cells = count_val * vol_val * 10000
    st.latex(f"現在の総細胞数: {format_sci_latex(total_cells)} \, [cells]")

# --- 2. 懸濁液の調製 ---
with st.container(border=True):
    st.subheader("2. 懸濁液の調製")
    resuspension_vol = st.number_input("ペレットに加える培地量 (mL)", value=5.0, min_value=0.1, step=0.1)
    
    if resuspension_vol > 0:
        density_val = total_cells / resuspension_vol
        st.latex(f"懸濁後の細胞密度: {format_sci_latex(density_val)} \, [cells/mL]")
    else:
        density_val = 0

# --- 3. まき直し設定 ---
with st.container(border=True):
    st.subheader("3. まき直し設定")
    
    dish_info = {"3 cm": 2.0, "6 cm": 4.0, "10 cm": 8.0}
    d_size_col, d_num_col = st.columns(2)
    with d_size_col:
        selected_size = st.selectbox("Dishサイズ", list(dish_info.keys()))
    with d_num_col:
        dish_count = st.number_input("Dish枚数", value=1, min_value=1)
    
    st.write("1枚あたりの目標細胞数 (D)")
    c_col, e_col = st.columns([2, 1])
    with c_col:
        d_coeff = st.number_input("細胞数", value=2.0, step=0.1, key="d_c")
    with e_col:
        d_expo = st.number_input("× 10^x", value=6, step=1, key="d_e")
    target_D = d_coeff * (10**d_expo)

    seeding_method = st.radio("まき方の選択", ["方法1: 規定量に上乗せ", "方法2: 合計量を規定量に合わせる"], horizontal=True)

    required_cells_seeding = target_D * dish_count

    if required_cells_seeding > total_cells:
        st.error(f"◆ 不足: {format_sci_latex(required_cells_seeding - total_cells)} 個")
        seeding_possible = False
        remaining_cells = 0
    else:
        seeding_possible = True
        remaining_cells = total_cells - required_cells_seeding
        if density_val > 0:
            vol_per_dish_mL = target_D / density_val
            base_vol_standard = dish_info[selected_size]
            
            st.markdown("---")
            if seeding_method == "方法1: 規定量に上乗せ":
                pre_fill_vol = base_vol_standard
                st.markdown(f'<div class="instruction-blue">◆ 各Dishに培地を {pre_fill_vol} mL ずつ入れておく</div>', unsafe_allow_html=True)
            else:
                pre_fill_vol = base_vol_standard - vol_per_dish_mL
                st.markdown(f'<div class="instruction-blue">◆ 各Dishに培地を {pre_fill_vol:.3f} mL ずつ入れておく</div>', unsafe_allow_html=True)
            
            st.markdown(f'<div class="instruction-yellow">◇ そこに細胞溶液を {label_vol(vol_per_dish_mL)} ずつ加える</div>', unsafe_allow_html=True)

# --- 4. 凍結保存 (Stock) ---
if seeding_possible and density_val > 0:
    with st.container(border=True):
        st.subheader("4. 凍結保存 (Stock)")
        st.latex(f"凍結可能細胞数: {format_sci_latex(remaining_cells)} \, [cells]")
        
        st.markdown("---")
        v_col1, v_col2 = st.columns([2, 1])
        with v_col1:
            stock_coeff = st.number_input("目標密度 (個/tube)", value=1.0, step=0.1)
        with v_col2:
            stock_expo = st.number_input("× 10^n", value=6, step=1)
            
        cells_per_vial = stock_coeff * (10**stock_expo)
        vial_size_label = st.radio("1本あたりの分注量", ["0.5 mL", "1.0 mL"], horizontal=True)
        vial_size_ml = 0.5 if vial_size_label == "0.5 mL" else 1.0
        
        max_vials = max(0, int(remaining_cells // cells_per_vial)) if cells_per_vial > 0 else 0
        
        if max_vials > 0:
            st.write(f"作製可能な最大本数: **{max_vials} 本**")
            vial_count = st.number_input("実際に作成するチューブ本数", value=max_vials, min_value=0, max_value=max_vials)
        else:
            st.write("余り細胞が目標密度に満たないため、ストック作製不可")
            vial_count = 0

        st.markdown("---")
        if vial_count > 0:
            total_freezing_medium = vial_count * vial_size_ml
            used_stock_cells = cells_per_vial * vial_count
            
            st.markdown('<div class="instruction-blue">◆ 凍結工程の手順</div>', unsafe_allow_html=True)
            st.write(f"1. まき直し後の残液（約 {max(0.0, resuspension_vol - (vol_per_dish_mL * dish_count)):.3f} mL）を回収・遠心。")
            st.write(f"2. ペレットに **凍結溶液を {total_freezing_medium:.2f} mL 加えて再懸濁。**")
            st.write(f"3. 各チューブに **{vial_size_label}** ずつ、計 **{vial_count} 本** に分注。")
            
            final_leftover = remaining_cells - used_stock_cells
        else:
            st.write("◇ 凍結保存は行いません")
            final_leftover = remaining_cells
            
        st.latex(f"最終的な廃棄分: {format_sci_latex(max(0.0, final_leftover))} \, [cells]")
