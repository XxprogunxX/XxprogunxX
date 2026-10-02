#!/usr/bin/env python3
import json
import re
import sys
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup

USERNAME = "XxprogunxX"
URL = f"https://github.com/users/{USERNAME}/contributions"

def fetch_contributions():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    response = requests.get(URL, headers=headers)
    if response.status_code != 200:
        print(f"Error fetching contributions: HTTP {response.status_code}", file=sys.stderr)
        sys.exit(1)

    soup = BeautifulSoup(response.text, "html.parser")
    
    # Map tooltips by element id
    tooltips = {}
    for tip in soup.find_all("tool-tip"):
        for_id = tip.get("for")
        if for_id:
            tooltips[for_id] = tip.get_text(strip=True)

    # Find table with contributions
    # GitHub uses <tbody ...> <tr> <td class="ContributionCalendar-day" ...>
    calendar_days = []
    total_count = 0

    # Summary heading
    h2 = soup.find("h2", id="js-contribution-activity-description")
    if h2:
        match_total = re.search(r"([\d,]+)\s+contributions", h2.get_text())
        if match_total:
            total_count = int(match_total.group(1).replace(",", ""))

    # Find all day cells
    # Day cells are either <td class="ContributionCalendar-day"> or have data-date
    days = soup.find_all("td", attrs={"data-date": True})
    
    parsed_days = []
    for day in days:
        date_str = day.get("data-date")
        level = int(day.get("data-level", "0"))
        cell_id = day.get("id")
        
        # Get count from tooltip or text
        tip_text = tooltips.get(cell_id, "")
        count = 0
        if "No contributions" in tip_text:
            count = 0
        else:
            match = re.search(r"(\d+)\s+contribution", tip_text)
            if match:
                count = int(match.group(1))
            elif level > 0:
                count = level  # fallback approximation if tooltip is missing

        parsed_days.append({
            "date": date_str,
            "count": count,
            "level": level,
            "id": cell_id
        })

    # Sort chronologically
    parsed_days.sort(key=lambda d: d["date"])

    if not parsed_days:
        print("Warning: No contribution days parsed!", file=sys.stderr)
        sys.exit(1)

    # Calculate streaks and stats
    # Current streak and longest streak
    current_streak = 0
    longest_streak = 0
    temp_streak = 0
    best_day = {"date": "", "count": 0}
    actual_total = 0

    for d in parsed_days:
        cnt = d["count"]
        actual_total += cnt
        if cnt > best_day["count"]:
            best_day = {"date": d["date"], "count": cnt}

        if cnt > 0:
            temp_streak += 1
            if temp_streak > longest_streak:
                longest_streak = temp_streak
        else:
            temp_streak = 0

    # Calculate current streak ending today or yesterday
    # Walk backward from last day
    cur = 0
    for d in reversed(parsed_days):
        if d["count"] > 0:
            cur += 1
        else:
            # If the last day has 0, maybe today hasn't happened yet, check yesterday
            if cur == 0:
                continue
            break
    current_streak = cur

    if total_count == 0:
        total_count = actual_total

    # Group into weeks (GitHub calendar columns, Sun-Sat or start day)
    # Each column in GitHub corresponds to a week of up to 7 days
    # Let's organize days by their weekday (0=Sun, ..., 6=Sat) or parse dates
    weeks = []
    current_week = []
    
    for d in parsed_days:
        dt = datetime.strptime(d["date"], "%Y-%m-%d")
        # Python weekday: 0=Mon, 6=Sun. GitHub calendar starts on Sunday (weekday 6)
        # So github_weekday: (dt.weekday() + 1) % 7 -> 0 is Sun, 6 is Sat
        gh_weekday = (dt.weekday() + 1) % 7
        d["weekday"] = gh_weekday

        if gh_weekday == 0 and current_week:
            weeks.append(current_week)
            current_week = []
        current_week.append(d)

    if current_week:
        weeks.append(current_week)

    data = {
        "username": USERNAME,
        "total_contributions": total_count,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "weeks_count": len(weeks),
        "days_count": len(parsed_days),
        "days": parsed_days,
        "weeks": weeks,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }

    with open("data/contributions.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"Successfully fetched contributions for {USERNAME}!")
    print(f"Total: {total_count} | Longest streak: {longest_streak}d | Current streak: {current_streak}d | Best day: {best_day['count']} ({best_day['date']})")

if __name__ == "__main__":
    fetch_contributions()
