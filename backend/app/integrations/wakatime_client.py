import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from app.core.config import settings

class WakaTimeClient:
    BASE_URL = "https://wakatime.com/api/v1"

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.headers = {"Authorization": f"Bearer {access_token}"}

    async def _get(self, endpoint: str) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(f"{self.BASE_URL}/{endpoint}", headers=self.headers)
            resp.raise_for_status()
            return resp.json()

    async def get_current_user(self) -> Dict[str, Any]:
        return await self._get("users/current")

    async def get_all_time_since_today(self) -> Dict[str, Any]:
        """Returns total coding time since account creation."""
        return await self._get("users/current/all_time_since_today")

    async def get_summaries(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Summaries for a date range (YYYY-MM-DD)."""
        return await self._get(f"users/current/summaries?start={start_date}&end={end_date}")

    async def get_stats(self, range_str: str = "last_30_days") -> Dict[str, Any]:
        """Pre‑computed stats for a range: 'last_7_days', 'last_30_days', etc."""
        return await self._get(f"users/current/stats/{range_str}")

    async def get_daily_breakdown(self, days: int = 30) -> List[Dict[str, Any]]:
        """Fetch daily totals for the last N days."""
        end = datetime.utcnow().date()
        start = end - timedelta(days=days)
        summaries = await self.get_summaries(start.isoformat(), end.isoformat())
        daily = []
        for day in summaries.get("data", []):
            daily.append({
                "date": day["range"]["date"],
                "seconds": day["grand_total"]["total_seconds"],
            })
        return daily