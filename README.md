# Order Matching Engine — Real-Time Market Simulator

![CI](https://github.com/anagha-chaudhari/order-matching-engine/actions/workflows/ci.yml/badge.svg)

There is no easy way to see how an exchange actually works under the hood. Order matching is at the core of every stock exchange, but it's mostly a black box. This project makes it observable - a full engine with real price-time priority matching, live market simulation and a dashboard that shows exactly what is happening as trades execute. It also tracks system under load.

---

## Stack

Python | FastAPI | Streamlit | WebSocket | Docker | GitHub Actions

---

## Features

**Core engine**
- Deterministic price-time priority matching via heap-based order book
- Supports buy/sell limit orders and partial fills
- Real-time trade execution with event stream for engine activity

**Market simulation**
- Background daemon thread generating realistic order flow via random walk pricing
- Adjustable simulation speed, pause/resume controls for inspection

**Dashboard**
- Live order book (bids/asks), executed trades view, real-time event log
- Live volume chart and market overview (last traded price, bid-ask spread, recent volume)
- Manual order placement via sidebar

**Performance metrics**
- Orders processed, trades executed, orders/sec, trades/sec
- Average matching latency (ms), match rate (%)

**Infrastructure**
- REST + WebSocket APIs — HTTP for standard queries, WebSocket for real-time push
- Containerized with Docker Compose (two-service setup)
- CI pipeline via GitHub Actions 

---

## Diagram

<img width="971" height="1319" alt="matchingengine drawio" src="https://github.com/user-attachments/assets/f08815f4-c21f-4a30-96d5-0e7a564bd82d" />

---

<img width="1907" height="895" alt="image" src="https://github.com/user-attachments/assets/e1dea116-4d87-4767-ad5a-4b45ecf19dac" />
<img width="1906" height="958" alt="image" src="https://github.com/user-attachments/assets/9749f580-4c51-4c47-b20d-da566c645c67" />
<img width="1907" height="945" alt="image" src="https://github.com/user-attachments/assets/936583dd-5014-4090-8999-39933c1c3e07" />

## Run locally

```bash
pip install -r requirements.txt

# Terminal 1
python -m uvicorn matching_engine.main:app --reload

# Terminal 2
streamlit run ui/dashboard.py
```

## Run with Docker

```bash
docker compose up --build
```

Dashboard → `http://localhost:8501`
API docs → `http://localhost:8000/docs`

---

## Tests

```bash
pytest tests/ -v
```

Covers full match, partial fill (both sides), no-match on price gap,
multi-order sweep, time priority at equal prices, invalid input and trade ID correctness.

---

