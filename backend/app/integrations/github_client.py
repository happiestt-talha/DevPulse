import httpx
from github import Github, GithubException
from github.Auth import Token
from typing import Dict, Any, List, Tuple
from datetime import datetime, timezone
from app.core.config import settings

class GitHubClient:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.rest_client = Github(auth=Token(access_token))
        self.graphql_endpoint = "https://api.github.com/graphql"

    async def get_user_info(self) -> Dict[str, Any]:
        user = self.rest_client.get_user()
        return {
            "id": user.id,
            "login": user.login,
            "name": user.name,
            "email": user.email,
            "avatar_url": user.avatar_url,
        }

    async def get_contribution_calendar(self, username: str) -> List[Dict[str, Any]]:
        query = """
        query($login: String!) {
          user(login: $login) {
            contributionsCollection {
              contributionCalendar {
                totalContributions
                weeks {
                  contributionDays {
                    date
                    contributionCount
                  }
                }
              }
            }
          }
        }
        """
        variables = {"login": username}
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.graphql_endpoint,
                json={"query": query, "variables": variables},
                headers={"Authorization": f"Bearer {self.access_token}"},
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
        calendar = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
        days = []
        for week in calendar["weeks"]:
            for day in week["contributionDays"]:
                days.append({"date": day["date"], "count": day["contributionCount"]})
        return days

    async def get_events_stats(self, username: str) -> Dict[str, Any]:
        # Use search or events API to get last 30 days stats
        # For simplicity: fetch user events (max 300) and aggregate
        events = self.rest_client.get_user(username).get_events()
        commits_30d = 0
        prs_merged_30d = 0
        reviews_given_30d = 0
        active_repos = set()
        now = datetime.now(timezone.utc)
        for event in events:
            if (now - event.created_at).days > 30:
                break
            if event.type == "PushEvent":
                commits_30d += event.payload.get("size", 0)
                active_repos.add(event.repo.name)
            elif event.type == "PullRequestEvent" and event.payload.get("action") == "closed" and event.payload.get("pull_request", {}).get("merged"):
                prs_merged_30d += 1
                active_repos.add(event.repo.name)
            elif event.type == "PullRequestReviewEvent":
                reviews_given_30d += 1
                active_repos.add(event.repo.name)
        return {
            "commits_30d": commits_30d,
            "prs_merged_30d": prs_merged_30d,
            "reviews_given_30d": reviews_given_30d,
            "active_repos_30d": len(active_repos),
        }

    async def get_lifetime_stats(self, username: str) -> Dict[str, Any]:
        user = self.rest_client.get_user(username)
        repos = user.get_repos()
        total_commits = 0
        total_prs_merged = 0
        total_issues_closed = 0
        total_stars_earned = 0
        lang_counter = {}
        for repo in repos:
            total_stars_earned += repo.stargazers_count
            try:
                # get commit count (approximate)
                commits = repo.get_commits(author=user)
                total_commits += commits.totalCount
            except:
                pass
            # PRs merged – would need search across repos, skip for now
            # Issues closed
            issues = repo.get_issues(state="closed", creator=user)
            total_issues_closed += issues.totalCount
            # Languages
            langs = repo.get_languages()
            for lang, bytes_ in langs.items():
                lang_counter[lang] = lang_counter.get(lang, 0) + bytes_
        # top languages by bytes
        total_bytes = sum(lang_counter.values())
        top_langs = []
        if total_bytes > 0:
            for lang, bytes_ in sorted(lang_counter.items(), key=lambda x: x[1], reverse=True)[:5]:
                top_langs.append({"language": lang, "percent": round(bytes_ / total_bytes * 100, 1)})
        return {
            "total_commits": total_commits,
            "total_prs_merged": total_prs_merged,
            "total_issues_closed": total_issues_closed,
            "total_stars_earned": total_stars_earned,
            "top_languages": top_langs,
        }