import streamlit as st
import pandas as pd

# 页面基础配置：宽屏模式
st.set_page_config(
    page_title="Daily Operations Control Tower",
    page_icon="⚡",
    layout="wide"
)

# 压缩顶部空白，保证一屏看全
st.markdown("""
<style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
    }
</style>
""", unsafe_allow_html=True)

# 1. 模拟数据库初始化
if "orders_df" not in st.session_state:
    st.session_state.orders_df = pd.DataFrame([
        {
            "Order_ID": "DX-8801",
            "Customer": "Costco Wholesale",
            "Gate": "Finance Hold",
            "Pending_Reason": "Credit limit exceeded ($180k over)",
            "Pending_Hours": 28,
            "Penalty_Risk": True,
            "Value ($)": 342000,
            "Owner": "Finance - Sarah",
            "Action_Status": "Blocked",
            "Operational_Notes": "Waiting for wire receipt confirmation today"
        },
        {
            "Order_ID": "DX-8804",
            "Customer": "Sysco Supply",
            "Gate": "Warehouse Hold",
            "Pending_Reason": "Stockout: SKU-Nitrile (2,000 cases)",
            "Pending_Hours": 18,
            "Penalty_Risk": True,
            "Value ($)": 94500,
            "Owner": "Warehouse - Mike",
            "Action_Status": "In Progress",
            "Operational_Notes": "Inbound container ETA 4:00 PM at Dock 4"
        },
        {
            "Order_ID": "DX-8809",
            "Customer": "US Foods",
            "Gate": "CSR Review",
            "Pending_Reason": "Custom packaging barcode clause ambiguous",
            "Pending_Hours": 14,
            "Penalty_Risk": False,
            "Value ($)": 128000,
            "Owner": "CSR - Emily",
            "Action_Status": "Investigating",
            "Operational_Notes": "AI extracted clause on p.42; sales confirming"
        },
        {
            "Order_ID": "DX-8812",
            "Customer": "Bunzl Distribution",
            "Gate": "Logistics Hold",
            "Pending_Reason": "Carrier delayed pickup > 8h past appointment",
            "Pending_Hours": 9,
            "Penalty_Risk": False,
            "Value ($)": 67000,
            "Owner": "Logistics - Dave",
            "Action_Status": "Blocked",
            "Operational_Notes": "Carrier repatched new driver ETA 11:30 AM"
        },
        {
            "Order_ID": "DX-8815",
            "Customer": "Performance Food",
            "Gate": "Warehouse Hold",
            "Pending_Reason": "Pallet height constraint (Max 1.5m)",
            "Pending_Hours": 6,
            "Penalty_Risk": False,
            "Value ($)": 45000,
            "Owner": "Warehouse - Mike",
            "Action_Status": "Resolved",
            "Operational_Notes": "Re-stacked into 1.4m tier pallets; staged"
        },
        {
            "Order_ID": "DX-8820",
            "Customer": "McLane Foodservice",
            "Gate": "Finance Hold",
            "Pending_Reason": "Net 60 term verification against Contract",
            "Pending_Hours": 4,
            "Penalty_Risk": False,
            "Value ($)": 210000,
            "Owner": "Finance - Sarah",
            "Action_Status": "In Progress",
            "Operational_Notes": "Matched with contract appendix A"
        }
    ])

df = st.session_state.orders_df

# 2. 顶部标题栏
st.title("⚡ Daily Operations Control Tower")
st.caption("8:00 AM Morning Standup & Closed-Loop Operations Workbench")

# 3. 统计指标卡
p0_count = len(df[(df["Pending_Hours"] >= 12) & (df["Penalty_Risk"] == True) & (df["Action_Status"] != "Resolved")])
p1_count = len(df[(df["Action_Status"] != "Resolved") & ~((df["Pending_Hours"] >= 12) & (df["Penalty_Risk"] == True))])
resolved_count = len(df[df["Action_Status"] == "Resolved"])
total_blocked_val = df[df["Action_Status"] != "Resolved"]["Value ($)"].sum()

col1, col2, col3, col4 = st.columns(4)
col1.metric("🔴 P0 Urgent (>12h & Penalty)", f"{p0_count} Orders", "Immediate Action", delta_color="inverse")
col2.metric("🟡 P1 Holds (In Triage)", f"{p1_count} Orders", "Standard holds")
col3.metric("🟢 Resolved Today", f"{resolved_count} Orders", "Ready to ship")
col4.metric("💰 Blocked Pipeline Value", f"${total_blocked_val:,.0f}", "Pending Cash")

st.markdown("---")

# 4. Tabs 门禁切换
tabs = st.tabs(["🔥 All Active Blockers", "📝 CSR Review", "💳 Finance Hold", "🏭 Warehouse Hold", "🚚 Logistics Hold", "✅ All (Inc. Resolved)"])

gate_mapping = {
    1: "CSR Review",
    2: "Finance Hold",
    3: "Warehouse Hold",
    4: "Logistics Hold"
}

for i, tab in enumerate(tabs):
    with tab:
        if i == 0:
            view_df = df[df["Action_Status"] != "Resolved"]
        elif i == 5:
            view_df = df
        else:
            view_df = df[(df["Gate"] == gate_mapping[i]) & (df["Action_Status"] != "Resolved")]
        
        # 兼容性调用：直接传入 DataFrame，老版本也能完美交互编辑
        try:
            edited = st.data_editor(view_df, use_container_width=True, key=f"editor_{i}")
        except AttributeError:
            # 如果 Streamlit 版本极老连 data_editor 都没有，降级到交互表格
            edited = st.experimental_data_editor(view_df, use_container_width=True, key=f"editor_{i}")

# 5. 保存闭环按钮
c1, c2 = st.columns([2, 5])
with c1:
    if st.button("💾 Save Changes & Sync to DB", type="primary"):
        st.success("✅ Changes synced back to internal database!")
with c2:
    if st.button("🔄 Trigger Morning 6:00 AM ETL"):
        st.info("Pipeline refreshed.")

