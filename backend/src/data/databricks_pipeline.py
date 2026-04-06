"""
Databricks pipeline integration for writing Bronze/Silver/Gold data layers to Delta Lake.
"""

import logging
from datetime import datetime
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)


class DatabricksPipeline:
    """Wrapper for writing data pipeline outputs to Databricks Delta Lake."""

    def __init__(
        self,
        databricks_client,
        catalog: str = "insightgenie",
        schema: str = "default",
    ):
        """Initialize Databricks pipeline wrapper.

        Args:
            databricks_client: DatabricksClient instance
            catalog: Unity Catalog name
            schema: Schema name
        """
        self.db_client = databricks_client
        self.catalog = catalog
        self.schema = schema

    def write_bronze_layer(
        self, df: pd.DataFrame, table_name: str = "bronze_stocks"
    ) -> bool:
        """Write raw data to Bronze layer in Delta Lake.

        Args:
            df: DataFrame with raw data
            table_name: Bronze table name

        Returns:
            True if successful
        """
        try:
            if df.empty:
                logger.warning("Bronze DataFrame is empty, skipping write")
                return False

            # Add metadata columns
            df["_loaded_at"] = datetime.utcnow()
            df["_data_source"] = "nse_bse"

            # Write to Delta Lake
            full_table_name = f"{self.catalog}.{self.schema}.{table_name}"

            success = self.db_client.write_dataframe_to_delta(
                df,
                full_table_name,
                mode="append",
                partition_cols=["_loaded_at"],
            )

            if success:
                row_count = len(df)
                logger.info(
                    f"Wrote {row_count} rows to Bronze layer: {full_table_name}"
                )
            return success

        except Exception as e:
            logger.error(f"Failed to write Bronze layer: {e}")
            return False

    def write_silver_layer(
        self,
        df: pd.DataFrame,
        table_name: str = "silver_stocks",
        partition_cols: Optional[list] = None,
    ) -> bool:
        """Write cleaned and normalized data to Silver layer.

        Args:
            df: DataFrame with cleaned data
            table_name: Silver table name
            partition_cols: Columns to partition by

        Returns:
            True if successful
        """
        try:
            if df.empty:
                logger.warning("Silver DataFrame is empty, skipping write")
                return False

            # Add metadata columns
            df["_transformed_at"] = datetime.utcnow()
            df["_quality_score"] = 1.0  # Default quality score

            # Default partition columns
            if partition_cols is None:
                partition_cols = ["_transformed_at"]

            # Write to Delta Lake
            full_table_name = f"{self.catalog}.{self.schema}.{table_name}"

            success = self.db_client.write_dataframe_to_delta(
                df,
                full_table_name,
                mode="append",
                partition_cols=partition_cols,
            )

            if success:
                row_count = len(df)
                logger.info(
                    f"Wrote {row_count} rows to Silver layer: {full_table_name}"
                )
            return success

        except Exception as e:
            logger.error(f"Failed to write Silver layer: {e}")
            return False

    def write_gold_layer(
        self,
        df: pd.DataFrame,
        table_name: str = "gold_stocks",
        partition_cols: Optional[list] = None,
    ) -> bool:
        """Write aggregated and analyzed data to Gold layer.

        Args:
            df: DataFrame with aggregated data
            table_name: Gold table name
            partition_cols: Columns to partition by

        Returns:
            True if successful
        """
        try:
            if df.empty:
                logger.warning("Gold DataFrame is empty, skipping write")
                return False

            # Add metadata columns
            df["_analyzed_at"] = datetime.utcnow()
            df["_analysis_version"] = "1.0"

            # Default partition columns
            if partition_cols is None:
                partition_cols = ["_analyzed_at"]

            # Write to Delta Lake
            full_table_name = f"{self.catalog}.{self.schema}.{table_name}"

            success = self.db_client.write_dataframe_to_delta(
                df,
                full_table_name,
                mode="append",
                partition_cols=partition_cols,
            )

            if success:
                row_count = len(df)
                logger.info(
                    f"Wrote {row_count} rows to Gold layer: {full_table_name}"
                )
            return success

        except Exception as e:
            logger.error(f"Failed to write Gold layer: {e}")
            return False

    def create_layer_tables(self) -> bool:
        """Create Bronze, Silver, and Gold layer tables.

        Returns:
            True if successful
        """
        try:
            # Create Bronze table schema
            bronze_schema = {
                "ticker": "string",
                "company_name": "string",
                "price": "double",
                "change": "double",
                "volume": "long",
                "timestamp": "timestamp",
                "_loaded_at": "timestamp",
                "_data_source": "string",
            }

            # Create Silver table schema
            silver_schema = {
                "ticker": "string",
                "company_name": "string",
                "price_normalized": "double",
                "change_normalized": "double",
                "volume_normalized": "long",
                "quality_indicator": "double",
                "timestamp": "timestamp",
                "_transformed_at": "timestamp",
                "_quality_score": "double",
            }

            # Create Gold table schema
            gold_schema = {
                "ticker": "string",
                "company_name": "string",
                "price_aggregated": "double",
                "volatility": "double",
                "momentum": "double",
                "trend": "string",
                "analysis_timestamp": "timestamp",
                "_analyzed_at": "timestamp",
                "_analysis_version": "string",
            }

            # Create tables with schemas
            bronze_df = pd.DataFrame({k: pd.Series([], dtype=v) for k, v in bronze_schema.items()})
            silver_df = pd.DataFrame({k: pd.Series([], dtype=v) for k, v in silver_schema.items()})
            gold_df = pd.DataFrame({k: pd.Series([], dtype=v) for k, v in gold_schema.items()})

            # Write table structures
            tables = [
                ("bronze_stocks", bronze_df),
                ("silver_stocks", silver_df),
                ("gold_stocks", gold_df),
            ]

            for table_name, df in tables:
                full_table_name = f"{self.catalog}.{self.schema}.{table_name}"
                success = self.db_client.create_or_replace_table(
                    full_table_name, df
                )
                if success:
                    logger.info(f"Created table: {full_table_name}")
                else:
                    logger.error(f"Failed to create table: {full_table_name}")
                    return False

            return True

        except Exception as e:
            logger.error(f"Failed to create layer tables: {e}")
            return False

    def get_layer_stats(self) -> dict:
        """Get statistics for all data layers.

        Returns:
            Dictionary with layer statistics
        """
        stats = {}

        try:
            for layer_name, table_name in [
                ("bronze", "bronze_stocks"),
                ("silver", "silver_stocks"),
                ("gold", "gold_stocks"),
            ]:
                full_table_name = f"{self.catalog}.{self.schema}.{table_name}"

                if self.db_client.table_exists(full_table_name):
                    table_info = self.db_client.get_table_info(
                        full_table_name
                    )
                    if table_info:
                        stats[layer_name] = {
                            "table_name": full_table_name,
                            "columns": len(table_info.get("columns", [])),
                            "exists": True,
                        }
                    else:
                        stats[layer_name] = {
                            "table_name": full_table_name,
                            "exists": False,
                        }
                else:
                    stats[layer_name] = {
                        "table_name": full_table_name,
                        "exists": False,
                    }

        except Exception as e:
            logger.error(f"Failed to get layer stats: {e}")

        return stats

    def validate_schema(self, df: pd.DataFrame, layer_type: str) -> bool:
        """Validate DataFrame schema for layer type.

        Args:
            df: DataFrame to validate
            layer_type: Type of layer (bronze, silver, gold)

        Returns:
            True if schema is valid
        """
        try:
            required_columns = {
                "bronze": ["ticker", "company_name", "price", "volume"],
                "silver": [
                    "ticker",
                    "company_name",
                    "price_normalized",
                    "volume_normalized",
                ],
                "gold": [
                    "ticker",
                    "company_name",
                    "price_aggregated",
                    "volatility",
                ],
            }

            if layer_type not in required_columns:
                logger.error(f"Unknown layer type: {layer_type}")
                return False

            missing_cols = [
                col
                for col in required_columns[layer_type]
                if col not in df.columns
            ]

            if missing_cols:
                logger.error(
                    f"Missing columns for {layer_type}: {missing_cols}"
                )
                return False

            return True

        except Exception as e:
            logger.error(f"Failed to validate schema: {e}")
            return False


# Global Databricks pipeline instance
_db_pipeline: Optional[DatabricksPipeline] = None


def get_databricks_pipeline(
    databricks_client=None,
    catalog: str = "insightgenie",
    schema: str = "default",
) -> Optional[DatabricksPipeline]:
    """Get or create Databricks pipeline instance.

    Args:
        databricks_client: DatabricksClient instance
        catalog: Unity Catalog name
        schema: Schema name

    Returns:
        DatabricksPipeline instance or None
    """
    global _db_pipeline

    if _db_pipeline is None and databricks_client:
        _db_pipeline = DatabricksPipeline(
            databricks_client, catalog, schema
        )

    return _db_pipeline
