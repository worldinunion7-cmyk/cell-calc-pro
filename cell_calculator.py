import streamlit as st
import math

# --- 補助関数：科学的表記（LaTeX） ---
def format_sci_latex(val):
    if val <= 0: return "0"
    exponent = int(math.floor(math.log10(abs(val))))
    coeff = val / (10**exponent)
    return f"{coeff:.2f} \\times 10^{{{exponent}}}"

# --- アプリ設定 ---
st.set_page_config(page_title="Cell Susp Calc", layout="centered")
st.title("🧫 Cell Suspension & Seeding")

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

# --- 2. 懸濁液の調製（濃度算出） ---
with st.container(border=True):
    st.subheader("2. 懸濁液の調製")
    # サクション後のペレットに加える培地量
    resuspension_vol = st.number_input("ペレットに加える培地量 (mL)", value=5.0, step=0.1)
    
    if resuspension_vol > 0:
        density_C = total_cells / resuspension_vol
        st.info(f"💡 **細胞懸濁液の濃度 (C):**")
        st.latex(f"C = {format_sci_latex(density_C)} \, [cells/mL]")
    else:
        density_C = 0

# --- 3. まき直し設定 ---
with st.container(border=True):
    st.subheader("3. まき直し設定")
    
    st.write("1枚あたりの目標細胞数 D")
    c_col, e_col = st.columns([2, 1])
    with c_col:
        # デフォルトを 2.0 に設定
        d_coeff = st.number_input("係数", value=2.0, step=0.1, key="d_c")
    with e_col:
        # デフォルトを 10^6 に設定
        d_expo = st.number_input("指数 10^x", value=6, step=1, key="d_e")
    target_D = d_coeff * (10**d_expo)
    st.latex(f"D = {format_sci_latex(target_D)} \, [cells/dish]")

    dish_count = st.number_input("まくDishの枚数", value=1, min_value=1)
    required_cells_total = target_D * dish_count

# --- 4. 分注量と余りの計算 ---
if density_C > 0:
    with st.container(border=True):
        st.subheader("4. 分注指示と余剰管理")
        
        # 1枚あたりの分注量 (mL)
        vol_per_dish_mL = target_D / density_C
        # 総分注量 (mL)
        total_seeding_vol_mL = vol_per_dish_mL * dish_count
        
        # 表示の切り替え（mLまたはμL）
        def label_vol(v_ml):
            return f"{v_ml*1000:.1f} μL" if v_ml < 1 else f"{v_ml:.3f} mL"

        col1, col2 = st.columns(2)
        col1.metric("1枚あたりの分注量", label_vol(vol_per_dish_mL))
        col2.metric("総分注量 (全Dish)", f"{total_seeding_vol_mL:.3f} mL")
        
        if total_seeding_vol_mL > resuspension_vol:
            st.error(f"⚠️ 細胞溶液が足りません！ (不足: {total_seeding_vol_mL - resuspension_vol:.2f} mL)")
        else:
            st.markdown("---")
            # 余剰分の管理
            remaining_vol_mL = resuspension_vol - total_seeding_vol_mL
            remaining_cells = remaining_vol_mL * density_C
            
            st.write("▼ 余った細胞の処理")
            st.latex(f"現在の余り細胞数: {format_sci_latex(remaining_cells)}")
            
            # ご指示：余りの細胞数を入力する欄
            st.caption("凍結保存などに回す目標細胞数を入力してください")
            save_c_col, save_e_col = st.columns([2, 1])
            with save_c_col:
                s_coeff = st.number_input("保存用係数", value=1.0, step=0.1)
            with save_e_col:
                s_expo = st.number_input("保存用指数 10^x", value=6, step=1)
            target_save_cells = s_coeff * (10**s_expo)
            
            if target_save_cells > 0:
                save_vol_mL = target_save_cells / density_C
                st.success(f"✅ **保存用に回収する液量: {save_vol_mL:.3f} mL**")
                
                final_discard_vol = remaining_vol_mL - save_vol_mL
                if final_discard_vol >= 0:
                    st.write(f"🗑️ 最終的な廃棄量: **{final_discard_vol:.3f} mL**")
                else:
                    st.warning("⚠️ 保存したい細胞数が、余っている細胞数を超えています。")
