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

# Pipeline
## Historical Extract
The patching will be handled by the [Old Trade Lookup API](https://binance-docs.github.io/apidocs/spot/en/#old-trade-lookup-market_data).

![Figure 1: Historical Loading](img/historical.png?raw=true)
The historical pipeline is designed to run in 3 ways for a given instrument:
1. Reverse load (optional first date). Given an input instrument, the latest trade_id is found and the instrument is chunked back in time until trade_id=0 is reached or until first_date-1 is reached if specified.
2. Load from trade_id = 0
3. Load from date (optional to date)

The function is triggered with an orchestration message which specifies which of the three above options are to be selected.

For 3., some pre work is required to discover what the starting trade_id should be. It is proposed the in-memory [Recent Trade List](https://binance-docs.github.io/apidocs/spot/en/#recent-trades-list) be called to discover the last trade_id for today's date. The Old Trade Lookup API is then called once with an instrument limit of 1 to find the first date on which that instrument was traded. The data is then searched assuming uniform distribution of trades and dates until the first date is found. More on this later.

Given the environment variables RESERVED_CONCURRENCY, `x`, and CHUNK_LIMIT, `n`, the SQS is initially fed to retrieve the first API responses with `x` number of discrete messages, each with fromId as `(trade_id + nx)` (2., 3.) or `(trade_id - nx)` (1.). The SQS is then recursively fed in the same way at the end of each invocation with a single +/- `nx` until either the trade_id or date threshold has been breached.

During the invocation, the lambda loads the payload for the API as received from SQS and calls the API, dumping the response to file in S3.

## Live Extract
![Figure 2: Live Loading](img/live.png?raw=true)
The live pipeline is designed to be constantly on while trading is in progress. For the websocket connection, having the code run on an EC2 instance is preferred. To keep up with traffic on the websocket it is proposed that this EC2 instance send the received data into a streaming system in received batches limited by size and time where it can sink to a file store. Once in the file store, the rest of the data pipeline remains unchanged from the initial historical pipeline.

Depending on latency requirements for applications designed to consume the output of this pipeline, it is advisable to look at Kafka and ksqlDB for this use case instead of Kinesis. MSK was made generally available this week and is worth further investigation.

## Transformation
The transformation step is concerned with combining a number of files together in S3 and storing in columnar structured format with compression - .snappy.parquet. To function as a performant data lake, 4 partition columns are proposed: trade_year, trade_month, trade_day, instrument. In this way, a spark engine does not have to open each parquet file to read the footer to find where data exists if it matches the query, since common query paths on dates and instruments are handled by this partitioning. Based on the way the files have been generated the data are naturally separated by these partition columns already in the majority in the raw json files so it can be seen as "free partitioning".

Once the data has been stored to file for Spark based querying (Glue+Athena/PySpark notebooks) it is also loaded into a database that can be queried by other applications, especially those that do not have low latency requirements. 
