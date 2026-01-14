import streamlit as st
import requests

API_BASE = "http://127.0.0.1:8000"

st.set_page_config(page_title="Trade Engine", layout="wide")

# -------------------------------
# Header
# -------------------------------
st.title("Trade Matching Engine")
st.caption("Deterministic engine with ML-based execution advisory")

st.divider()

# -------------------------------
# Place Order
# -------------------------------
st.subheader("Place Order")

c1, c2, c3, c4 = st.columns([1, 1, 1, 1])

with c1:
    side = st.selectbox("Side", ["buy", "sell"])

with c2:
    price = st.number_input("Price", value=100.0, step=1.0)

with c3:
    quantity = st.number_input("Quantity", value=10, step=1)

with c4:
    place = st.button("Place Order", use_container_width=True)

if place:
    payload = {"side": side, "price": price, "quantity": quantity}
    try:
        res = requests.post(f"{API_BASE}/orders", json=payload)
        if res.status_code == 200:
            short_id = res.json()["id"][:8]
            st.success(f"Order placed successfully (ID: {short_id})")
        else:
            st.error(res.text)
    except:
        st.error("Backend not reachable")

st.divider()

# -------------------------------
# AI Advisory
# -------------------------------
st.subheader("Execution Advisory (ML)")

if st.button("Analyze Order"):
    payload = {"side": side, "price": price, "quantity": quantity}

    try:
        res = requests.post(f"{API_BASE}/recommend", json=payload)

        if res.status_code == 200:
            prob = float(res.json()["fill_probability"])

            st.metric("Estimated Fill Probability", f"{int(prob*100)}%")

            # Simple, interpretable advice
            if prob >= 0.7:
                st.success("Good conditions – high likelihood of quick execution.")
            elif prob >= 0.45:
                st.warning("Moderate conditions – execution may take time.")
            else:
                st.error("Low likelihood of execution – consider adjusting price.")

        else:
            st.error("AI service error")

    except:
        st.error("Could not reach backend")

st.divider()

# -------------------------------
# Orderbook
# -------------------------------
st.subheader("Order Book")

if st.button("Refresh Order Book"):
    try:
        res = requests.get(f"{API_BASE}/orderbook")
        data = res.json()

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Buy Orders**")
            if data["buy_orders"]:
                st.dataframe(data["buy_orders"], use_container_width=True)
            else:
                st.caption("No buy orders")

        with col2:
            st.markdown("**Sell Orders**")
            if data["sell_orders"]:
                st.dataframe(data["sell_orders"], use_container_width=True)
            else:
                st.caption("No sell orders")

    except:
        st.error("Failed to fetch order book")

st.divider()

# -------------------------------
# Trades
# -------------------------------
st.subheader("Executed Trades")

if st.button("Refresh Trades"):
    try:
        res = requests.get(f"{API_BASE}/trades")
        trades = res.json()

        if trades:
            # Show short IDs
            formatted = []
            for t in trades:
                formatted.append({
                    "buy_id": t["buy_order_id"][:8],
                    "sell_id": t["sell_order_id"][:8],
                    "price": t["price"],
                    "quantity": t["quantity"]
                })

            st.dataframe(formatted, use_container_width=True)
        else:
            st.caption("No trades executed yet")

    except:
        st.error("Failed to fetch trades")
