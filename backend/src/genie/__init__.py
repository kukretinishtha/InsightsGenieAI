"""
Genie space manager for programmatic dashboard creation and management.
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class GenieSpaceManager:
    """Manages Genie spaces for automated dashboard creation."""

    def __init__(self, databricks_client):
        """Initialize Genie space manager.

        Args:
            databricks_client: DatabricksClient instance
        """
        self.db_client = databricks_client
        self.spaces: Dict[str, Dict[str, Any]] = {}

    def create_genie_space(
        self,
        space_name: str,
        description: str = "",
        source_table: str = None,
    ) -> bool:
        """Create a new Genie space.

        Args:
            space_name: Name of the Genie space
            description: Space description
            source_table: Source table for analysis

        Returns:
            True if successful
        """
        try:
            # Create space metadata
            space_config = {
                "name": space_name,
                "description": description,
                "source_table": source_table,
                "dashboards": [],
                "queries": [],
                "insights": [],
            }

            # Store in local registry
            self.spaces[space_name] = space_config

            logger.info(f"Created Genie space '{space_name}'")
            return True

        except Exception as e:
            logger.error(f"Failed to create Genie space: {e}")
            return False

    def create_auto_dashboard(
        self,
        space_name: str,
        table_name: str,
        dashboard_name: str = None,
    ) -> bool:
        """Create automatic dashboard from table data.

        Args:
            space_name: Genie space name
            table_name: Source table name
            dashboard_name: Dashboard name (auto-generated if not provided)

        Returns:
            True if successful
        """
        try:
            if space_name not in self.spaces:
                logger.error(f"Space '{space_name}' not found")
                return False

            dashboard_name = (
                dashboard_name or f"{table_name}_dashboard"
            )

            # Create dashboard config
            dashboard_config = {
                "name": dashboard_name,
                "table": table_name,
                "widgets": self._generate_widgets(table_name),
                "type": "auto_generated",
            }

            # Add to space
            self.spaces[space_name]["dashboards"].append(
                dashboard_config
            )

            logger.info(
                f"Created dashboard '{dashboard_name}' in space '{space_name}'"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to create auto dashboard: {e}")
            return False

    def _generate_widgets(self, table_name: str) -> List[Dict[str, Any]]:
        """Generate dashboard widgets based on table schema.

        Args:
            table_name: Table name

        Returns:
            List of widget configurations
        """
        widgets = []

        try:
            # Get table info
            table_info = self.db_client.get_table_info(table_name)

            if not table_info:
                return widgets

            # Generate standard widgets
            widgets.extend([
                {
                    "type": "metric",
                    "title": f"{table_name} Row Count",
                    "query": f"SELECT COUNT(*) as count FROM {table_name}",
                },
                {
                    "type": "bar_chart",
                    "title": f"{table_name} Distribution",
                    "query": f"SELECT * FROM {table_name} LIMIT 1000",
                },
                {
                    "type": "table",
                    "title": f"{table_name} Data Preview",
                    "query": f"SELECT * FROM {table_name} LIMIT 100",
                },
            ])

        except Exception as e:
            logger.error(f"Failed to generate widgets: {e}")

        return widgets

    def add_insight_query(
        self,
        space_name: str,
        query_name: str,
        query: str,
        description: str = "",
    ) -> bool:
        """Add insight query to Genie space.

        Args:
            space_name: Genie space name
            query_name: Query name
            query: SQL query
            description: Query description

        Returns:
            True if successful
        """
        try:
            if space_name not in self.spaces:
                logger.error(f"Space '{space_name}' not found")
                return False

            # Execute query to validate
            results = self.db_client.execute_sql(query)

            if results is None:
                logger.warning(f"Query validation failed for '{query_name}'")
                return False

            # Add to space
            query_config = {
                "name": query_name,
                "description": description,
                "query": query,
                "result_count": len(results) if results else 0,
            }

            self.spaces[space_name]["queries"].append(query_config)

            logger.info(
                f"Added query '{query_name}' to space '{space_name}'"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to add insight query: {e}")
            return False

    def create_analysis_dashboard(
        self, space_name: str, analysis_type: str = "comprehensive"
    ) -> bool:
        """Create comprehensive analysis dashboard.

        Args:
            space_name: Genie space name
            analysis_type: Type of analysis (quick, comprehensive, deep)

        Returns:
            True if successful
        """
        try:
            if space_name not in self.spaces:
                logger.error(f"Space '{space_name}' not found")
                return False

            # Define analysis queries based on type
            if analysis_type == "quick":
                queries = {
                    "overview": "SELECT COUNT(*) as total_records",
                    "summary": "SELECT * LIMIT 10",
                }
            elif analysis_type == "comprehensive":
                queries = {
                    "overview": "SELECT COUNT(*) as total_records",
                    "summary": "SELECT * LIMIT 100",
                    "stats": "SELECT COUNT(*), AVG(*), MAX(*), MIN(*) FROM {table}",
                    "trends": "SELECT * FROM {table} ORDER BY timestamp DESC LIMIT 1000",
                }
            else:  # deep
                queries = {
                    "overview": "SELECT COUNT(*) as total_records",
                    "summary": "SELECT * LIMIT 100",
                    "stats": "SELECT * FROM {table}",
                    "trends": "SELECT * FROM {table} ORDER BY timestamp DESC",
                    "anomalies": "SELECT * FROM {table} WHERE anomaly_score > 0.8",
                    "correlations": "SELECT * FROM {table} WHERE correlation > 0.7",
                }

            # Add queries to space
            for query_name, query_template in queries.items():
                self.add_insight_query(
                    space_name,
                    query_name,
                    query_template,
                    f"{analysis_type} {query_name} analysis",
                )

            logger.info(
                f"Created {analysis_type} analysis dashboard in '{space_name}'"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to create analysis dashboard: {e}")
            return False

    def get_space_summary(self, space_name: str) -> Optional[Dict[str, Any]]:
        """Get summary of Genie space contents.

        Args:
            space_name: Genie space name

        Returns:
            Space summary dict or None
        """
        try:
            if space_name not in self.spaces:
                return None

            space = self.spaces[space_name]
            return {
                "name": space["name"],
                "description": space["description"],
                "dashboards": len(space["dashboards"]),
                "queries": len(space["queries"]),
                "insights": len(space["insights"]),
                "dashboards_list": [d["name"] for d in space["dashboards"]],
                "queries_list": [q["name"] for q in space["queries"]],
            }

        except Exception as e:
            logger.error(f"Failed to get space summary: {e}")
            return None

    def list_spaces(self) -> List[str]:
        """List all Genie spaces.

        Returns:
            List of space names
        """
        return list(self.spaces.keys())

    def export_space_config(self, space_name: str) -> Optional[Dict[str, Any]]:
        """Export space configuration.

        Args:
            space_name: Genie space name

        Returns:
            Space configuration dict or None
        """
        if space_name in self.spaces:
            return self.spaces[space_name]
        return None

    def delete_space(self, space_name: str) -> bool:
        """Delete Genie space.

        Args:
            space_name: Genie space name

        Returns:
            True if successful
        """
        try:
            if space_name in self.spaces:
                del self.spaces[space_name]
                logger.info(f"Deleted Genie space '{space_name}'")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete space: {e}")
            return False


# Global Genie manager instance
_genie_manager: Optional[GenieSpaceManager] = None


def get_genie_manager(
    databricks_client=None,
) -> Optional[GenieSpaceManager]:
    """Get or create Genie space manager instance.

    Args:
        databricks_client: DatabricksClient instance

    Returns:
        GenieSpaceManager instance or None
    """
    global _genie_manager

    if _genie_manager is None and databricks_client:
        _genie_manager = GenieSpaceManager(databricks_client)

    return _genie_manager
