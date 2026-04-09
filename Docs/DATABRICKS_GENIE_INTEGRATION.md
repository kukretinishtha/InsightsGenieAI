# Databricks & Genie Integration Guide

## Overview

This guide explains how to set up and use the Databricks and Genie integration in InsightGenie AI for production data storage and automated analytics dashboards.

## Architecture

### Data Flow

```
NSE/BSE Data
    ↓
Data Pipeline (Bronze → Silver → Gold)
    ↓
Databricks Delta Lake (UC)
    ↓
Genie Spaces (Auto-Dashboards)
    ↓
Streamlit Frontend
```

### Components

1. **Databricks Client** (`databricks_client.py`)
   - Manages Unity Catalog connections
   - Handles Delta Lake table operations
   - Provides SQL query interface

2. **Databricks Pipeline** (`databricks_pipeline.py`)
   - Writes Bronze/Silver/Gold layers to Delta Lake
   - Manages schema and partitioning
   - Handles data validation

3. **Genie Space Manager** (`genie/__init__.py`)
   - Creates Genie spaces programmatically
   - Generates auto-dashboards
   - Manages insight queries

## Setup Instructions

### 1. Databricks Workspace Configuration

#### Prerequisites
- Active Databricks workspace
- Unity Catalog enabled
- Personal Access Token (PAT) generated

#### Steps

1. **Get Workspace URL**
   ```bash
   # From Databricks workspace
   https://<region>.cloud.databricks.com
   # Example: https://adb-1234567890.cloud.databricks.com
   ```

2. **Generate Personal Access Token**
   - Click Settings → User Settings
   - Click Access Tokens
   - Click Generate New Token
   - Copy token (only shown once)

3. **Enable Unity Catalog**
   - Admin settings → Workspace settings
   - Enable Unity Catalog if not already enabled
   - Note the default catalog name

### 2. Environment Configuration

Create or update `.env` file:

```env
# Databricks Configuration
DATABRICKS_HOST=https://adb-1234567890.cloud.databricks.com
DATABRICKS_TOKEN=your_personal_access_token_here
DATABRICKS_CATALOG=insightgenie
DATABRICKS_SCHEMA=default
DATABRICKS_WAREHOUSE_ID=your_warehouse_id
DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/your_warehouse_id
ENABLE_DATABRICKS=true

# Genie Configuration
GENIE_SPACE_NAME=insightgenie-analytics
GENIE_AUTO_INSIGHTS=true
GENIE_ENABLE_DASHBOARDS=true
GENIE_DASHBOARD_REFRESH_INTERVAL=300
```

### 3. Dependencies Installation

```bash
# Install Databricks SDK
pip install databricks-sdk databricks-sql-connector

# Or update requirements.txt
pip install -r requirements.txt
```

Update `requirements.txt`:

```
databricks-sdk>=0.20.0
databricks-sql-connector>=3.0.0
pandas>=1.5.0
sqlalchemy>=2.0.0
```

## Usage Examples

### Initialize Databricks Client

```python
from src.data.databricks_client import get_databricks_client
from src.config import settings

# Get client instance
db_client = get_databricks_client(
    host=settings.databricks_host,
    token=settings.databricks_token,
    catalog=settings.databricks_catalog,
    schema=settings.databricks_schema,
)

# Setup catalog and schema
if db_client.setup_catalog_and_schema():
    print("Catalog and schema created successfully")
```

### Write Data to Delta Lake

```python
from src.data.databricks_pipeline import get_databricks_pipeline
import pandas as pd

# Initialize pipeline
db_pipeline = get_databricks_pipeline(
    db_client,
    catalog=settings.databricks_catalog,
    schema=settings.databricks_schema,
)

# Create sample data
df = pd.DataFrame({
    'ticker': ['INFY', 'TCS', 'WIPRO'],
    'price': [1234.5, 3456.7, 567.8],
    'volume': [1000000, 2000000, 500000],
})

# Write to Bronze layer
db_pipeline.write_bronze_layer(df, table_name='bronze_stocks')

# Write to Silver layer (cleaned)
df_silver = df.copy()
df_silver['price_normalized'] = (df_silver['price'] - df_silver['price'].mean()) / df_silver['price'].std()
db_pipeline.write_silver_layer(df_silver, table_name='silver_stocks')

# Write to Gold layer (aggregated)
df_gold = df.groupby('ticker').agg({
    'price': 'mean',
    'volume': 'sum'
}).reset_index()
df_gold.columns = ['ticker', 'price_aggregated', 'volume']
db_pipeline.write_gold_layer(df_gold, table_name='gold_stocks')
```

### Create Genie Spaces

```python
from src.genie import get_genie_manager
from src.config import settings

# Initialize Genie manager
genie_manager = get_genie_manager(db_client)

# Create space
genie_manager.create_genie_space(
    space_name=settings.genie_space_name,
    description="Stock market analysis and insights",
    source_table=f"{settings.databricks_catalog}.{settings.databricks_schema}.gold_stocks"
)

# Create auto-dashboard
genie_manager.create_auto_dashboard(
    space_name=settings.genie_space_name,
    table_name=f"{settings.databricks_catalog}.{settings.databricks_schema}.gold_stocks",
    dashboard_name="Stock Analysis Dashboard"
)

# Add insight queries
genie_manager.add_insight_query(
    space_name=settings.genie_space_name,
    query_name="Top Performers",
    query=f"SELECT * FROM {settings.databricks_catalog}.{settings.databricks_schema}.gold_stocks ORDER BY price_aggregated DESC LIMIT 10",
    description="Top 10 performing stocks"
)

# Create comprehensive analysis
genie_manager.create_analysis_dashboard(
    space_name=settings.genie_space_name,
    analysis_type="comprehensive"  # quick, comprehensive, or deep
)
```

### Query Data from Delta Lake

```python
# Execute SQL query
results = db_client.execute_sql(
    f"SELECT ticker, price_aggregated FROM {settings.databricks_catalog}.{settings.databricks_schema}.gold_stocks LIMIT 10"
)

# Check table existence
exists = db_client.table_exists(f"{settings.databricks_catalog}.{settings.databricks_schema}.bronze_stocks")

# Get table metadata
info = db_client.get_table_info(f"{settings.databricks_catalog}.{settings.databricks_schema}.silver_stocks")

# List all tables
tables = db_client.list_tables()
```

## Data Layer Details

### Bronze Layer

**Purpose**: Raw data storage  
**Characteristics**:
- Unmodified data from source
- Includes metadata columns (`_loaded_at`, `_data_source`)
- Partitioned by load date
- Example tables: `bronze_stocks`, `bronze_news`

**Schema**:
```sql
CREATE TABLE bronze_stocks (
    ticker STRING,
    company_name STRING,
    price DOUBLE,
    change DOUBLE,
    volume LONG,
    timestamp TIMESTAMP,
    _loaded_at TIMESTAMP,
    _data_source STRING
)
PARTITIONED BY (_loaded_at)
```

### Silver Layer

**Purpose**: Cleaned and normalized data  
**Characteristics**:
- Data quality validation applied
- Normalized values
- Includes quality scores (`_quality_score`)
- Transformation metadata (`_transformed_at`)
- Partitioned by transformation date

**Schema**:
```sql
CREATE TABLE silver_stocks (
    ticker STRING,
    company_name STRING,
    price_normalized DOUBLE,
    change_normalized DOUBLE,
    volume_normalized LONG,
    quality_indicator DOUBLE,
    timestamp TIMESTAMP,
    _transformed_at TIMESTAMP,
    _quality_score DOUBLE
)
PARTITIONED BY (_transformed_at)
```

### Gold Layer

**Purpose**: Aggregated and analyzed data  
**Characteristics**:
- Business-level aggregations
- Technical indicators calculated
- Analysis metadata (`_analysis_version`)
- Ready for reporting and visualization
- Partitioned by analysis date

**Schema**:
```sql
CREATE TABLE gold_stocks (
    ticker STRING,
    company_name STRING,
    price_aggregated DOUBLE,
    volatility DOUBLE,
    momentum DOUBLE,
    trend STRING,
    analysis_timestamp TIMESTAMP,
    _analyzed_at TIMESTAMP,
    _analysis_version STRING
)
PARTITIONED BY (_analyzed_at)
```

## Genie Space Management

### Create Space

```python
genie_manager.create_genie_space(
    space_name="stock-analysis",
    description="Real-time stock market analysis",
    source_table="insightgenie.default.gold_stocks"
)
```

### Create Dashboard

```python
# Auto-generated from table schema
genie_manager.create_auto_dashboard(
    space_name="stock-analysis",
    table_name="insightgenie.default.gold_stocks",
    dashboard_name="Market Overview"
)
```

### Add Custom Queries

```python
# Stock performance query
genie_manager.add_insight_query(
    space_name="stock-analysis",
    query_name="Stock Performance",
    query="SELECT ticker, price_aggregated, momentum FROM insightgenie.default.gold_stocks",
    description="Current stock performance metrics"
)

# Volatility analysis
genie_manager.add_insight_query(
    space_name="stock-analysis",
    query_name="Volatility Analysis",
    query="SELECT ticker, volatility FROM insightgenie.default.gold_stocks WHERE volatility > 0.2",
    description="High volatility stocks"
)

# Trend analysis
genie_manager.add_insight_query(
    space_name="stock-analysis",
    query_name="Trend Analysis",
    query="SELECT ticker, trend, price_aggregated FROM insightgenie.default.gold_stocks WHERE trend = 'UPTREND'",
    description="Stocks in uptrend"
)
```

### Analysis Dashboards

```python
# Quick analysis (3 queries)
genie_manager.create_analysis_dashboard(
    space_name="stock-analysis",
    analysis_type="quick"
)

# Comprehensive analysis (6 queries)
genie_manager.create_analysis_dashboard(
    space_name="stock-analysis",
    analysis_type="comprehensive"
)

# Deep analysis (9 queries)
genie_manager.create_analysis_dashboard(
    space_name="stock-analysis",
    analysis_type="deep"
)
```

### Get Space Information

```python
# Get space summary
summary = genie_manager.get_space_summary("stock-analysis")
print(f"Dashboards: {summary['dashboards']}")
print(f"Queries: {summary['queries']}")

# List all spaces
spaces = genie_manager.list_spaces()

# Export space config
config = genie_manager.export_space_config("stock-analysis")

# Delete space
genie_manager.delete_space("stock-analysis")
```

## Integration with Data Pipeline

### Automatic Writing to Databricks

The data pipeline is automatically integrated with Databricks through the FastAPI lifespan events:

1. **On Startup**
   - Databricks client initialized
   - Catalog and schema created
   - Delta Lake tables created
   - Genie space created

2. **During Operation**
   - Pipeline Bronze/Silver/Gold outputs written to Delta Lake
   - Data automatically partitioned
   - Metadata tracked

3. **On Shutdown**
   - Databricks connections closed gracefully

### Configuration in main.py

```python
# Lifespan startup:
if settings.enable_databricks:
    db_client = get_databricks_client(...)
    db_pipeline = get_databricks_pipeline(db_client)
    genie_manager = get_genie_manager(db_client)
    db_pipeline.create_layer_tables()
    genie_manager.create_genie_space(...)
```

## Best Practices

### 1. Data Quality
- Always validate data before writing
- Use `write_*_layer()` methods for schema consistency
- Monitor partition sizes
- Implement data quality checks

### 2. Performance
- Partition tables by date columns
- Use appropriate data types
- Implement clustering for frequently queried columns
- Monitor query performance in Databricks SQL

### 3. Security
- Never commit credentials to version control
- Use environment variables for sensitive data
- Implement workspace-level access controls
- Use UC roles and permissions

### 4. Monitoring
- Enable audit logging in Databricks
- Monitor query execution times
- Track data freshness
- Set up alerts for failures

### 5. Maintenance
- Archive old data to external locations
- Optimize Delta tables regularly
- Monitor catalog growth
- Update statistics for accurate query planning

## Troubleshooting

### Connection Errors

**Problem**: `Authentication failed`  
**Solution**:
- Verify DATABRICKS_TOKEN is valid
- Check token hasn't expired
- Regenerate token if needed

**Problem**: `Host not found`  
**Solution**:
- Verify DATABRICKS_HOST format
- Check workspace URL is correct
- Ensure network connectivity

### Table Operation Errors

**Problem**: `Table not found`  
**Solution**:
- Check catalog and schema exist
- Verify table name spelling
- Ensure proper UC permissions

**Problem**: `Permission denied`  
**Solution**:
- Check UC role permissions
- Verify user has table write permissions
- Request access from workspace admin

### Data Writing Errors

**Problem**: `Schema mismatch`  
**Solution**:
- Use schema validation before writing
- Call `validate_schema()` method
- Check DataFrame column types

**Problem**: `Out of memory`  
**Solution**:
- Write data in batches
- Reduce batch size
- Use `mode='append'` instead of `mode='overwrite'`

## Monitoring and Analytics

### Query Performance

Monitor query execution:

```python
# Get execution stats
results = db_client.execute_sql(
    f"SELECT COUNT(*) as record_count FROM {catalog}.{schema}.gold_stocks"
)

# Get table size
info = db_client.get_table_info(f"{catalog}.{schema}.gold_stocks")
```

### Data Freshness

Track data updates:

```python
# Check latest update time
latest = db_client.execute_sql(
    f"SELECT MAX(_analyzed_at) as latest_update FROM {catalog}.{schema}.gold_stocks"
)

# Count records by date
daily_counts = db_client.execute_sql(
    f"SELECT DATE(_analyzed_at), COUNT(*) FROM {catalog}.{schema}.gold_stocks GROUP BY DATE(_analyzed_at)"
)
```

### Space Analytics

Monitor Genie space usage:

```python
# Get space summary
summary = genie_manager.get_space_summary("stock-analysis")

# List all dashboards
dashboards = [d['name'] for d in summary['dashboards_list']]

# List all queries
queries = [q['name'] for q in summary['queries_list']]
```

## API Endpoints

### Databricks Operations

These operations are exposed through the FastAPI backend:

- `GET /health` - Check service health (includes Databricks status)
- `GET /api/data/{layer}/{symbol}` - Get data from specific layer
- `POST /api/analyze` - Run analysis and write to Databricks
- `GET /api/analyze/{request_id}` - Get analysis results

### Genie Integration

Genie dashboards are accessible through:

1. Databricks workspace → Genie section
2. Direct URL: `https://<workspace>/genie/spaces/<space_id>`
3. Embedded in Streamlit frontend (optional)

## Advanced Configuration

### Custom Warehouse

Use specific warehouse for queries:

```python
db_client = get_databricks_client(
    host=settings.databricks_host,
    token=settings.databricks_token,
    catalog=settings.databricks_catalog,
    schema=settings.databricks_schema,
)

# Warehouse is specified in HTTP path
```

### Table Properties

Set custom properties:

```python
# Tables created with default properties
# Can be customized in Databricks SQL

CREATE TABLE gold_stocks (...)
TBLPROPERTIES (
    'owner' = 'analytics_team',
    'domain' = 'finance',
    'criticality' = 'high',
    'retention_days' = '365'
)
```

### Genie Schedules

Configure automatic updates:

1. Create Genie queries
2. Set refresh schedules in Databricks UI
3. Monitor execution in Genie dashboard

## Support and Resources

- **Databricks Documentation**: https://docs.databricks.com
- **Genie Documentation**: https://docs.databricks.com/genie
- **Unity Catalog**: https://docs.databricks.com/data-governance
- **Delta Lake**: https://delta.io

## Next Steps

1. Set up Databricks workspace and UC
2. Generate personal access token
3. Configure environment variables
4. Run backend with `ENABLE_DATABRICKS=true`
5. Monitor data in Databricks
6. Create custom Genie queries
7. Share dashboards with team
