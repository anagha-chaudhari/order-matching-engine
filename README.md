# 🧩 Order Matching Engine Simulator with Real-Time Observability Dashboard

- Built a real-time order matching engine with interactive dashboard, user controls and system performance metrics.
- Visualized order flow, trade execution and backend behaviour under simulated market load.
- Improved system observability by tracking latency, throughput and match rate in real time.

## 🔺 Features
### 1. Core Engine
- deterministic price-time priority matching engine
- supports buy/sell orders and partial fills
- real time trade execution
- event stream for engine activity

### 2. Market Simulation
- background market simulator generating realistic order flow
- adjustable simulation speed (pause/resume controls for inspection)

### 3. Dashboard
- Streamlit UI
- live order book(bids/asks)
- executed trades view
- real time event log of orders and trades
- live volume chart
- market overview indicators (last traded price, bid-ask spread, recent volume)
- manual order placement

### 4. Performance Metrics
- orders processed
- trades executed
- orders per second
- trades per second
- average matching latency (ms)
- match rate (%)

## 🔺 Tech Stack
- Python 3.10+
- FastAPI
- Streamlit
- Requests
- Heap-based data structures

## Future improvements
- dockerize
- websocket support
- basic test suite engine
- ci pipeline for automated checks
