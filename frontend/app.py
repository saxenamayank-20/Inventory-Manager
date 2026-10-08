import os

import streamlit as st
import requests
from dotenv import load_dotenv

# ─────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────
load_dotenv()

# backend url, set BACKEND_URL to point at a local backend
BASE_URL = os.getenv("BACKEND_URL", "https://inventory-manager-sqqa.onrender.com").rstrip("/")
# render free plan goes to sleep, so first call can be slow
TIMEOUT = 60

st.set_page_config(
    page_title="📦 Item Inventory Manager",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# Custom CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Dark glassmorphism sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(160deg, #0f0c29, #302b63, #24243e) !important;
    }
    [data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }

    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        color: #f1f5f9;
    }

    /* Card style */
    .card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        transition: transform 0.2s ease;
    }
    .card:hover {
        transform: translateY(-2px);
    }

    /* Metric cards */
    [data-testid="metric-container"] {
        background: rgba(255,255,255,0.07);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 16px;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 24px;
        font-weight: 600;
        font-size: 15px;
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #764ba2, #667eea);
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(102,126,234,0.4);
    }

    /* Inputs */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 10px !important;
        color: #f1f5f9 !important;
        padding: 10px 14px !important;
    }

    /* Success / Error alerts */
    .stSuccess, .stError, .stInfo, .stWarning {
        border-radius: 10px !important;
    }

    /* Dataframe */
    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
    }

    /* Section headers */
    .section-header {
        font-size: 24px;
        font-weight: 700;
        color: #a78bfa;
        margin-bottom: 8px;
        border-bottom: 2px solid rgba(167,139,250,0.3);
        padding-bottom: 8px;
    }
    .sub-header {
        font-size: 14px;
        color: #94a3b8;
        margin-bottom: 20px;
    }
    
    /* Nav radio buttons */
    .stRadio > div {
        gap: 8px;
    }
    .stRadio > div > label {
        background: rgba(255,255,255,0.05);
        border-radius: 10px;
        padding: 10px 16px !important;
        border: 1px solid rgba(255,255,255,0.1);
        transition: all 0.2s ease;
    }
    .stRadio > div > label:hover {
        background: rgba(102,126,234,0.2);
        border-color: #667eea;
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────
def fetch_all_items():
    try:
        r = requests.get(f"{BASE_URL}/items", timeout=TIMEOUT)
        if r.status_code == 200:
            return r.json()
    except requests.exceptions.RequestException:
        st.error(f"❌ Cannot connect to backend at {BASE_URL}")
    return []


def error_detail(r, default):
    # a 500 comes back as plain text, not json
    try:
        return r.json().get("detail", default)
    except ValueError:
        return r.text or default


def check_backend():
    try:
        r = requests.get(BASE_URL, timeout=TIMEOUT)
        return r.status_code == 200
    except requests.exceptions.RequestException:
        return False


# ─────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📦 Inventory Manager")
    st.markdown("---")

    # Backend status indicator
    if check_backend():
        st.success("✅ API Connected")
    else:
        st.error("❌ API Offline")

    st.markdown("### 🗂️ Navigation")
    page = st.radio(
        "Go to",
        ["🏠 Dashboard", "➕ Add Item", "✏️ Update Item", "🗑️ Delete Item", "🔍 Search Items"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.markdown("**📡 Backend URL**")
    st.code(BASE_URL)
    st.markdown("**📖 API Docs**")
    st.markdown(f"[Open Swagger UI]({BASE_URL}/docs)")


# ─────────────────────────────────────────────
# Dashboard Page
# ─────────────────────────────────────────────
if page == "🏠 Dashboard":
    st.markdown('<p class="section-header">🏠 Inventory Dashboard</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Overview of all items in the inventory database.</p>', unsafe_allow_html=True)

    items = fetch_all_items()

    if items:
        # KPI metrics
        total_items = len(items)
        total_quantity = sum(i["quantity"] for i in items)
        total_value = sum(i["price"] * i["quantity"] for i in items)
        avg_price = sum(i["price"] for i in items) / total_items

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("📦 Total Products",  total_items)
        col2.metric("🔢 Total Quantity",  total_quantity)
        col3.metric("💰 Inventory Value", f"₹{total_value:,.2f}")
        col4.metric("📊 Avg. Price",      f"₹{avg_price:,.2f}")

        st.markdown("---")
        st.markdown("### 📋 All Items")

        # Format for display
        import pandas as pd
        df = pd.DataFrame(items)
        df = df[["id", "name", "description", "price", "quantity", "created_at"]]
        df.columns = ["ID", "Name", "Description", "Price (₹)", "Quantity", "Created At"]
        df["Price (₹)"] = df["Price (₹)"].map(lambda x: f"₹{x:,.2f}")
        df["Created At"] = pd.to_datetime(df["Created At"]).dt.strftime("%Y-%m-%d %H:%M")
        st.dataframe(df, width="stretch", hide_index=True)
    else:
        st.info("🫙 No items in inventory yet. Use **➕ Add Item** to get started!")


# ─────────────────────────────────────────────
# Add Item Page
# ─────────────────────────────────────────────
elif page == "➕ Add Item":
    st.markdown('<p class="section-header">➕ Add New Item</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Fill in the details below to add a new product to the inventory.</p>', unsafe_allow_html=True)

    with st.form("add_item_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name        = st.text_input("📛 Item Name *", placeholder="e.g. Laptop")
            price       = st.number_input("💰 Price (₹) *", min_value=0.01, step=0.01, format="%.2f")
        with col2:
            quantity    = st.number_input("🔢 Quantity *", min_value=0, step=1)
            description = st.text_area("📝 Description", placeholder="Optional description...", height=100)

        submitted = st.form_submit_button("➕ Add Item to Inventory")

    if submitted:
        if not name.strip():
            st.error("❌ Item name is required.")
        else:
            payload = {
                "name": name.strip(),
                "description": description.strip() or None,
                "price": float(price),
                "quantity": int(quantity),
            }
            try:
                r = requests.post(f"{BASE_URL}/items", json=payload, timeout=TIMEOUT)
                if r.status_code == 201:
                    item = r.json()
                    st.success(f"✅ Item **{item['name']}** added successfully! (ID: {item['id']})")
                    st.json(item)
                else:
                    st.error(f"❌ Error: {error_detail(r, r.text)}")
            except requests.exceptions.RequestException:
                st.error("❌ Cannot reach backend. Is FastAPI running?")


# ─────────────────────────────────────────────
# Update Item Page
# ─────────────────────────────────────────────
elif page == "✏️ Update Item":
    st.markdown('<p class="section-header">✏️ Update Existing Item</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Enter an Item ID and update any of its fields.</p>', unsafe_allow_html=True)

    item_id = st.number_input("🔍 Enter Item ID to Update", min_value=1, step=1, key="update_id")

    # Fetch current data for preview
    if st.button("📥 Load Item Data"):
        try:
            r = requests.get(f"{BASE_URL}/items/{int(item_id)}", timeout=TIMEOUT)
            if r.status_code == 200:
                st.session_state["loaded_item"] = r.json()
                st.success("✅ Item loaded! Modify the fields below.")
            else:
                st.error(f"❌ {error_detail(r, 'Item not found')}")
                st.session_state.pop("loaded_item", None)
        except requests.exceptions.RequestException:
            st.error("❌ Cannot reach backend.")

    # Show update form if item is loaded
    if "loaded_item" in st.session_state:
        item = st.session_state["loaded_item"]
        st.info(f"📦 Editing: **{item['name']}** (ID: {item['id']})")

        with st.form("update_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_name  = st.text_input("📛 Name",     value=item["name"])
                new_price = st.number_input("💰 Price (₹)", value=float(item["price"]), min_value=0.01, step=0.01, format="%.2f")
            with col2:
                new_qty   = st.number_input("🔢 Quantity", value=int(item["quantity"]), min_value=0, step=1)
                new_desc  = st.text_area("📝 Description", value=item.get("description") or "", height=100)

            update_btn = st.form_submit_button("💾 Save Changes")

        if update_btn:
            payload = {
                "name":        new_name.strip() or None,
                "description": new_desc.strip() or None,
                "price":       float(new_price),
                "quantity":    int(new_qty),
            }
            try:
                r = requests.put(f"{BASE_URL}/items/{item['id']}", json=payload, timeout=TIMEOUT)
                if r.status_code == 200:
                    st.success(f"✅ Item **{r.json()['name']}** updated successfully!")
                    st.json(r.json())
                    del st.session_state["loaded_item"]
                else:
                    st.error(f"❌ {error_detail(r, 'Update failed')}")
            except requests.exceptions.RequestException:
                st.error("❌ Cannot reach backend.")


# ─────────────────────────────────────────────
# Delete Item Page
# ─────────────────────────────────────────────
elif page == "🗑️ Delete Item":
    st.markdown('<p class="section-header">🗑️ Delete Item</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Permanently remove an item from the inventory.</p>', unsafe_allow_html=True)

    item_id = st.number_input("🔍 Enter Item ID to Delete", min_value=1, step=1, key="del_id")

    # Preview before delete
    if st.button("🔎 Preview Item"):
        try:
            r = requests.get(f"{BASE_URL}/items/{int(item_id)}", timeout=TIMEOUT)
            if r.status_code == 200:
                st.session_state["delete_preview"] = r.json()
            else:
                st.error(f"❌ {error_detail(r, 'Item not found')}")
                st.session_state.pop("delete_preview", None)
        except requests.exceptions.RequestException:
            st.error("❌ Cannot reach backend.")

    if "delete_preview" in st.session_state:
        item = st.session_state["delete_preview"]
        st.warning(f"⚠️ You are about to delete: **{item['name']}** (ID: {item['id']}, Price: ₹{item['price']}, Qty: {item['quantity']})")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Confirm Delete", type="primary"):
                try:
                    r = requests.delete(f"{BASE_URL}/items/{item['id']}", timeout=TIMEOUT)
                    if r.status_code == 200:
                        st.success(r.json().get("message", "Deleted!"))
                        del st.session_state["delete_preview"]
                    else:
                        st.error(f"❌ {error_detail(r, 'Delete failed')}")
                except requests.exceptions.RequestException:
                    st.error("❌ Cannot reach backend.")
        with col2:
            if st.button("❌ Cancel"):
                st.session_state.pop("delete_preview", None)
                st.rerun()


# ─────────────────────────────────────────────
# Search Items Page
# ─────────────────────────────────────────────
elif page == "🔍 Search Items":
    st.markdown('<p class="section-header">🔍 Search Items</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Search the inventory by item name (partial match supported).</p>', unsafe_allow_html=True)

    keyword = st.text_input("🔎 Enter search keyword", placeholder="e.g. lap")
    if st.button("🔍 Search") and keyword:
        try:
            r = requests.get(f"{BASE_URL}/items/search", params={"keyword": keyword}, timeout=TIMEOUT)
            if r.status_code == 200:
                results = r.json()
                st.success(f"✅ Found **{len(results)}** item(s) matching **'{keyword}'**")
                import pandas as pd
                df = pd.DataFrame(results)[["id", "name", "description", "price", "quantity"]]
                df.columns = ["ID", "Name", "Description", "Price (₹)", "Qty"]
                df["Price (₹)"] = df["Price (₹)"].map(lambda x: f"₹{x:,.2f}")
                st.dataframe(df, width="stretch", hide_index=True)
            else:
                st.warning(f"🔍 {error_detail(r, 'No results found')}")
        except requests.exceptions.RequestException:
            st.error("❌ Cannot reach backend.")
