from typing import Optional
from app.models.user import User
from app.models.stats import GitHubStats, WakaTimeStats, LeetCodeStats

def normalize(value: float, max_value: float, max_score: float) -> float:
    if value >= max_value:
        return max_score
    return (value / max_value) * max_score

def calculate_github_score(github: Optional[GitHubStats], user: User) -> float:
    if not github:
        return 0.0
    commits = normalize(github.commits_30d, 60, 120)
    prs = normalize(github.prs_merged_30d, 20, 100)
    streak = normalize(user.streak_current, 30, 100)
    lang_count = len(github.top_languages or [])
    langs = normalize(lang_count, 5, 80)
    return commits + prs + streak + langs  # max 400

def calculate_wakatime_score(wakatime: Optional[WakaTimeStats]) -> float:
    if not wakatime:
        return 0.0
    hours_7d = wakatime.week_seconds / 3600.0
    hours_score = normalize(hours_7d, 40, 200)
    # Consistency: number of distinct days with >0 seconds in last 7 days
    if wakatime.daily_breakdown:
        last_7_days = [d for d in wakatime.daily_breakdown if d["seconds"] > 0][:7]
        coded_days = len(last_7_days)
    else:
        coded_days = 0
    consistency_score = normalize(coded_days, 7, 150)
    return hours_score + consistency_score  # max 350

def calculate_leetcode_score(leetcode: Optional[LeetCodeStats]) -> float:
    if not leetcode:
        return 0.0
    solved = normalize(leetcode.total_solved, 200, 100)
    hard = normalize(leetcode.hard_solved, 50, 100)
    acc = normalize(leetcode.acceptance_rate, 70, 50)
    return solved + hard + acc  # max 250

def calculate_developer_score(user: User, github: Optional[GitHubStats], wakatime: Optional[WakaTimeStats], leetcode: Optional[LeetCodeStats]) -> int:
    github_score = calculate_github_score(github, user)
    wakatime_score = calculate_wakatime_score(wakatime)
    leetcode_score = calculate_leetcode_score(leetcode)
    total = (github_score * 0.40) + (wakatime_score * 0.35) + (leetcode_score * 0.25)
    return int(round(total))