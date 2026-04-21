import streamlit as st
import math
# --- アプリ設定 ---
st.set_page_config(page_title="Cell Seeding & Stock Manager", layout="centered", page_icon="🧬")

# --- カスタムCSS（視認性向上・スタイリッシュフォント） ---
st.markdown("""
    <style>
    /* Google FontsからInterとJetBrains Monoを読み込み */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&family=JetBrains+Mono:wght@500&display=swap');

    /* 全体のフォント設定 */
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
        color: #FFFFFF !important; /* 基本の文字色を純白にして視認性UP */
    }

    /* 背景色 */
    .stApp {
        background-color: #05070A;
    }

    /* タイトル：鮮やかなグラデーション */
    h1 {
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
        padding-bottom: 20px;
    }

    /* サブヘッダーの強調 */
    h2, h3 {
        color: #4facfe !important;
        font-weight: 700 !important;
        border-left: 4px solid #4facfe;
        padding-left: 15px !important;
    }

    /* カード（Container）のデザイン：透明感と立体感 */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 20px !important;
        padding: 25px !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5) !important;
        margin-bottom: 20px;
    }

    /* グレーで見えにくかったラベル（入力欄のタイトル）を明るく */
    label p {
        color: #B0C4DE !important; /* 明るいスチールブルー */
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }

    /* メトリック（計算結果）の数値を美しく */
    [data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace !important;
        color: #00f2fe !important;
        font-weight: 700 !important;
    }

    /* LaTeX（数式）の視認性 */
    .stLatex {
        color: #FFFFFF !important;
        background: rgba(0, 242, 254, 0.05);
        padding: 10px;
        border-radius: 10px;
    }

    /* ボタンをよりApple風のクリーンなデザインに */
    .stButton>button {
        background: #4facfe !important;
        color: white !important;
        border-radius: 12px !important;
        border: none !important;
        font-weight: 700 !important;
        height: 3em !important;
        transition: all 0.2s ease-in-out !important;
    }
    .stButton>button:hover {
        background: #00f2fe !important;
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(79, 172, 254, 0.4);
    }

    /* スライダーや入力欄の背景 */
    input {
        background-color: rgba(255, 255, 255, 0.07) !important;
        border-radius: 8px !important;
    }

    /* キャプション（注釈）の文字色を少し明るく */
    .stCaption {
        color: #94a3b8 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ここから下の計算ロジックはそのまま継続 ---
st.title("🧬 Cell Stock & Seeding Manager")
# (ここから下のカウント計算などのコードを続けてください)
# --- 補助関数：科学的表記（LaTeX） ---
def format_sci_latex(val):
    if val <= 0: return "0"
    exponent = int(math.floor(math.log10(abs(val))))
    coeff = val / (10**exponent)
    return f"{coeff:.2f} \\times 10^{{{exponent}}}"

def label_vol(v_ml):
    return f"{v_ml*1000:.1f} μL" if v_ml < 1 else f"{v_ml:.3f} mL"

# --- アプリ設定 ---
st.set_page_config(page_title="Cell Seeding & Stock Manager", layout="centered")
st.title("🧫 Cell Seeding & Stock Manager")

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
        st.error(f"⚠️ 細胞が足りません！ (不足: {format_sci_latex(required_cells_seeding - total_cells)} 個)")
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
                st.success(f"✅ **各Dishに培地を {pre_fill_vol} mL ずつ入れておく**")
            else:
                pre_fill_vol = base_vol_standard - vol_per_dish_mL
                st.success(f"✅ **各Dishに培地を {pre_fill_vol:.3f} mL ずつ入れておく**")
            
            st.info(f"💡 **そこに細胞溶液を {label_vol(vol_per_dish_mL)} ずつ加える**")

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
        
        # 【復活】最大本数の算出
        max_vials = max(0, int(remaining_cells // cells_per_vial)) if cells_per_vial > 0 else 0
        
        if max_vials > 0:
            st.write(f"作製可能な最大本数: **{max_vials} 本**")
            vial_count = st.number_input("実際に作成するチューブ本数", value=max_vials, min_value=0, max_value=max_vials)
        else:
            st.warning("余り細胞が目標密度に満たないため、凍結ストックは作製できません。")
            vial_count = 0

        st.markdown("---")
        # 凍結手順の表示
        if vial_count > 0:
            total_freezing_medium = vial_count * vial_size_ml
            used_stock_cells = cells_per_vial * vial_count
            
            st.info(f"🧪 **凍結手順:**")
            st.write(f"① まき直し後の残液（約 **{max(0.0, resuspension_vol - (vol_per_dish_mL * dish_count)):.3f} mL**）をすべて回収し、遠心分離。")
            st.write(f"② 上清を除去したペレットに **凍結溶液を {total_freezing_medium:.2f} mL 加えて再懸濁。**")
            st.write(f"③ 各チューブに **{vial_size_label}** ずつ、計 **{vial_count} 本** に分注する。")
            
            final_leftover = remaining_cells - used_stock_cells
        else:
            # 凍結しない場合
            st.write("❄️ **凍結保存は行いません。**")
            final_leftover = remaining_cells
            
        # 廃棄細胞数は常に表示
        st.latex(f"最終的な廃棄分: {format_sci_latex(max(0.0, final_leftover))} \, [cells]")
    
