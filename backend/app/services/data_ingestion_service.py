"""
Data ingestion service for fetching and inserting stock data.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
import requests
import json

logger = logging.getLogger(__name__)


class DataIngestionService:
    """Service for ingesting stock data into Bronze layer."""
    
    def __init__(self, databricks_service):
        self.db_service = databricks_service
    
    def get_real_stock_data(self, symbols: List[str] = None) -> List[Dict[str, Any]]:
        """Fetch real stock data from yfinance for Indian stocks."""
        if symbols is None:
            # Major Indian tech stocks
            symbols = ["INFY.NS", "TCS.NS", "WIPRO.NS", "LT.NS", "HCL.NS", 
                      "RELIANCE.NS", "HDFC.NS", "ICICIBANK.NS", "SBIN.NS", "AXISBANK.NS"]
        
        try:
            import yfinance as yf
            
            data = []
            now = datetime.utcnow()
            timestamp_ms = int(now.timestamp() * 1000)
            partition_date = now.strftime("%Y-%m-%d")
            
            for symbol in symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    # Get latest quote
                    hist = ticker.history(period="1d")
                    
                    if hist.empty:
                        logger.warning(f"No data for {symbol}")
                        continue
                    
                    latest = hist.iloc[-1]
                    price = float(latest['Close'])
                    volume = int(latest['Volume'])
                    
                    # Clean symbol (remove .NS suffix)
                    clean_symbol = symbol.replace(".NS", "").replace(".BO", "")
                    
                    data.append({
                        "symbol": clean_symbol,
                        "price": price,
                        "volume": volume,
                        "timestamp": timestamp_ms,
                        "source": "yfinance",
                        "ingestion_time": now.isoformat(),
                        "_partition_date": partition_date
                    })
                    logger.info(f"Fetched real data for {clean_symbol}: ₹{price}, Volume: {volume}")
                    
                except Exception as e:
                    logger.warning(f"Failed to fetch {symbol}: {e}")
                    continue
            
            if not data:
                logger.warning("No real data fetched, falling back to sample data")
                return self.get_sample_stock_data()
            
            logger.info(f"Successfully fetched real data for {len(data)} stocks")
            return data
            
        except ImportError:
            logger.warning("yfinance not installed, using sample data")
            return self.get_sample_stock_data()
        except Exception as e:
            logger.warning(f"Error fetching real data: {e}, falling back to sample data")
            return self.get_sample_stock_data()
    
    def get_sample_stock_data(self) -> List[Dict[str, Any]]:
        """Generate sample stock data for demonstration."""
        stocks = [
            {"symbol": "INFY", "price": 1850.50, "volume": 2500000},
            {"symbol": "TCS", "price": 3750.75, "volume": 1800000},
            {"symbol": "WIPRO", "price": 625.25, "volume": 3200000},
            {"symbol": "RELIANCE", "price": 2450.00, "volume": 2100000},
            {"symbol": "HDFC", "price": 2750.50, "volume": 1500000},
            {"symbol": "ICICIBANK", "price": 980.75, "volume": 2800000},
            {"symbol": "SBIN", "price": 550.25, "volume": 3500000},
            {"symbol": "ADANIPORT", "price": 750.00, "volume": 1200000},
        ]
        
        data = []
        now = datetime.utcnow()
        timestamp_ms = int(now.timestamp() * 1000)
        partition_date = now.strftime("%Y-%m-%d")
        
        for stock in stocks:
            data.append({
                "symbol": stock["symbol"],
                "price": stock["price"],
                "volume": stock["volume"],
                "timestamp": timestamp_ms,
                "source": "demo_data",
                "ingestion_time": now.isoformat(),
                "_partition_date": partition_date
            })
        
        return data
    
    async def ingest_bronze_data(self, use_real_data: bool = True) -> Dict[str, Any]:
        """Ingest stock data into Bronze table.
        
        Args:
            use_real_data: If True, fetch real data from yfinance. If False, use sample data.
        """
        try:
            if not self.db_service.warehouse_id:
                return {"status": "error", "message": "Warehouse not configured"}
            
            # Get data - real or sample
            if use_real_data:
                logger.info("Fetching REAL stock data from yfinance...")
                data = self.get_real_stock_data()
            else:
                logger.info("Using sample stock data...")
                data = self.get_sample_stock_data()
            
            logger.info(f"Ingesting {len(data)} records into Bronze table")
            
            # Generate INSERT statement
            insert_sql = self._generate_insert_sql(data)
            
            # Execute INSERT via REST API
            headers = {
                "Authorization": f"Bearer {self.db_service.token}",
                "Content-Type": "application/json"
            }
            
            url = f"{self.db_service.host}/api/2.0/sql/statements"
            payload = {
                "warehouse_id": self.db_service.warehouse_id,
                "statement": insert_sql,
                "wait_timeout": "30s"
            }
            
            logger.info(f"Executing INSERT into Bronze table")
            response = requests.post(url, json=payload, headers=headers, timeout=120)
            
            if response.status_code != 200:
                logger.error(f"INSERT Error: {response.text}")
                return {"status": "error", "message": response.text}
            
            response.raise_for_status()
            
            logger.info(f"Successfully ingested {len(data)} records into Bronze table")
            return {
                "status": "success",
                "layer": "bronze",
                "records_ingested": len(data),
                "data_source": "yfinance" if use_real_data else "sample",
                "message": f"Ingested {len(data)} stock records into Bronze table"
            }
            
        except Exception as e:
            logger.error(f"Bronze ingestion failed: {e}")
            return {"status": "error", "message": str(e)}
    
    def _generate_insert_sql(self, data: List[Dict[str, Any]]) -> str:
        """Generate INSERT statement from data records."""
        # Build VALUES clause
        values_list = []
        for record in data:
            # Escape symbols and values
            symbol = record["symbol"].replace("'", "''")
            source = record["source"].replace("'", "''")
            ingestion_time = record["ingestion_time"].replace("'", "''")
            partition_date = record["_partition_date"].replace("'", "''")
            
            value_tuple = (
                f"('{symbol}', {record['price']}, {record['volume']}, "
                f"{record['timestamp']}, '{source}', "
                f"'{ingestion_time}', '{partition_date}')"
            )
            values_list.append(value_tuple)
        
        values_clause = ", ".join(values_list)
        
        insert_sql = (
            f"INSERT INTO {self.db_service.catalog}.{self.db_service.schema}.bronze_stock_data "
            f"(symbol, price, volume, timestamp, source, ingestion_time, _partition_date) "
            f"VALUES {values_clause}"
        )
        
        return insert_sql
    
    async def transform_to_silver(self) -> Dict[str, Any]:
        """Transform Bronze data to Silver layer (aggregated by day)."""
        try:
            if not self.db_service.warehouse_id:
                return {"status": "error", "message": "Warehouse not configured"}
            
            # SQL to transform Bronze to Silver
            transform_sql = (
                f"INSERT INTO {self.db_service.catalog}.{self.db_service.schema}.silver_stock_data "
                f"(symbol, price, volume, date, cleaned_at, data_quality_score) "
                f"SELECT "
                f"  symbol, "
                f"  AVG(price) as price, "
                f"  SUM(volume) as volume, "
                f"  FROM_UNIXTIME(timestamp/1000, 'yyyy-MM-dd')::DATE as date, "
                f"  CURRENT_TIMESTAMP() as cleaned_at, "
                f"  0.95 as data_quality_score "
                f"FROM {self.db_service.catalog}.{self.db_service.schema}.bronze_stock_data "
                f"GROUP BY symbol, FROM_UNIXTIME(timestamp/1000, 'yyyy-MM-dd')::DATE"
            )
            
            headers = {
                "Authorization": f"Bearer {self.db_service.token}",
                "Content-Type": "application/json"
            }
            
            url = f"{self.db_service.host}/api/2.0/sql/statements"
            payload = {
                "warehouse_id": self.db_service.warehouse_id,
                "statement": transform_sql,
                "wait_timeout": "30s"
            }
            
            logger.info("Transforming data to Silver layer")
            response = requests.post(url, json=payload, headers=headers, timeout=120)
            
            if response.status_code != 200:
                logger.error(f"Silver transformation error: {response.text}")
                return {"status": "error", "message": response.text}
            
            response.raise_for_status()
            
            logger.info("Successfully transformed data to Silver layer")
            return {
                "status": "success",
                "layer": "silver",
                "message": "Transformed Bronze data to Silver layer"
            }
            
        except Exception as e:
            logger.error(f"Silver transformation failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def aggregate_to_gold(self) -> Dict[str, Any]:
        """Aggregate Silver data to Gold layer insights."""
        try:
            if not self.db_service.warehouse_id:
                return {"status": "error", "message": "Warehouse not configured"}
            
            # SQL to aggregate Silver to Gold
            aggregate_sql = (
                f"INSERT INTO {self.db_service.catalog}.{self.db_service.schema}.gold_stock_insights "
                f"(symbol, avg_price, max_price, min_price, total_volume, trend, volatility, date, generated_at) "
                f"SELECT "
                f"  symbol, "
                f"  AVG(price) as avg_price, "
                f"  MAX(price) as max_price, "
                f"  MIN(price) as min_price, "
                f"  SUM(volume) as total_volume, "
                f"  CASE WHEN MAX(price) > AVG(price) THEN 'UP' ELSE 'DOWN' END as trend, "
                f"  STDDEV_POP(price) as volatility, "
                f"  date, "
                f"  CURRENT_TIMESTAMP() as generated_at "
                f"FROM {self.db_service.catalog}.{self.db_service.schema}.silver_stock_data "
                f"GROUP BY symbol, date"
            )
            
            headers = {
                "Authorization": f"Bearer {self.db_service.token}",
                "Content-Type": "application/json"
            }
            
            url = f"{self.db_service.host}/api/2.0/sql/statements"
            payload = {
                "warehouse_id": self.db_service.warehouse_id,
                "statement": aggregate_sql,
                "wait_timeout": "30s"
            }
            
            logger.info("Aggregating data to Gold layer")
            response = requests.post(url, json=payload, headers=headers, timeout=120)
            
            if response.status_code != 200:
                logger.error(f"Gold aggregation error: {response.text}")
                return {"status": "error", "message": response.text}
            
            response.raise_for_status()
            
            logger.info("Successfully aggregated data to Gold layer")
            return {
                "status": "success",
                "layer": "gold",
                "message": "Aggregated Silver data to Gold layer insights"
            }
            
        except Exception as e:
            logger.error(f"Gold aggregation failed: {e}")
            return {"status": "error", "message": str(e)}


def get_data_ingestion_service(databricks_service) -> DataIngestionService:
    """Get or create data ingestion service instance."""
    return DataIngestionService(databricks_service)
