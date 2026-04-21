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
st.set_page_config(page_title="Cell Seeding & Stock Manager", layout="centered")
st.title("🧫 Cell Seeding & Stock Manager")

# --- 1. カウント結果 ---
with st.container(border=True):
    st.subheader("1. カウント結果")
    col_a, col_b = st.columns(2)
    with col_a:
        count_A = st.number_input("カウント数 A (個/0.1mm³)", value=50, min_value=0, step=1)
    with col_b:
        vol_B = st.number_input("回収溶液量 B (mL)", value=5, min_value=1, step=1)
    
    total_cells = count_A * vol_B * 10000
    st.latex(f"現在の総細胞数: {format_sci_latex(total_cells)} \, [cells]")

# --- 2. 懸濁液の調製（まき直し用） ---
with st.container(border=True):
    st.subheader("2. 懸濁液の調製")
    resuspension_vol = st.number_input("ペレットに加える培地量 (mL)", value=5.0, min_value=0.1, step=0.1)
    
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

    # エラーチェック
    if required_cells_seeding > total_cells:
        st.error(f"⚠️ 細胞が足りません！ (不足: {format_sci_latex(required_cells_seeding - total_cells)} 個)")
        remaining_cells = 0
        seeding_possible = False
    else:
        remaining_cells = total_cells - required_cells_seeding
        seeding_possible = True

    if seeding_possible and density_C > 0:
        vol_per_dish_mL = target_D / density_C
        total_seeding_vol_mL = vol_per_dish_mL * dish_count
        st.markdown("---")
        st.success(f"✅ **分注量: {label_vol(vol_per_dish_mL)} / 枚**")
        st.caption(f"(まき直し後の残液量: {max(0.0, resuspension_vol - total_seeding_vol_mL):.3f} mL)")

# --- 4. 凍結保存 (Stock) ---
if seeding_possible and density_C > 0:
    with st.container(border=True):
        st.subheader("4. 凍結保存 (Stock)")
        
        st.write(f"凍結に回せる余り細胞: ${format_sci_latex(remaining_cells)}$ 個")
        
        st.markdown("---")
        st.write("**凍結条件の設定**")
        v_col1, v_col2 = st.columns([2, 1])
        with v_col1:
            stock_coeff = st.number_input("目標密度 (個/tube)", value=1.0, step=0.1)
        with v_col2:
            stock_expo = st.number_input("× 10^n", value=6, step=1)
        
        cells_per_vial = stock_coeff * (10**stock_expo)
        vial_size_label = st.radio("1本あたりの分注量", ["0.5 mL", "1.0 mL"], horizontal=True)
        vial_size_ml = 0.5 if vial_size_label == "0.5 mL" else 1.0
        
        # 最大本数の算出（エラー回避のため下限0）
        max_vials = max(0, int(remaining_cells // cells_per_vial)) if cells_per_vial > 0 else 0
        
        if max_vials > 0:
            st.write(f"現在の細胞数で、目標密度を維持して作れる最大本数: **{max_vials} 本**")
            vial_count = st.number_input("実際に作成するチューブ本数", value=max_vials, min_value=0, max_value=max_vials)
        else:
            st.warning("余り細胞が目標密度に満たないため、凍結ストックは作製できません。")
            vial_count = 0

        # 手順と廃棄表示のロジック
        st.markdown("---")
        if vial_count > 0:
            # 凍結ありの場合
            total_freezing_medium = vial_count * vial_size_ml
            used_stock_cells = cells_per_vial * vial_count
            
            st.info(f"🧪 **凍結工程の手順:**")
            st.write(f"① まき直し後の残液（約 **{max(0.0, resuspension_vol - total_seeding_vol_mL):.3f} mL**）をすべて回収し、遠心分離。")
            st.write(f"② 上清を除去したペレットに **凍結溶液を {total_freezing_medium:.2f} mL 加えて再懸濁。**")
            st.write(f"③ 各チューブに **{vial_size_label}** ずつ、計 **{vial_count} 本** に分注する。")
            
            final_leftover_cells = remaining_cells - used_stock_cells
            st.write(f"🗑️ **最終的な廃棄分:** 約 **{format_sci_latex(max(0.0, final_leftover_cells))} 個**")
        else:
            # 凍結なし（または不可）の場合
            st.write("❄️ **凍結保存は行いません。**")
            # まき直し後に残った細胞をすべて破棄
            st.write(f"🗑️ **最終的な廃棄分:** 約 **{format_sci_latex(remaining_cells)} 個**")
            st.caption(f"(まき直し後の残液 {max(0.0, resuspension_vol - total_seeding_vol_mL):.3f} mL をそのまま廃棄)")
