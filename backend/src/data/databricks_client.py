"""
Databricks client for Unity Catalog integration and Delta Lake management.
"""

import logging
from typing import Any, Dict, List, Optional

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.catalog import (
    CreateCatalogRequest,
    CreateSchemaRequest,
    CreateVolumeRequest,
)
from databricks.sql import connect

logger = logging.getLogger(__name__)


class DatabricksClient:
    """Manages Databricks workspace, UC, and Delta Lake operations."""

    def __init__(
        self,
        host: str,
        token: str,
        catalog: str = "insightgenie",
        schema: str = "default",
    ):
        """Initialize Databricks client.

        Args:
            host: Databricks workspace URL
            token: Personal access token
            catalog: Unity Catalog name
            schema: Schema name within catalog
        """
        self.host = host
        self.token = token
        self.catalog = catalog
        self.schema = schema

        # Initialize Workspace Client
        self.ws_client = WorkspaceClient(host=host, token=token)

        # Initialize SQL connection
        try:
            self.sql_conn = connect(
                server_hostname=host.replace("https://", "").replace("/", ""),
                http_path="/sql/1.0/warehouses/default",
                auth_type="pat",
                personal_access_token=token,
            )
            self.cursor = self.sql_conn.cursor()
        except Exception as e:
            logger.warning(f"SQL connection failed: {e}")
            self.sql_conn = None
            self.cursor = None

    def setup_catalog_and_schema(self) -> bool:
        """Setup catalog and schema if they don't exist.

        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if catalog exists
            try:
                self.ws_client.catalogs.get(self.catalog)
                logger.info(f"Catalog '{self.catalog}' already exists")
            except Exception:
                # Create catalog
                request = CreateCatalogRequest(name=self.catalog)
                self.ws_client.catalogs.create(request)
                logger.info(f"Created catalog '{self.catalog}'")

            # Check if schema exists
            try:
                self.ws_client.schemas.get(
                    f"{self.catalog}.{self.schema}"
                )
                logger.info(
                    f"Schema '{self.schema}' already exists in '{self.catalog}'"
                )
            except Exception:
                # Create schema
                request = CreateSchemaRequest(
                    name=self.schema,
                    catalog_name=self.catalog,
                )
                self.ws_client.schemas.create(request)
                logger.info(
                    f"Created schema '{self.schema}' in '{self.catalog}'"
                )

            return True

        except Exception as e:
            logger.error(f"Failed to setup catalog/schema: {e}")
            return False

    def create_volume(
        self, volume_name: str, description: str = ""
    ) -> bool:
        """Create a Unity Catalog volume.

        Args:
            volume_name: Name of the volume
            description: Volume description

        Returns:
            True if successful
        """
        try:
            full_name = f"{self.catalog}.{self.schema}.{volume_name}"

            # Check if volume exists
            try:
                self.ws_client.volumes.read(full_name)
                logger.info(f"Volume '{full_name}' already exists")
                return True
            except Exception:
                pass

            # Create volume
            request = CreateVolumeRequest(
                catalog_name=self.catalog,
                schema_name=self.schema,
                name=volume_name,
                volume_type="EXTERNAL",
            )
            self.ws_client.volumes.create(request)
            logger.info(f"Created volume '{full_name}'")
            return True

        except Exception as e:
            logger.error(f"Failed to create volume: {e}")
            return False

    def write_dataframe_to_delta(
        self,
        df,
        table_name: str,
        mode: str = "overwrite",
        partition_cols: Optional[List[str]] = None,
    ) -> bool:
        """Write Pandas/PySpark DataFrame to Delta Lake table.

        Args:
            df: DataFrame to write
            table_name: Target table name
            mode: Write mode (overwrite, append, etc.)
            partition_cols: Columns to partition by

        Returns:
            True if successful
        """
        try:
            full_table = f"{self.catalog}.{self.schema}.{table_name}"

            # Handle Pandas DataFrame
            if hasattr(df, "to_spark"):
                spark_df = df.to_spark()
            else:
                spark_df = df

            # Write to Delta Lake
            writer = spark_df.write.mode(mode).format("delta")

            if partition_cols:
                writer = writer.partitionBy(*partition_cols)

            writer.option("mergeSchema", "true").saveAsTable(
                full_table, path=None
            )

            logger.info(
                f"Wrote data to '{full_table}' (mode: {mode})"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to write to Delta: {e}")
            return False

    def execute_sql(self, sql: str) -> Optional[List[Dict[str, Any]]]:
        """Execute SQL query against Databricks warehouse.

        Args:
            sql: SQL query string

        Returns:
            List of result rows as dicts, or None on error
        """
        if not self.cursor:
            logger.error("SQL connection not available")
            return None

        try:
            self.cursor.execute(sql)
            results = self.cursor.fetchall()

            # Convert to list of dicts
            columns = [desc[0] for desc in self.cursor.description]
            return [dict(zip(columns, row)) for row in results]

        except Exception as e:
            logger.error(f"SQL execution failed: {e}")
            return None

    def create_or_replace_table(
        self,
        table_name: str,
        df,
        columns_spec: Optional[str] = None,
    ) -> bool:
        """Create or replace Delta Lake table.

        Args:
            table_name: Table name
            df: DataFrame with data
            columns_spec: Optional column specification

        Returns:
            True if successful
        """
        return self.write_dataframe_to_delta(
            df, table_name, mode="overwrite"
        )

    def append_to_table(self, table_name: str, df) -> bool:
        """Append data to existing Delta Lake table.

        Args:
            table_name: Table name
            df: DataFrame with data

        Returns:
            True if successful
        """
        return self.write_dataframe_to_delta(
            df, table_name, mode="append"
        )

    def table_exists(self, table_name: str) -> bool:
        """Check if table exists in Unity Catalog.

        Args:
            table_name: Table name

        Returns:
            True if table exists
        """
        try:
            full_table = f"{self.catalog}.{self.schema}.{table_name}"
            self.ws_client.tables.get(full_table)
            return True
        except Exception:
            return False

    def get_table_info(self, table_name: str) -> Optional[Dict[str, Any]]:
        """Get table metadata.

        Args:
            table_name: Table name

        Returns:
            Table info dict or None
        """
        try:
            full_table = f"{self.catalog}.{self.schema}.{table_name}"
            table = self.ws_client.tables.get(full_table)
            return {
                "name": table.name,
                "schema_name": table.schema_name,
                "catalog_name": table.catalog_name,
                "table_type": table.table_type,
                "columns": len(table.columns) if table.columns else 0,
            }
        except Exception as e:
            logger.error(f"Failed to get table info: {e}")
            return None

    def list_tables(self) -> Optional[List[str]]:
        """List all tables in schema.

        Returns:
            List of table names or None
        """
        try:
            full_schema = f"{self.catalog}.{self.schema}"
            tables = self.ws_client.tables.list(
                catalog_name=self.catalog,
                schema_name=self.schema,
            )
            return [t.name for t in tables]
        except Exception as e:
            logger.error(f"Failed to list tables: {e}")
            return None

    def delete_table(self, table_name: str, purge: bool = False) -> bool:
        """Delete table from Unity Catalog.

        Args:
            table_name: Table name
            purge: Whether to purge underlying data

        Returns:
            True if successful
        """
        try:
            full_table = f"{self.catalog}.{self.schema}.{table_name}"
            self.ws_client.tables.delete(full_table)
            logger.info(f"Deleted table '{full_table}'")
            return True
        except Exception as e:
            logger.error(f"Failed to delete table: {e}")
            return False

    def get_catalog_info(self) -> Optional[Dict[str, Any]]:
        """Get catalog information.

        Returns:
            Catalog info dict or None
        """
        try:
            catalog = self.ws_client.catalogs.get(self.catalog)
            return {
                "name": catalog.name,
                "owner": catalog.owner,
                "created_at": catalog.created_at,
            }
        except Exception as e:
            logger.error(f"Failed to get catalog info: {e}")
            return None

    def close(self) -> None:
        """Close connections."""
        if self.cursor:
            self.cursor.close()
        if self.sql_conn:
            self.sql_conn.close()
        logger.info("Databricks connections closed")


# Global client instance
_databricks_client: Optional[DatabricksClient] = None


def get_databricks_client(
    host: str = None,
    token: str = None,
    catalog: str = "insightgenie",
    schema: str = "default",
) -> DatabricksClient:
    """Get or create Databricks client instance.

    Args:
        host: Databricks host URL
        token: Personal access token
        catalog: Catalog name
        schema: Schema name

    Returns:
        DatabricksClient instance
    """
    global _databricks_client

    if _databricks_client is None and host and token:
        _databricks_client = DatabricksClient(
            host=host,
            token=token,
            catalog=catalog,
            schema=schema,
        )

    return _databricks_client


def close_databricks_client() -> None:
    """Close global Databricks client."""
    global _databricks_client

    if _databricks_client:
        _databricks_client.close()
        _databricks_client = None
