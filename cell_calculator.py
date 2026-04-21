import streamlit as st
import math

# --- 補助関数：科学的表記（LaTeX） ---
def format_sci_latex(val):
    if val <= 0: return "0"
    exponent = int(math.floor(math.log10(abs(val))))
    coeff = val / (10**exponent)
    return f"{coeff:.2f} \\times 10^{{{exponent}}}"

# --- アプリ設定 ---
st.set_page_config(page_title="Cell Calc Pro", layout="centered")
st.title("🧫 Cell Counting & Seeding Pro")
st.caption("セルカウントから『まき直し』と『凍結』の計算を一括で行います")

# --- 1. カウント入力 (Step 1) ---
with st.container(border=True):
    st.subheader("1. カウント結果")
    col_a, col_b = st.columns(2)
    with col_a:
        count_A = st.number_input("カウント数 A (個/0.1mm³)", value=50.0, step=1.0)
    with col_b:
        vol_B = st.number_input("回収溶液量 B (mL)", value=5.0, step=0.1)
    
    total_cells = count_A * vol_B * 10000
    st.latex(f"現在の総細胞数: {format_sci_latex(total_cells)} \, [cells]")

# --- 2. まき直し設定 (Step 2) ---
with st.container(border=True):
    st.subheader("2. まき直し設定")
    
    # 指数入力ウィジェット
    st.write("1枚あたりの目標細胞数 D")
    c_col, e_col = st.columns([2, 1])
    with c_col:
        d_coeff = st.number_input("係数 (例: 2.5)", value=1.0, step=0.1, key="d_c")
    with e_col:
        d_expo = st.number_input("指数 10^x (例: 6)", value=5, step=1, key="d_e")
    target_D = d_coeff * (10**d_expo)
    st.latex(f"D = {format_sci_latex(target_D)} \, [cells/dish]")

    dish_info = {"3 cm": 2.0, "6 cm": 4.0, "10 cm": 8.0}
    d_size_col, d_num_col = st.columns(2)
    with d_size_col:
        selected_size = st.selectbox("Dishサイズ", list(dish_info.keys()))
    with d_num_col:
        dish_count = st.number_input("Dish枚数", value=1, min_value=1)
    
    # 必要な細胞総量
    required_cells_seeding = target_D * dish_count

# --- 3. 凍結設定 (Step 3) ---
with st.container(border=True):
    st.subheader("3. 凍結設定")
    vial_count = st.number_input("凍結チューブの本数", value=0, min_value=0)
    # 凍結条件: 1本あたり 1.0 x 10^6 cells
    cells_per_vial = 1.0 * (10**6)
    required_cells_freezing = cells_per_vial * vial_count
    
    if vial_count > 0:
        st.latex(f"凍結必要数: {format_sci_latex(required_cells_freezing)} \, [cells]")

# --- 4. 計算結果 (Result) ---
st.divider()
st.subheader("📊 計算結果")

# 細胞が足りるかチェック
grand_total_required = required_cells_seeding + required_cells_freezing

if grand_total_required > total_cells:
    st.error(f"⚠️ 細胞が足りません！ (不足: {format_sci_latex(grand_total_required - total_cells)} 個)")
else:
    # まきやすさ（分注量）の指定
    dispense_uL = st.slider("まきやすさの調整：1枚あたりの分注量 (uL)", 50, 500, 200, step=10)
    
    # 目標濃度 C の計算 (D / 分注量mL)
    target_C = target_D / (dispense_uL / 1000)
    # 懸濁用培地量
    suspend_vol_mL = total_cells / target_C
    
    st.latex(f"目標濃度 C: {format_sci_latex(target_C)} \, [cells/mL]")
    st.info(f"💡 **培地 {suspend_vol_mL:.3f} mL** で細胞を懸濁してください。")

    # 消費内訳の計算
    vol_seeding_total_mL = (dispense_uL * dish_count) / 1000
    vol_freezing_total_mL = required_cells_freezing / target_C
    vol_discard_mL = suspend_vol_mL - vol_seeding_total_mL - vol_freezing_total_mL
    cells_discard = vol_discard_mL * target_C

    # 結果テーブルの表示
    col1, col2, col3 = st.columns(3)
    col1.metric("まき直し用", f"{vol_seeding_total_mL:.2f} mL")
    col2.metric("凍結用", f"{vol_freezing_total_mL:.2f} mL")
    col3.metric("破棄分", f"{max(0, vol_discard_mL):.2f} mL")

    # 方法の指示
    method = st.radio("まき方", ["方法1: 規定量に上乗せ", "方法2: 合計量を合わせる"])
    base_v = dish_info[selected_size]
    
    with st.expander("具体的な作業手順を表示", expanded=True):
        if method == "方法1: 規定量に上乗せ":
            st.write(f"1. 各Dishに培地 **{base_v} mL** を分注しておく。")
            st.write(f"2. 作製した細胞溶液を **{dispense_uL} μL** ずつ加える。")
        else:
            st.write(f"1. 各Dishに培地 **{base_v - (dispense_uL/1000):.3f} mL** を分注しておく。")
            st.write(f"2. 作製した細胞溶液を **{dispense_uL} μL** ずつ加えて、合計 **{base_v} mL** にする。")
        
        if vial_count > 0:
            st.write(f"3. 凍結用として **{vol_freezing_total_mL:.3f} mL** を別チューブに回収し、遠心後に凍結媒体 **{0.5 * vial_count} mL** で再懸濁して **{vial_count} 本** に分注する。")
        
        st.write(f"4. 残りの **{max(0, vol_discard_mL):.3f} mL** （約 {format_sci_latex(max(0, cells_discard))} 個）は破棄する。")