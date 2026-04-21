import streamlit as st
import math

# --- 1. アプリ基本設定 ---
st.set_page_config(page_title="Cell Stock & Seeding Manager", layout="centered", page_icon="🔬")

# --- 2. カスタムCSS（はみ出し完全解決・入力欄圧縮版） ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono:wght@500&display=swap');

    /* =========================================================
       超強力：スマホ強制横並び ＆ はみ出し防止コード
    ========================================================= */
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 8px !important; /* ボックス間の隙間 */
        width: 100% !important;
    }
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
        width: 50% !important;
        flex: 1 1 0% !important;
        min-width: 0 !important; /* 画面外へのはみ出しを防ぐ絶対条件 */
    }
    /* ========================================================= */

    /* 全体の背景設定 */
    .stApp {
        background-color: #0d1117;
        color: #e6edf3 !important;
    }

    /* タイトル */
    h1 {
        color: #58a6ff !important;
        font-family: 'Inter', sans-serif;
        font-weight: 800 !important;
        padding-bottom: 10px;
        border-bottom: 2px solid #30363d;
        margin-bottom: 20px !important;
        font-size: 1.8rem !important;
    }

    /* セクションヘッダー */
    h2, h3 {
        color: #f0f6fc !important;
        font-size: 1.0rem !important;
        font-weight: 600 !important;
        margin-top: 5px !important;
        border-left: 3px solid #58a6ff;
        padding-left: 10px !important;
        background: rgba(88, 166, 255, 0.05);
        border-radius: 4px;
    }

    /* 入力ボックス（長さを圧縮し、画面に収める） */
    div[data-baseweb="input"], div[data-baseweb="select"] {
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
        min-width: 0 !important; /* 入力欄が勝手に広がるのを防ぐ */
    }
    
    input {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.9rem !important; /* スマホ用に少し小さく */
        padding: 4px 8px !important; /* 内側の余白を削ってスリムに */
    }

    /* ラベル（項目名） */
    label p {
        color: #8b949e !important;
        font-weight: 600 !important;
        font-size: 0.75rem !important; /* スマホで1行に収まるように縮小 */
        margin-bottom: 2px !important;
        white-space: nowrap !important; /* 文字の折り返しを防ぐ */
    }

    /* 囲み枠 */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
        border-radius: 10px !important;
        padding: 15px !important;
        margin-bottom: 10px !important;
    }

    /* 指示バー */
    .ins-blue {
        background-color: #00d2ff !important;
        color: #000000 !important;
        padding: 10px;
        border-radius: 6px;
        font-weight: 800;
        margin: 5px 0;
        border-left: 8px solid #0095b6;
        font-size: 0.85rem;
    }
    .ins-yellow {
        background-color: #ffd700 !important;
        color: #000000 !important;
        padding: 10px;
        border-radius: 6px;
        font-weight: 800;
        margin: 5px 0;
        border-left: 8px solid #c5a000;
        font-size: 0.85rem;
    }

    /* 数値表示 */
    [data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace !important;
        color: #58a6ff !important;
        font-size: 1.4rem !important;
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
    col1, col2 = st.columns(2)
    with col1:
        count_val = st.number_input("カウント数 (個/0.1mm³)", value=50, min_value=0, step=1)
    with col2:
        vol_val = st.number_input("回収溶液量 (mL)", value=5, min_value=1, step=1)
    st.latex(f"現在の総細胞数: {format_sci_latex(count_val * vol_val * 10000)}")

# --- 2. 懸濁液の調製 ---
with st.container(border=True):
    st.subheader("2. 懸濁液の調製")
    res_vol = st.number_input("ペレットに加える培地量 (mL)", value=5.0, min_value=0.1, step=0.1)
    density = (count_val * vol_val * 10000) / res_vol if res_vol > 0 else 0
    st.latex(f"懸濁後の細胞密度: {format_sci_latex(density)} \, [cells/mL]")

# --- 3. まき直し設定 ---
with st.container(border=True):
    st.subheader("3. まき直し設定")
    
    col1, col2 = st.columns(2)
    with col1:
        dish_info = {"3 cm": 2.0, "6 cm": 4.0, "10 cm": 8.0}
        selected_size = st.selectbox("Dishサイズ", list(dish_info.keys()))
    with col2:
        dish_count = st.number_input("Dish枚数", value=1, min_value=1)
    
    st.caption("1枚あたりの目標細胞数")
    col3, col4 = st.columns(2)
    with col3:
        d_coeff = st.number_input("細胞数", value=2.0, step=0.1, key="d_c")
    with col4:
        d_expo = st.number_input("× 10^x", value=6, step=1, key="d_e")
    
    target_D = d_coeff * (10**d_expo)
    seeding_method = st.radio("まき方", ["方法1: 上乗せ", "方法2: 合計調整"], horizontal=True)

    required_seeding = target_D * dish_count
    total_cells = count_val * vol_val * 10000

    if required_seeding > total_cells:
        st.error(f"◆ 不足: {format_sci_latex(required_seeding - total_cells)} 個")
        seeding_possible = False
    else:
        seeding_possible = True
        if density > 0:
            vol_per_dish = target_D / density
            base_v = dish_info[selected_size]
            st.markdown("---")
            if seeding_method == "方法1: 上乗せ":
                st.markdown(f'<div class="ins-blue">◆ 各Dishに培地を {base_v} mL 入れておく</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="ins-blue">◆ 各Dishに培地を {base_v - vol_per_dish:.3f} mL 入れておく</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="ins-yellow">◇ そこに細胞溶液を {label_vol(vol_per_dish)} ずつ加える</div>', unsafe_allow_html=True)

# --- 4. 凍結保存 (Stock) ---
if seeding_possible and density > 0:
    with st.container(border=True):
        st.subheader("4. 凍結保存 (Stock)")
        rem_cells = total_cells - required_seeding
        st.latex(f"凍結可能数: {format_sci_latex(rem_cells)}")
        
        col1, col2 = st.columns(2)
        with col1:
            stock_coeff = st.number_input("密度/tube", value=1.0, step=0.1)
        with col2:
            stock_expo = st.number_input("× 10^n", value=6, step=1)
            
        vial_size_label = st.radio("分注量", ["0.5 mL", "1.0 mL"], horizontal=True)
        vial_size_ml = 0.5 if vial_size_label == "0.5 mL" else 1.0
        
        per_vial = stock_coeff * (10**stock_expo)
        max_v = max(0, int(rem_cells // per_vial)) if per_vial > 0 else 0
        
        if max_v > 0:
            st.write(f"最大本数: **{max_v} 本**")
            vial_count = st.number_input("作成数", value=max_v, min_value=0, max_value=max_v)
            
            total_fm = vial_count * vial_size_ml
            st.markdown('<div class="ins-blue">◆ 凍結手順</div>', unsafe_allow_html=True)
            st.write(f"1. 残液を回収・遠心 ➔ 2. 凍結液 **{total_fm:.2f} mL** で懸濁 ➔ 3. **{vial_size_label}** ずつ分注")
            final_left = rem_cells - (vial_count * per_vial)
        else:
            st.write("◇ 凍結不可")
            final_left = rem_cells
            
        st.latex(f"最終廃棄分: {format_sci_latex(max(0.0, final_left))} \, [cells]")
