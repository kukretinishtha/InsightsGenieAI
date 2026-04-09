"""
Databricks integration service for Unity Catalog and Delta Lake operations.
"""

import logging
from typing import Optional, Dict, List, Any

from app.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()


class DatabricksService:
    """Service for managing Databricks operations."""
    
    def __init__(self):
        """Initialize Databricks service."""
        self.enabled = settings.ENABLE_DATABRICKS
        self.host = settings.DATABRICKS_HOST
        self.token = settings.DATABRICKS_TOKEN
        self.catalog = settings.DATABRICKS_CATALOG
        self.schema = settings.DATABRICKS_SCHEMA
        self.warehouse_id = settings.DATABRICKS_WAREHOUSE_ID
        self.client = None
        
        if self.enabled and self.token and self.host:
            self._initialize_client()
        else:
            logger.warning("Databricks integration disabled or credentials missing")
    
    def _initialize_client(self):
        """Initialize Databricks client."""
        try:
            from databricks.sdk import WorkspaceClient
            
            self.client = WorkspaceClient(
                host=self.host,
                token=self.token
            )
            logger.info(f"Databricks client initialized for {self.host}")
            
            # Try to get or create a warehouse
            if not self.warehouse_id:
                self._setup_warehouse()
        except Exception as e:
            logger.error(f"Failed to initialize Databricks client: {e}")
            self.client = None
    
    def _setup_warehouse(self):
        """Get or create a default warehouse."""
        try:
            # Try to list SQL warehouses (without purpose filter)
            warehouses_iter = self.client.warehouses.list()
            if warehouses_iter:
                # Get first SQL warehouse
                for warehouse in warehouses_iter:
                    if hasattr(warehouse, 'id') and warehouse.id:
                        self.warehouse_id = warehouse.id
                        logger.info(f"Using warehouse: {self.warehouse_id}")
                        return
            
            logger.warning("No SQL warehouses found. Please create one in Databricks UI or set DATABRICKS_WAREHOUSE_ID.")
        except AttributeError as e:
            logger.warning(f"Warehouses API not available: {e}. You must set DATABRICKS_WAREHOUSE_ID manually.")
        except Exception as e:
            logger.warning(f"Could not auto-detect warehouses: {e}. You must set DATABRICKS_WAREHOUSE_ID manually.")
    
    async def create_catalog(self) -> Dict[str, Any]:
        """Create Unity Catalog using SQL."""
        if not self.client:
            return {"status": "disabled", "message": "Databricks not configured"}
        
        if not self.warehouse_id:
            return {"status": "error", "message": "No Databricks SQL warehouse available. Create one in Databricks UI."}
        
        try:
            import time
            
            # Create SQL statement
            sql_command = f"CREATE CATALOG IF NOT EXISTS {self.catalog}"
            
            logger.info(f"Creating catalog: {sql_command}")
            
            # Use REST API to execute statement
            import requests
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            url = f"{self.host}/api/2.0/sql/statements"
            payload = {
                "warehouse_id": self.warehouse_id,
                "statement": sql_command,
                "wait_timeout": "30s"
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            
            logger.info(f"Created catalog: {self.catalog}")
            return {"status": "created", "catalog": self.catalog}
            
        except Exception as e:
            logger.error(f"Failed to create catalog: {e}")
            return {"status": "error", "message": str(e)}
    
    async def create_schema(self) -> Dict[str, Any]:
        """Create schema using SQL."""
        if not self.client:
            return {"status": "disabled", "message": "Databricks not configured"}
        
        if not self.warehouse_id:
            return {"status": "error", "message": "No Databricks SQL warehouse available. Create one in Databricks UI."}
        
        try:
            import requests
            
            # Create SQL statement
            sql_command = f"CREATE SCHEMA IF NOT EXISTS {self.catalog}.{self.schema}"
            
            logger.info(f"Creating schema: {sql_command}")
            
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            url = f"{self.host}/api/2.0/sql/statements"
            payload = {
                "warehouse_id": self.warehouse_id,
                "statement": sql_command,
                "wait_timeout": "30s"
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            
            logger.info(f"Created schema: {self.catalog}.{self.schema}")
            return {"status": "created", "schema": self.schema}
            
        except Exception as e:
            logger.error(f"Failed to create schema: {e}")
            return {"status": "error", "message": str(e)}
    
    async def get_tables(self) -> Dict[str, Any]:
        """Get list of tables in the schema using SQL."""
        if not self.client:
            return {"status": "disabled", "tables": []}
        
        if not self.warehouse_id:
            return {"status": "error", "message": "No Databricks SQL warehouse available", "tables": []}
        
        try:
            import requests
            
            sql_query = f"SHOW TABLES IN {self.catalog}.{self.schema}"
            
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            url = f"{self.host}/api/2.0/sql/statements"
            payload = {
                "warehouse_id": self.warehouse_id,
                "statement": sql_query,
                "wait_timeout": "30s"
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            result = response.json()
            
            tables = []
            if result and "result" in result and "rows" in result.get("result", {}):
                for row in result["result"]["rows"]:
                    tables.append({
                        "name": row[0] if row else "unknown",
                        "type": row[1] if len(row) > 1 else "TABLE"
                    })
            
            return {
                "status": "success",
                "catalog": self.catalog,
                "schema": self.schema,
                "tables": tables
            }
        except Exception as e:
            logger.error(f"Failed to get tables: {e}")
            return {"status": "error", "message": str(e), "tables": []}
    
    async def create_bronze_table(self, table_name: str = "bronze_stock_data") -> Dict[str, Any]:
        """Create bronze layer table for raw stock data."""
        if not self.client:
            return {"status": "disabled"}
        
        if not self.warehouse_id:
            return {"status": "error", "message": "No Databricks SQL warehouse available"}
        
        try:
            import requests
            
            # Simplified SQL
            create_table_sql = (
                f"CREATE TABLE IF NOT EXISTS {self.catalog}.{self.schema}.{table_name} "
                f"(symbol STRING, price DOUBLE, volume LONG, timestamp LONG, source STRING, "
                f"ingestion_time TIMESTAMP, _partition_date DATE) "
                f"USING DELTA PARTITIONED BY (_partition_date)"
            )
            
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            url = f"{self.host}/api/2.0/sql/statements"
            payload = {
                "warehouse_id": self.warehouse_id,
                "statement": create_table_sql,
                "wait_timeout": "30s"
            }
            
            logger.info(f"Creating bronze table with URL: {url}")
            logger.info(f"Payload: {payload}")
            
            response = requests.post(url, json=payload, headers=headers, timeout=120)
            
            if response.status_code != 200:
                error_detail = response.text
                logger.error(f"API Error Response: {error_detail}")
            
            response.raise_for_status()
            
            logger.info(f"Created bronze table: {self.catalog}.{self.schema}.{table_name}")
            return {
                "status": "created",
                "table": f"{self.catalog}.{self.schema}.{table_name}",
                "layer": "bronze"
            }
        except Exception as e:
            logger.error(f"Failed to create bronze table: {e}")
            return {"status": "error", "message": str(e)}
    
    async def create_silver_table(self, table_name: str = "silver_stock_data") -> Dict[str, Any]:
        """Create silver layer table for cleaned stock data."""
        if not self.client:
            return {"status": "disabled"}
        
        if not self.warehouse_id:
            return {"status": "error", "message": "No Databricks SQL warehouse available"}
        
        try:
            import requests
            
            # Single-line SQL to avoid formatting issues
            create_table_sql = (
                f"CREATE TABLE IF NOT EXISTS {self.catalog}.{self.schema}.{table_name} "
                f"(symbol STRING, price DOUBLE, volume LONG, date DATE, cleaned_at TIMESTAMP, "
                f"data_quality_score DOUBLE) "
                f"USING DELTA PARTITIONED BY (date)"
            )
            
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            url = f"{self.host}/api/2.0/sql/statements"
            payload = {
                "warehouse_id": self.warehouse_id,
                "statement": create_table_sql,
                "wait_timeout": "30s"
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=120)
            response.raise_for_status()
            
            logger.info(f"Created silver table: {self.catalog}.{self.schema}.{table_name}")
            return {
                "status": "created",
                "table": f"{self.catalog}.{self.schema}.{table_name}",
                "layer": "silver"
            }
        except Exception as e:
            logger.error(f"Failed to create silver table: {e}")
            return {"status": "error", "message": str(e)}
    
    async def create_gold_table(self, table_name: str = "gold_stock_insights") -> Dict[str, Any]:
        """Create gold layer table for aggregated insights."""
        if not self.client:
            return {"status": "disabled"}
        
        if not self.warehouse_id:
            return {"status": "error", "message": "No Databricks SQL warehouse available"}
        
        try:
            import requests
            
            # Single-line SQL to avoid formatting issues
            create_table_sql = (
                f"CREATE TABLE IF NOT EXISTS {self.catalog}.{self.schema}.{table_name} "
                f"(symbol STRING, avg_price DOUBLE, max_price DOUBLE, min_price DOUBLE, "
                f"total_volume LONG, trend STRING, volatility DOUBLE, date DATE, "
                f"generated_at TIMESTAMP) "
                f"USING DELTA PARTITIONED BY (date)"
            )
            
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            url = f"{self.host}/api/2.0/sql/statements"
            payload = {
                "warehouse_id": self.warehouse_id,
                "statement": create_table_sql,
                "wait_timeout": "30s"
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=120)
            response.raise_for_status()
            
            logger.info(f"Created gold table: {self.catalog}.{self.schema}.{table_name}")
            return {
                "status": "created",
                "table": f"{self.catalog}.{self.schema}.{table_name}",
                "layer": "gold"
            }
        except Exception as e:
            logger.error(f"Failed to create gold table: {e}")
            return {"status": "error", "message": str(e)}
    
    
    async def get_status(self) -> Dict[str, Any]:
        """Get Databricks connection status."""
        if not self.enabled:
            return {
                "connected": False,
                "enabled": False,
                "message": "Databricks integration is disabled"
            }
        
        if not self.client:
            return {
                "connected": False,
                "enabled": True,
                "message": "Failed to initialize Databricks client"
            }
        
        if not self.warehouse_id:
            return {
                "connected": False,
                "enabled": True,
                "message": "No SQL warehouse available. Create one in Databricks UI.",
                "warehouse_required": True
            }
        
        try:
            import requests
            
            # Try a simple SQL query to verify connection
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            url = f"{self.host}/api/2.0/sql/statements"
            payload = {
                "warehouse_id": self.warehouse_id,
                "statement": "SELECT 1 as test",
                "wait_timeout": "10s"
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            return {
                "connected": True,
                "enabled": True,
                "host": self.host,
                "catalog": self.catalog,
                "schema": self.schema,
                "warehouse_id": self.warehouse_id,
                "message": "Connected successfully"
            }
        except Exception as e:
            return {
                "connected": False,
                "enabled": True,
                "warehouse_id": self.warehouse_id,
                "message": f"Connection failed: {str(e)}"
            }


# Global instance
_databricks_service: Optional[DatabricksService] = None


def get_databricks_service() -> DatabricksService:
    """Get or create Databricks service instance."""
    global _databricks_service
    if _databricks_service is None:
        _databricks_service = DatabricksService()
    return _databricks_service
