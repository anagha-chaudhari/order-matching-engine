import os

import streamlit as st
import requests
import time

API_BASE = os.environ.get("API_BASE", "http://127.0.0.1:8000")

st.set_page_config(page_title="Market Simulator", layout="wide")

# -------------------------------------------------
# Styling
# -------------------------------------------------
st.markdown("""
<style>
.title { font-size: 34px; font-weight: 600; }
.section { font-size: 22px; font-weight: 600; margin-top: 10px; }
.box { background: #f8f9fa; padding: 12px; border-radius: 8px; margin-bottom: 6px; }
.event-trade { background: #d4edda; padding: 8px; border-radius: 6px; margin-bottom: 6px; }
.event-order { background: #f1f3f5; padding: 6px; border-radius: 6px; margin-bottom: 4px; }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# Header
# -------------------------------------------------
st.markdown('<div class="title">Real-Time Market Simulator</div>', unsafe_allow_html=True)
st.caption("Interactive dashboard for order matching engine with live metrics and controls")

st.divider()

# -------------------------------------------------
# Market Controls
# -------------------------------------------------
st.markdown('<div class="section">Market Controls</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns([2, 1, 1])

with c1:
    speed = st.slider("Market Speed (lower = faster)", 0.05, 1.5, 0.5, 0.05)
    if st.button("Apply Speed"):
        try:
            requests.post(f"{API_BASE}/speed/{speed}")
            st.success(f"Speed updated to {speed}s delay")
        except:
            st.error("Backend unreachable")

with c2:
    if st.button("Pause Market", use_container_width=True):
        try:
            requests.post(f"{API_BASE}/pause")
            st.success("Market paused")
        except:
            st.error("Pause failed")

with c3:
    if st.button("Resume Market", use_container_width=True):
        try:
            requests.post(f"{API_BASE}/resume")
            st.success("Market resumed")
        except:
            st.error("Resume failed")

st.divider()

# -------------------------------------------------
# Sidebar: Manual order
# -------------------------------------------------
st.sidebar.header("Manual Order")

side = st.sidebar.selectbox("Side", ["buy", "sell"])
price = st.sidebar.number_input("Price", value=100.0, step=0.5)
quantity = st.sidebar.number_input("Quantity", value=5, step=1)

if st.sidebar.button("Submit Order", use_container_width=True):
    payload = {"side": side, "price": price, "quantity": quantity}
    try:
        res = requests.post(f"{API_BASE}/orders", json=payload)
        if res.status_code == 200:
            st.sidebar.success("Order sent to engine")
        else:
            st.sidebar.error("Order rejected")
    except:
        st.sidebar.error("Backend unreachable")

# -------------------------------------------------
# Safe fetch helper
# -------------------------------------------------
def safe_get(endpoint):
    try:
        r = requests.get(f"{API_BASE}/{endpoint}", timeout=2)
        if r.status_code == 200:
            return r.json()
    except:
        return None
    return None

orderbook = safe_get("orderbook") or {"buy_orders": [], "sell_orders": []}
trades = safe_get("trades") or []
events = safe_get("events") or []
metrics = safe_get("metrics") or {}

# -------------------------------------------------
# Metrics
# -------------------------------------------------
st.markdown('<div class="section">System Performance</div>', unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Orders", metrics.get("orders", 0))
m2.metric("Total Trades", metrics.get("trades", 0))
m3.metric("Orders/sec", metrics.get("orders_per_sec", 0))
m4.metric("Latency (ms)", metrics.get("avg_latency_ms", 0))

m5, m6 = st.columns(2)
m5.metric("Trades/sec", metrics.get("trades_per_sec", 0))
m6.metric("Match Rate", f"{metrics.get('match_rate_percent', 0)}%")

st.divider()

# -------------------------------------------------
# Market Overview
# -------------------------------------------------
st.markdown('<div class="section">Market Overview</div>', unsafe_allow_html=True)

last_price = trades[-1]["price"] if trades else None

buy_prices = [o["price"] for o in orderbook["buy_orders"]]
sell_prices = [o["price"] for o in orderbook["sell_orders"]]

best_bid = max(buy_prices) if buy_prices else None
best_ask = min(sell_prices) if sell_prices else None

spread = round(best_ask - best_bid, 4) if best_bid and best_ask else None
recent_volume = sum(t["quantity"] for t in trades[-20:]) if trades else 0

o1, o2, o3 = st.columns(3)

o1.metric("Last Price", last_price if last_price else "-")
o2.metric("Bid–Ask Spread", spread if spread is not None else "-")
o3.metric("Recent Volume", recent_volume)

st.divider()

# -------------------------------------------------
# Orderbook + Events
# -------------------------------------------------
left, right = st.columns([2, 2])

with left:
    st.markdown('<div class="section">Order Book</div>', unsafe_allow_html=True)

    b1, b2 = st.columns(2)

    with b1:
        st.markdown("**Buy Orders**")
        st.dataframe(orderbook["buy_orders"], height=260, use_container_width=True)

    with b2:
        st.markdown("**Sell Orders**")
        st.dataframe(orderbook["sell_orders"], height=260, use_container_width=True)

with right:
    st.markdown('<div class="section">Engine Activity</div>', unsafe_allow_html=True)

    for e in events[:20]:
        if "Trade executed" in e:
            st.markdown(f"<div class='event-trade'>🟢 {e}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='event-order'>• {e}</div>", unsafe_allow_html=True)

st.divider()


# -------------------------------------------------
# Volume Chart
# -------------------------------------------------
st.markdown('<div class="section">Trade Volume</div>', unsafe_allow_html=True)

if trades:
    volumes = [t["quantity"] for t in trades[-150:]]
    st.bar_chart(volumes, height=200, use_container_width=True)
else:
    st.caption("Waiting for trades...")

st.divider()

# -------------------------------------------------
# Recent Trades
# -------------------------------------------------
st.markdown('<div class="section">Recent Trades</div>', unsafe_allow_html=True)

if trades:
    for t in reversed(trades[-10:]):
        st.markdown(
            f"<div class='box'>Trade: {t['quantity']} @ {t['price']}</div>",
            unsafe_allow_html=True
        )
else:
    st.caption("No trades yet")

# -------------------------------------------------
# Auto refresh
# -------------------------------------------------
time.sleep(1)
st.rerun()
