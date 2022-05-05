# Binance

## Context
We have just come up with a new trading strategy idea that runs on the exchange Binance. Our strategy aims to take advantage of an exploit in the way Binance creates the trades based on the order ids and the time of day. 

## Objective
Our aim is to test the strategy & then deploy it to production. First we need historic trade data from binance to test our strategy. Once tested we then will also need that same trade data in real-time to eventually trade on in in production. 

Your objective is to put together a high level design for a system for ingesting both historic and real-time data. 
Additionally, we ask you to develop a small program for backfilling the historic data to show us your coding skills.

## Deliverable

1. A high level design for a system to ingest the data. We are mostly looking at your thought process and the trade-offs you evaluate.
2. A basic implementation of ingesting historic trade data into the system.
3. Think about how your basic implementation in (2.) would be adapted to handle real-time data. What are the main considerations? 

It is important for us to see how you think about the data, the considerations you have given the context of the challenge and then also how you would go about thinking about each aspect of process.

## Resources
- Recent Trade List
[https://binance-docs.github.io/apidocs/spot/en/#recent-trades-list](https://binance-docs.github.io/apidocs/spot/en/#recent-trades-list)
- Old Trade Lookup API
[https://binance-docs.github.io/apidocs/spot/en/#old-trade-lookup-market_data](https://binance-docs.github.io/apidocs/spot/en/#old-trade-lookup-market_data)
- Binance Websocket Trade Stream:
[https://binance-docs.github.io/apidocs/spot/en/#trade-streams](https://binance-docs.github.io/apidocs/spot/en/#trade-streams)
