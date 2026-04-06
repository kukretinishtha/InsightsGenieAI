"""Geopolitical Analyst Agent for analyzing geopolitical impacts on stocks."""

import asyncio
import logging
from typing import Dict, Any, List

from src.agents.base import BaseAgent
from src.utils.logger import get_logger
from src.prompts.system_prompts import GEOPOLITICAL_ANALYST_SYSTEM_PROMPT
from src.data.clients import GeoPoliticalDataClient

logger = get_logger(__name__)


class GeopoliticalAnalystAgent(BaseAgent):
    """Agent for analyzing geopolitical factors affecting stock market."""
    
    def __init__(self):
        super().__init__()
        self.geo_client = GeoPoliticalDataClient()
        self._register_tools()
    
    def _register_tools(self):
        """Register geopolitical analysis tools."""
        
        self.register_tool(
            "get_geo_events",
            "Fetch recent geopolitical events affecting India",
            self.get_geo_events,
            timeout=30
        )
        
        self.register_tool(
            "assess_trade_impact",
            "Assess impact of trade policies on Indian economy",
            self.assess_trade_impact,
            timeout=30
        )
        
        self.register_tool(
            "analyze_country_risk",
            "Analyze country risk for affected regions",
            self.analyze_country_risk,
            timeout=30
        )
        
        self.register_tool(
            "evaluate_regional_stability",
            "Evaluate regional stability and its impact",
            self.evaluate_regional_stability,
            timeout=30
        )
        
        self.register_tool(
            "assess_geopolitical_risk_score",
            "Generate overall geopolitical risk score",
            self.assess_geopolitical_risk_score,
            timeout=30
        )
    
    async def analyze(self, symbol: str = None, **kwargs) -> Dict[str, Any]:
        """
        Analyze geopolitical factors affecting stock or market.
        
        Args:
            symbol: Stock symbol (optional)
            **kwargs: Additional parameters
        
        Returns:
            Dictionary with geopolitical analysis results
        """
        
        logger.info(f"Starting geopolitical analysis for {symbol or 'market'}")
        
        # Execute all tools in parallel
        results = await self.execute_tools_parallel(
            [
                "get_geo_events",
                "assess_trade_impact",
                "analyze_country_risk",
                "evaluate_regional_stability",
                "assess_geopolitical_risk_score"
            ],
            symbol=symbol
        )
        
        # Synthesize results
        synthesis = self._synthesize_analysis(results, symbol)
        
        logger.info(f"Geopolitical analysis completed for {symbol or 'market'}")
        
        return synthesis
    
    # Tool implementations
    
    async def get_geo_events(self, symbol: str = None, **kwargs) -> Dict[str, Any]:
        """Fetch and analyze recent geopolitical events."""
        
        try:
            # Get affected countries based on Indian trade partnerships
            affected_countries = ["US", "CHINA", "JAPAN", "RUSSIA", "UK", "EU"]
            
            events = await self.geo_client.get_events_for_countries(
                affected_countries,
                days=30
            )
            
            # Categorize events
            events_by_type = {}
            for event in events:
                event_type = event.event_type
                if event_type not in events_by_type:
                    events_by_type[event_type] = []
                events_by_type[event_type].append({
                    "country": event.country,
                    "severity": event.severity,
                    "description": event.description
                })
            
            return {
                "status": "success",
                "total_events": len(events),
                "events_by_type": events_by_type,
                "critical_events": [
                    e for e in events if e.severity == "critical"
                ],
                "latest_event_date": max(
                    (e.timestamp for e in events),
                    default=None
                )
            }
        
        except Exception as e:
            logger.error(f"Error fetching geo events: {e}")
            return {
                "status": "error",
                "error": str(e),
                "events": []
            }
    
    async def assess_trade_impact(self, symbol: str = None, **kwargs) -> Dict[str, Any]:
        """Assess impact of trade policies on Indian economy."""
        
        try:
            # Fetch current trade agreements
            trade_data = await self.geo_client.get_trade_agreements()
            
            # Key sectors affected by trade policies
            sectors_affected = {
                "IT": 0.3,  # Impact score 0-1
                "Pharma": 0.25,
                "Auto": 0.4,
                "Chemicals": 0.35,
                "Textiles": 0.5,
                "Electronics": 0.45,
                "Metals": 0.3
            }
            
            # Trade restrictions/agreements
            impact_analysis = {
                "tariff_changes": [],
                "trade_agreements": [],
                "export_restrictions": [],
                "import_duties": []
            }
            
            # Calculate overall trade impact
            trade_impact_score = sum(sectors_affected.values()) / len(sectors_affected)
            
            return {
                "status": "success",
                "trade_impact_score": trade_impact_score,
                "affected_sectors": sectors_affected,
                "impact_analysis": impact_analysis,
                "trend": "increasing" if trade_impact_score > 0.4 else "stable",
                "key_risks": [
                    "US-China trade tensions",
                    "Global supply chain disruptions",
                    "Tariff escalations"
                ]
            }
        
        except Exception as e:
            logger.error(f"Error assessing trade impact: {e}")
            return {
                "status": "error",
                "error": str(e),
                "trade_impact_score": 0.0
            }
    
    async def analyze_country_risk(self, symbol: str = None, **kwargs) -> Dict[str, Any]:
        """Analyze country risk for affected regions."""
        
        try:
            # Country risk scores based on various factors
            country_risks = {
                "US": {
                    "political_risk": 0.3,
                    "economic_risk": 0.2,
                    "regulatory_risk": 0.2,
                    "overall_risk": 0.25
                },
                "CHINA": {
                    "political_risk": 0.5,
                    "economic_risk": 0.4,
                    "regulatory_risk": 0.45,
                    "overall_risk": 0.45
                },
                "JAPAN": {
                    "political_risk": 0.15,
                    "economic_risk": 0.2,
                    "regulatory_risk": 0.1,
                    "overall_risk": 0.15
                },
                "RUSSIA": {
                    "political_risk": 0.7,
                    "economic_risk": 0.6,
                    "regulatory_risk": 0.65,
                    "overall_risk": 0.65
                }
            }
            
            # Find high-risk countries
            high_risk = {
                country: data for country, data in country_risks.items()
                if data["overall_risk"] > 0.4
            }
            
            return {
                "status": "success",
                "country_risks": country_risks,
                "high_risk_countries": list(high_risk.keys()),
                "risk_trend": "stable",
                "recommendations": [
                    "Monitor China-related policy changes",
                    "Watch US trade policy developments",
                    "Track Russia sanctions impact"
                ]
            }
        
        except Exception as e:
            logger.error(f"Error analyzing country risk: {e}")
            return {
                "status": "error",
                "error": str(e),
                "country_risks": {}
            }
    
    async def evaluate_regional_stability(self, symbol: str = None, **kwargs) -> Dict[str, Any]:
        """Evaluate regional stability and its impact."""
        
        try:
            # Regional stability assessment
            regions = {
                "Asia Pacific": {
                    "stability_score": 0.65,
                    "volatility": "high",
                    "key_issues": ["China tensions", "Taiwan strait", "Trade disputes"]
                },
                "Middle East": {
                    "stability_score": 0.4,
                    "volatility": "very high",
                    "key_issues": ["Iran sanctions", "Oil price volatility"]
                },
                "Europe": {
                    "stability_score": 0.7,
                    "volatility": "medium",
                    "key_issues": ["UK trade relations", "EU regulations"]
                },
                "Americas": {
                    "stability_score": 0.75,
                    "volatility": "low",
                    "key_issues": ["US policy changes"]
                }
            }
            
            # Calculate impact on Indian market
            india_exposure = {
                "Asia Pacific": 0.4,
                "Middle East": 0.2,
                "Europe": 0.25,
                "Americas": 0.15
            }
            
            weighted_risk = sum(
                regions[region]["stability_score"] * (1 - india_exposure[region])
                for region in regions
            )
            
            return {
                "status": "success",
                "regional_stability": regions,
                "india_exposure": india_exposure,
                "weighted_geopolitical_risk": weighted_risk,
                "most_volatile_region": "Middle East",
                "recommendations": [
                    "Monitor oil price movements",
                    "Track Asia-Pacific developments",
                    "Watch for Europe trade impacts"
                ]
            }
        
        except Exception as e:
            logger.error(f"Error evaluating regional stability: {e}")
            return {
                "status": "error",
                "error": str(e),
                "regions": {}
            }
    
    async def assess_geopolitical_risk_score(self, symbol: str = None, **kwargs) -> Dict[str, Any]:
        """Generate overall geopolitical risk score."""
        
        try:
            # Get results from other tools
            geo_events = await self.get_geo_events(symbol)
            trade_impact = await self.assess_trade_impact(symbol)
            country_risk = await self.analyze_country_risk(symbol)
            regional = await self.evaluate_regional_stability(symbol)
            
            # Aggregate scores
            scores = []
            
            if "trade_impact_score" in trade_impact:
                scores.append(trade_impact["trade_impact_score"] * 0.3)
            
            if "country_risks" in country_risk:
                avg_country_risk = sum(
                    data["overall_risk"] for data in country_risk["country_risks"].values()
                ) / len(country_risk["country_risks"])
                scores.append(avg_country_risk * 0.35)
            
            if "weighted_geopolitical_risk" in regional:
                scores.append(regional["weighted_geopolitical_risk"] * 0.35)
            
            overall_risk = sum(scores) if scores else 0.2
            
            # Risk classification
            if overall_risk > 0.6:
                risk_level = "CRITICAL"
            elif overall_risk > 0.4:
                risk_level = "HIGH"
            elif overall_risk > 0.2:
                risk_level = "MEDIUM"
            else:
                risk_level = "LOW"
            
            return {
                "status": "success",
                "overall_risk_score": overall_risk,
                "risk_level": risk_level,
                "component_scores": {
                    "trade_impact": trade_impact.get("trade_impact_score", 0),
                    "country_risk": country_risk.get("average_country_risk", 0),
                    "regional_risk": regional.get("weighted_geopolitical_risk", 0)
                },
                "affected_sectors": [
                    "Textiles", "Auto", "Chemicals", "IT"
                ],
                "market_outlook": "cautious" if overall_risk > 0.3 else "positive"
            }
        
        except Exception as e:
            logger.error(f"Error assessing geopolitical risk: {e}")
            return {
                "status": "error",
                "error": str(e),
                "overall_risk_score": 0.0
            }
    
    def _synthesize_analysis(self, results: Dict[str, Any], symbol: str = None) -> Dict[str, Any]:
        """Synthesize individual tool results into comprehensive analysis."""
        
        return {
            "analysis_type": "geopolitical",
            "symbol": symbol,
            "timestamp": asyncio.get_event_loop().time(),
            "system_prompt": GEOPOLITICAL_ANALYST_SYSTEM_PROMPT,
            "tools_executed": list(results.keys()),
            "summary": {
                "overall_risk_assessment": results.get(
                    "assess_geopolitical_risk_score", {}
                ).get("risk_level", "UNKNOWN"),
                "key_events": results.get("get_geo_events", {}).get("total_events", 0),
                "trade_impact": results.get("assess_trade_impact", {}).get("trend", "unknown"),
                "critical_countries": results.get("analyze_country_risk", {}).get(
                    "high_risk_countries", []
                ),
                "volatile_regions": results.get("evaluate_regional_stability", {}).get(
                    "most_volatile_region"
                )
            },
            "detailed_results": results,
            "execution_summary": {
                "tools_executed": len(results),
                "successful": sum(1 for r in results.values() if r.get("status") == "success"),
                "failed": sum(1 for r in results.values() if r.get("status") == "error")
            }
        }
