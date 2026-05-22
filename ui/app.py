import os
import streamlit as st
import requests
import time
import pandas as pd

API_BASE = os.environ.get("API_BASE", "http://127.0.0.1:8000")

st.set_page_config(page_title="Order Matching Engine", layout="wide", page_icon="📈")

# ─────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Global ── */
[data-testid="stAppViewContainer"] { background: #f5f5f3; }
[data-testid="stSidebar"] { background: #ffffff; border-right: 1px solid #e8e8e5; }
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { padding-top: 0.5rem; }

/* ── Typography ── */
.page-title   { font-size: 22px; font-weight: 600; color: #1a1a18; letter-spacing: -0.3px; margin-bottom: 2px; }
.page-sub     { font-size: 13px; color: #888780; margin-bottom: 0; }
.section-label{ font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; color: #888780; margin-bottom: 10px; }

/* ── Ticker bar ── */
.ticker-bar { display: flex; align-items: center; gap: 18px; background: #fff; border: 1px solid #e8e8e5; border-radius: 10px; padding: 12px 20px; margin-bottom: 16px; }
.ticker-name  { font-size: 15px; font-weight: 600; color: #1a1a18; }
.ticker-price { font-size: 26px; font-weight: 600; color: #1a1a18; font-variant-numeric: tabular-nums; }
.badge-up   { background: #e1f5ee; color: #0f6e56; font-size: 12px; font-weight: 600; padding: 3px 10px; border-radius: 5px; }
.badge-down { background: #fcebeb; color: #a32d2d; font-size: 12px; font-weight: 600; padding: 3px 10px; border-radius: 5px; }
.ticker-meta  { margin-left: auto; font-size: 12px; color: #888780; }
.ticker-meta span { color: #1a1a18; font-weight: 500; }

/* ── Metric cards ── */
.metric-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; margin-bottom: 16px; }
.metric-card { background: #fff; border: 1px solid #e8e8e5; border-radius: 10px; padding: 12px 16px; }
.metric-card .lbl { font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.07em; color: #888780; margin-bottom: 4px; }
.metric-card .val { font-size: 22px; font-weight: 600; color: #1a1a18; font-variant-numeric: tabular-nums; }
.metric-card .sub { font-size: 11px; color: #888780; margin-top: 2px; }
.sub-up   { color: #0f6e56 !important; }
.sub-down { color: #a32d2d !important; }

/* ── Order book ── */
.ob-card { background: #fff; border: 1px solid #e8e8e5; border-radius: 10px; overflow: hidden; }
.ob-header { display: grid; grid-template-columns: 1fr 1fr; border-bottom: 1px solid #e8e8e5; }
.ob-side-title { padding: 8px 14px; font-size: 11px; font-weight: 600; }
.ob-side-bid  { color: #0f6e56; border-right: 1px solid #e8e8e5; }
.ob-side-ask  { color: #a32d2d; }
.ob-row { display: grid; grid-template-columns: 1fr 1fr; padding: 5px 14px; font-size: 12px; font-family: monospace; position: relative; border-bottom: 1px solid #f0f0ee; }
.ob-row:last-child { border-bottom: none; }
.ob-price-bid { color: #0f6e56; font-weight: 600; }
.ob-price-ask { color: #a32d2d; font-weight: 600; }
.ob-qty { text-align: right; color: #444441; }
.ob-depth { position: absolute; top: 0; bottom: 0; opacity: 0.07; pointer-events: none; }
.ob-depth-bid { background: #1d9e75; right: 0; }
.ob-depth-ask { background: #e24b4a; left: 0; }
.ob-spread-row { background: #f8f8f6; text-align: center; padding: 5px; font-size: 11px; color: #888780; border-top: 1px solid #e8e8e5; border-bottom: 1px solid #e8e8e5; }

/* ── Activity feed ── */
.feed-card { background: #fff; border: 1px solid #e8e8e5; border-radius: 10px; overflow: hidden; }
.feed-item { display: flex; align-items: flex-start; gap: 10px; padding: 8px 14px; border-bottom: 1px solid #f0f0ee; font-size: 12px; }
.feed-item:last-child { border-bottom: none; }
.feed-dot { width: 7px; height: 7px; border-radius: 50%; margin-top: 3px; flex-shrink: 0; }
.dot-trade  { background: #1d9e75; }
.dot-order  { background: #378add; }
.dot-cancel { background: #e24b4a; }
.feed-text  { color: #5f5e5a; flex: 1; line-height: 1.4; }
.feed-text b { color: #1a1a18; font-weight: 600; }
.feed-time  { font-size: 10px; color: #b4b2a9; font-family: monospace; padding-top: 1px; }

/* ── Recent trades ── */
.trade-row { display: flex; align-items: center; justify-content: space-between; padding: 8px 14px; border-bottom: 1px solid #f0f0ee; font-size: 13px; background: #fff; }
.trade-row:last-child { border-bottom: none; }
.trade-pair { font-family: monospace; color: #444441; }
.trade-badge { font-size: 11px; padding: 2px 8px; border-radius: 4px; background: #e1f5ee; color: #0f6e56; font-weight: 600; }
.trade-badge-lg { background: #e6f1fb; color: #185fa5; }

/* ── Sidebar ── */
.sidebar-section { font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; color: #888780; padding: 6px 0 8px; }
.speed-status { font-size: 12px; color: #888780; padding: 4px 0 10px; }
.speed-status span { color: #1d9e75; font-weight: 600; }

/* ── Control buttons ── */
.stButton > button {
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    border: 1px solid #d3d1c7 !important;
    background: #fff !important;
    color: #444441 !important;
    transition: all 0.15s !important;
}
.stButton > button:hover { background: #f5f5f3 !important; border-color: #b4b2a9 !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# Helper
# ─────────────────────────────────────────────────────────────
def safe_get(endpoint):
    try:
        r = requests.get(f"{API_BASE}/{endpoint}", timeout=2)
        if r.status_code == 200:
            return r.json()
    except Exception:
        return None
    return None

# ─────────────────────────────────────────────────────────────
# Fetch data
# ─────────────────────────────────────────────────────────────
orderbook = safe_get("orderbook") or {"buy_orders": [], "sell_orders": []}
trades    = safe_get("trades")    or []
events    = safe_get("events")    or []
metrics   = safe_get("metrics")   or {}

buy_orders  = orderbook.get("buy_orders",  [])
sell_orders = orderbook.get("sell_orders", [])

buy_prices  = [o["price"] for o in buy_orders]
sell_prices = [o["price"] for o in sell_orders]
best_bid    = max(buy_prices)  if buy_prices  else None
best_ask    = min(sell_prices) if sell_prices else None
spread      = round(best_ask - best_bid, 4) if best_bid and best_ask else None
mid         = round((best_ask + best_bid) / 2, 4) if best_bid and best_ask else None
last_price  = trades[-1]["price"] if trades else None
prev_price  = trades[-2]["price"] if len(trades) >= 2 else last_price

pct_change  = None
if last_price and prev_price and prev_price != 0:
    pct_change = round((last_price - prev_price) / prev_price * 100, 2)

total_orders  = metrics.get("orders", 0)
total_trades  = metrics.get("trades", 0)
orders_ps     = metrics.get("orders_per_sec", 0)
trades_ps     = metrics.get("trades_per_sec", 0)
latency       = metrics.get("avg_latency_ms", 0)
match_rate    = metrics.get("match_rate_percent", 0)

# ─────────────────────────────────────────────────────────────
# Sidebar — Manual Order + Speed
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-section">New Order</div>', unsafe_allow_html=True)

    side     = st.selectbox("Side", ["buy", "sell"], label_visibility="collapsed")
    price_in = st.number_input("Price",    value=100.0, step=0.5,  format="%.2f")
    qty_in   = st.number_input("Quantity", value=5,     step=1,    min_value=1)

    btn_label = f"{'🟢 Buy' if side == 'buy' else '🔴 Sell'}  {qty_in} @ {price_in:.2f}"
    if st.button(btn_label, use_container_width=True):
        payload = {"side": side, "price": price_in, "quantity": qty_in}
        try:
            res = requests.post(f"{API_BASE}/orders", json=payload)
            if res.status_code == 200:
                st.success("✓ Order sent to engine")
            else:
                st.error("✗ Order rejected")
        except Exception:
            st.error("✗ Backend unreachable")

    st.divider()
    st.markdown('<div class="sidebar-section">Market Speed</div>', unsafe_allow_html=True)

    speed = st.slider("Delay (s) — lower = faster", 0.05, 1.5, 0.5, 0.05,
                      label_visibility="visible")
    st.markdown(f'<div class="speed-status">Interval: <span>{speed:.2f}s</span></div>',
                unsafe_allow_html=True)

    col_apply, col_pause, col_resume = st.columns(3)
    with col_apply:
        if st.button("Apply", use_container_width=True):
            try:
                requests.post(f"{API_BASE}/speed/{speed}")
                st.success(f"Set {speed}s")
            except Exception:
                st.error("Failed")
    with col_pause:
        if st.button("Pause", use_container_width=True):
            try:
                requests.post(f"{API_BASE}/pause")
                st.warning("Paused")
            except Exception:
                st.error("Failed")
    with col_resume:
        if st.button("Run", use_container_width=True):
            try:
                requests.post(f"{API_BASE}/resume")
                st.success("Running")
            except Exception:
                st.error("Failed")

# ─────────────────────────────────────────────────────────────
# Page header
# ─────────────────────────────────────────────────────────────
st.markdown('<div class="page-title">Order Matching Engine</div>', unsafe_allow_html=True)
st.markdown('<div class="page-sub">Real-time order book · trade feed · performance metrics</div>',
            unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# Ticker bar
# ─────────────────────────────────────────────────────────────
if last_price is not None:
    badge_cls = "badge-up" if (pct_change or 0) >= 0 else "badge-down"
    badge_txt = f"{'▲' if (pct_change or 0) >= 0 else '▼'} {abs(pct_change or 0):.2f}%"
    spread_html = f"Spread: <span>{spread if spread else '—'}</span> &nbsp;·&nbsp; Mid: <span>{mid if mid else '—'}</span>"
    st.markdown(f"""
    <div class="ticker-bar">
        <span class="ticker-name">AAPL</span>
        <span class="ticker-price">{last_price:.2f}</span>
        <span class="{badge_cls}">{badge_txt}</span>
        <span class="ticker-meta">{spread_html}</span>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# Metrics bar (5 cards)
# ─────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="metric-grid">
  <div class="metric-card">
    <div class="lbl">Total Orders</div>
    <div class="val">{total_orders}</div>
    <div class="sub sub-up">↑ {orders_ps:.2f}/sec</div>
  </div>
  <div class="metric-card">
    <div class="lbl">Total Trades</div>
    <div class="val">{total_trades}</div>
    <div class="sub sub-up">↑ {trades_ps:.2f}/sec</div>
  </div>
  <div class="metric-card">
    <div class="lbl">Match Rate</div>
    <div class="val">{match_rate:.1f}%</div>
    <div class="sub">of all orders</div>
  </div>
  <div class="metric-card">
    <div class="lbl">Orders/sec</div>
    <div class="val">{orders_ps:.2f}</div>
    <div class="sub">avg throughput</div>
  </div>
  <div class="metric-card">
    <div class="lbl">Latency</div>
    <div class="val">{latency:.2f}<span style="font-size:14px;color:#888780">ms</span></div>
    <div class="sub sub-up">optimal</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# Order book + Activity feed
# ─────────────────────────────────────────────────────────────
col_ob, col_feed = st.columns([3, 2], gap="medium")

with col_ob:
    st.markdown('<div class="section-label">Order Book</div>', unsafe_allow_html=True)

    # Build side-by-side order book HTML
    bids_sorted = sorted(buy_orders,  key=lambda x: -x["price"])[:8]
    asks_sorted = sorted(sell_orders, key=lambda x:  x["price"])[:8]

    max_bid_q = max((o["quantity"] for o in bids_sorted), default=1)
    max_ask_q = max((o["quantity"] for o in asks_sorted), default=1)

    def bid_row(o):
        bar_w = int(o["quantity"] / max_bid_q * 70)
        return (
            f'<div class="ob-row">'
            f'<div class="ob-depth ob-depth-bid" style="width:{bar_w}%"></div>'
            f'<span class="ob-price-bid">{o["price"]:.2f}</span>'
            f'<span class="ob-qty">{o["quantity"]}</span>'
            f'</div>'
        )

    def ask_row(o):
        bar_w = int(o["quantity"] / max_ask_q * 70)
        return (
            f'<div class="ob-row">'
            f'<div class="ob-depth ob-depth-ask" style="width:{bar_w}%"></div>'
            f'<span class="ob-price-ask">{o["price"]:.2f}</span>'
            f'<span class="ob-qty">{o["quantity"]}</span>'
            f'</div>'
        )

    spread_html = (
        f'<div class="ob-spread-row">spread {spread:.4f} &nbsp;·&nbsp; mid {mid:.4f}</div>'
        if spread else '<div class="ob-spread-row">—</div>'
    )

    bids_html = "".join(bid_row(o) for o in bids_sorted) or '<div class="ob-row"><span style="color:#888780;font-size:12px">No bids</span></div>'
    asks_html = "".join(ask_row(o) for o in asks_sorted) or '<div class="ob-row"><span style="color:#888780;font-size:12px">No asks</span></div>'

    st.markdown(f"""
    <div class="ob-card">
      <div class="ob-header">
        <div class="ob-side-title ob-side-bid">▲ Bids &nbsp; Price / Qty</div>
        <div class="ob-side-title ob-side-ask" style="border-left:1px solid #e8e8e5;">▼ Asks &nbsp; Price / Qty</div>
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr;">
        <div>{bids_html}</div>
        <div style="border-left:1px solid #e8e8e5">{asks_html}</div>
      </div>
      {spread_html}
    </div>
    """, unsafe_allow_html=True)

with col_feed:
    st.markdown('<div class="section-label">Engine Activity</div>', unsafe_allow_html=True)

    def feed_item_html(e):
        import re, datetime
        now = datetime.datetime.now().strftime("%H:%M:%S")
        if "Trade executed" in e or "Trade:" in e:
            dot, text = "dot-trade", e.replace("Trade executed:", "<b>Trade</b>").replace("Trade:", "<b>Trade</b>")
        elif "SELL" in e or "sell" in e:
            dot, text = "dot-cancel", e
        else:
            dot, text = "dot-order", e
        return (
            f'<div class="feed-item">'
            f'<span class="feed-dot {dot}"></span>'
            f'<span class="feed-text">{text}</span>'
            f'<span class="feed-time">{now}</span>'
            f'</div>'
        )

    items_html = "".join(feed_item_html(e) for e in events[:22])
    if not items_html:
        items_html = '<div class="feed-item"><span class="feed-text" style="color:#888780">Waiting for events…</span></div>'

    st.markdown(f'<div class="feed-card">{items_html}</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# Trade Volume chart + Recent Trades
# ─────────────────────────────────────────────────────────────
col_chart, col_trades = st.columns([3, 2], gap="medium")

with col_chart:
    st.markdown('<div class="section-label">Trade Volume</div>', unsafe_allow_html=True)
    if trades:
        vol_data = [t["quantity"] for t in trades[-80:]]
        df_vol = pd.DataFrame({"Volume": vol_data})
        st.bar_chart(df_vol, height=200, use_container_width=True, color="#378ADD")
    else:
        st.caption("Waiting for trades…")

with col_trades:
    st.markdown('<div class="section-label">Recent Trades</div>', unsafe_allow_html=True)
    if trades:
        recent = list(reversed(trades[-10:]))
        rows_html = ""
        for i, t in enumerate(recent):
            size_cls = "trade-badge" if t["quantity"] <= 5 else "trade-badge trade-badge-lg"
            size_lbl = "small" if t["quantity"] <= 5 else "large"
            rows_html += (
                f'<div class="trade-row">'
                f'<span class="trade-pair">{t["quantity"]} × {t["price"]:.2f}</span>'
                f'<span class="{size_cls}">{size_lbl}</span>'
                f'</div>'
            )
        st.markdown(
            f'<div style="background:#fff;border:1px solid #e8e8e5;border-radius:10px;overflow:hidden">{rows_html}</div>',
            unsafe_allow_html=True
        )
    else:
        st.caption("No trades yet")

# ─────────────────────────────────────────────────────────────
# Auto-refresh
# ─────────────────────────────────────────────────────────────
time.sleep(1)
st.rerun()