import httpx
from typing import Dict, Any, Optional

class LeetCodeClient:
    GRAPHQL_URL = "https://leetcode.com/graphql"

    @staticmethod
    async def _graphql(query: str, variables: Optional[Dict] = None) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {"query": query}
            if variables:
                payload["variables"] = variables
            resp = await client.post(LeetCodeClient.GRAPHQL_URL, json=payload)
            resp.raise_for_status()
            data = resp.json()
            if "errors" in data:
                raise Exception(f"GraphQL error: {data['errors']}")
            return data

    @classmethod
    async def get_user_profile(cls, username: str) -> Dict[str, Any]:
        query = """
        query getUserProfile($username: String!) {
          matchedUser(username: $username) {
            username
            profile {
              realName
              ranking
              userAvatar
            }
            submitStats {
              acSubmissionNum {
                difficulty
                count
                submissions
              }
              totalSubmissionNum {
                difficulty
                count
                submissions
              }
            }
          }
        }
        """
        result = await cls._graphql(query, {"username": username})
        return result.get("data", {}).get("matchedUser")

    @classmethod
    async def get_recent_ac_submissions(cls, username: str, limit: int = 20) -> list:
        query = """
        query recentAcSubmissions($username: String!, $limit: Int!) {
          recentAcSubmissionList(username: $username, limit: $limit) {
            title
            status
            timestamp
            lang
          }
        }
        """
        result = await cls._graphql(query, {"username": username, "limit": limit})
        return result.get("data", {}).get("recentAcSubmissionList", [])

    @classmethod
    async def get_user_contest_ranking(cls, username: str) -> Optional[Dict[str, Any]]:
        query = """
        query userContestRanking($username: String!) {
          userContestRanking(username: $username) {
            rating
            globalRanking
            totalParticipants
            topPercentage
          }
        }
        """
        result = await cls._graphql(query, {"username": username})
        return result.get("data", {}).get("userContestRanking")