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

# --- 1. カウント入力 (整数入力) ---
with st.container(border=True):
    st.subheader("1. カウント結果")
    col_a, col_b = st.columns(2)
    with col_a:
        # 小数点なし、ステップ1の整数入力
        count_A = st.number_input("カウント数 A (個/0.1mm³)", value=50, step=1)
    with col_b:
        # 溶液量も整数指定（ご指示により小数表記なし）
        vol_B = st.number_input("回収溶液量 B (mL)", value=5, step=1)
    
    total_cells = count_A * vol_B * 10000
    st.latex(f"現在の総細胞数: {format_sci_latex(total_cells)} \, [cells]")

# --- 2. まき直し設定 ---
with st.container(border=True):
    st.subheader("2. まき直し設定")
    
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
    
    # 修正：必要細胞数と余り細胞数の表示
    required_cells_seeding = target_D * dish_count
    remaining_cells_after_seeding = total_cells - required_cells_seeding
    
    st.markdown("---")
    st.latex(f"必要細胞数 (Total \, D): {format_sci_latex(required_cells_seeding)}")
    if remaining_cells_after_seeding >= 0:
        st.latex(f"余り細胞数: {format_sci_latex(remaining_cells_after_seeding)}")
    else:
        st.error(f"⚠️ 細胞が足りません！ (不足: {format_sci_latex(abs(remaining_cells_after_seeding))})")

# --- 3. 計算結果 (Result & Freezing) ---
if remaining_cells_after_seeding >= 0:
    with st.container(border=True):
        st.subheader("3. 計算結果")
        
        # まきやすさスケールバーの修正
        # 100uL単位、最大5000uL(5mL)
        dispense_val = st.slider("まきやすさの調整：1枚あたりの分注量", 
                                 min_value=100, max_value=5000, value=200, step=100)
        
        # 単位表示の切り替え
        label_dispense = f"{dispense_val} μL" if dispense_val < 1000 else f"{dispense_val/1000:.1f} mL"
        st.write(f"現在の設定: **{label_dispense}** / 枚")
        
        # 目標濃度 C の計算
        target_C = target_D / (dispense_val / 1000)
        suspend_vol_mL = total_cells / target_C
        
        st.info(f"💡 **培地 {suspend_vol_mL:.3f} mL** で細胞を懸濁してください。")
        st.latex(f"算出された目標濃度 C: {format_sci_latex(target_C)} \, [cells/mL]")

        st.markdown("---")
        st.write("❄️ **凍結オプション (任意)**")
        vial_count = st.number_input("凍結チューブの本数", value=0, min_value=0)
        cells_per_vial = 1.0 * (10**6)
        required_cells_freezing = cells_per_vial * vial_count
        
        # 消費内訳の計算
        vol_seeding_total_mL = (dispense_val * dish_count) / 1000
        vol_freezing_total_mL = required_cells_freezing / target_C
        vol_discard_mL = suspend_vol_mL - vol_seeding_total_mL - vol_freezing_total_mL

        # 最終内訳の表示
        col1, col2, col3 = st.columns(3)
        col1.metric("まき直し用", f"{vol_seeding_total_mL:.2f} mL")
        col2.metric("凍結用", f"{vol_freezing_total_mL:.2f} mL")
        col3.metric("破棄分", f"{max(0.0, vol_discard_mL):.2f} mL")

        # 手順ガイド
        with st.expander("具体的な作業手順を表示", expanded=True):
            base_v = dish_info[selected_size]
            st.write(f"1. 各Dishに培地を準備。")
            if dispense_val < 1000:
                st.write(f"   (方法1なら {base_v} mL / 方法2なら {base_v - (dispense_val/1000):.3f} mL)")
            else:
                st.write(f"   (方法1なら {base_v} mL / 方法2なら {base_v - (dispense_val/1000):.1f} mL)")
            
            st.write(f"2. 細胞溶液を **{label_dispense}** ずつ加えて、まき直し完了。")
            
            if vial_count > 0:
                if (remaining_cells_after_seeding < required_cells_freezing):
                    st.warning("⚠️ 凍結用の細胞が足りません！本数を減らしてください。")
                else:
                    st.write(f"3. 凍結用として **{vol_freezing_total_mL:.3f} mL** を回収する。")
            
            st.write(f"4. 残りの **{max(0.0, vol_discard_mL):.3f} mL** は適切に破棄する。")
