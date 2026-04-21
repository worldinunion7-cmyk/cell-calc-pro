import streamlit as st
import math

# --- 補助関数：科学的表記（LaTeX） ---
def format_sci_latex(val):
    if val <= 0: return "0"
    exponent = int(math.floor(math.log10(abs(val))))
    coeff = val / (10**exponent)
    return f"{coeff:.2f} \\times 10^{{{exponent}}}"

# 単位表示の切り替え関数
def label_vol(v_ml):
    return f"{v_ml*1000:.1f} μL" if v_ml < 1 else f"{v_ml:.3f} mL"

# --- アプリ設定 ---
st.set_page_config(page_title="Cell Susp Calc", layout="centered")
st.title("🧫 Cell Seeding & Stock Manager")

# --- 1. カウント結果 ---
with st.container(border=True):
    st.subheader("1. カウント結果")
    col_a, col_b = st.columns(2)
    with col_a:
        count_A = st.number_input("カウント数 A (個/0.1mm³)", value=50, step=1)
    with col_b:
        vol_B = st.number_input("回収溶液量 B (mL)", value=5, step=1)
    
    total_cells = count_A * vol_B * 10000
    st.latex(f"現在の総細胞数: {format_sci_latex(total_cells)} \, [cells]")

# --- 2. 懸濁液の調製 ---
with st.container(border=True):
    st.subheader("2. 懸濁液の調製")
    resuspension_vol = st.number_input("ペレットに加える培地量 (mL)", value=5.0, step=0.1)
    
    if resuspension_vol > 0:
        density_C = total_cells / resuspension_vol
        st.info(f"💡 **懸濁後の細胞密度 (C):**")
        st.latex(f"C = {format_sci_latex(density_C)} \, [cells/mL]")
    else:
        density_C = 0

# --- 3. まき直し設定 ---
with st.container(border=True):
    st.subheader("3. まき直し設定")
    st.write("1枚あたりの目標細胞数 (D)")
    
    c_col, e_col = st.columns([2, 1])
    with c_col:
        d_coeff = st.number_input("細胞数", value=2.0, step=0.1, key="d_c")
    with e_col:
        d_expo = st.number_input("× 10^x", value=6, step=1, key="d_e")
        
    target_D = d_coeff * (10**d_expo)
    st.latex(f"D = {format_sci_latex(target_D)} \, [cells/dish]")

    dish_count = st.number_input("まくDishの枚数", value=1, min_value=1)
    required_cells_seeding = target_D * dish_count

    # 【修正】まき直し分注量をこの欄の最下段に表示
    if density_C > 0:
        vol_per_dish_mL = target_D / density_C
        total_seeding_vol_mL = vol_per_dish_mL * dish_count
        st.markdown("---")
        st.success(f"✅ **分注量: {label_vol(vol_per_dish_mL)} / 枚**")
        st.caption(f"(全Dish総量: {total_seeding_vol_mL:.3f} mL)")

# --- 4. 凍結保存 (Stock) ---
if density_C > 0:
    with st.container(border=True):
        st.subheader("4. 凍結保存 (Stock)")
        
        remaining_cells = total_cells - required_cells_seeding
        st.write(f"まき直し後の余り細胞: ${format_sci_latex(remaining_cells)}$ 個")
        
        st.markdown("---")
        st.write("**凍結チューブの設計**")
        v_col1, v_col2, v_col3 = st.columns([2, 1, 2])
        with v_col1:
            stock_coeff = st.number_input("1本あたりの細胞数", value=1.0, step=0.1)
        with v_col2:
            stock_expo = st.number_input("× 10^n", value=6, step=1)
        with v_col3:
            vial_count = st.number_input("チューブ本数", value=0, min_value=0)
            
        # 【修正】1本当たりの容量（500μL / 1mL）の選択
        vial_size_label = st.radio("1本あたりの容量", ["500 μL", "1 mL"], horizontal=True)
        vial_size_ml = 0.5 if vial_size_label == "500 μL" else 1.0
            
        cells_per_vial = stock_coeff * (10**stock_expo)
        total_stock_cells_needed = cells_per_vial * vial_count
        
        if total_stock_cells_needed > 0:
            if total_stock_cells_needed > remaining_cells:
                st.error(f"⚠️ 細胞が足りません！ (不足: {format_sci_latex(total_stock_cells_needed - remaining_cells)} 個)")
            else:
                # 今の懸濁液から回収すべき液量
                stock_vol_to_collect_mL = total_stock_cells_needed / density_C
                # 遠心後に加える凍結溶液の総量
                total_freezing_medium_mL = vial_count * vial_size_ml
                
                st.info(f"🧪 **工程指示:**")
                st.write(f"① 現在の懸濁液から **{stock_vol_to_collect_mL:.3f} mL** を回収し、遠心分離。")
                st.write(f"② 上清除去後のペレットに **凍結溶液を {total_freezing_medium_mL:.2f} mL** 加えて懸濁。")
                st.write(f"③ 各チューブに **{vial_size_label}** ずつ分注する。")
                
                discard_vol = resuspension_vol - total_seeding_vol_mL - stock_vol_to_collect_mL
                st.write(f"🗑️ 最終廃棄量: **{max(0.0, discard_vol):.3f} mL**")
        else:
            st.write("凍結保存なし")
