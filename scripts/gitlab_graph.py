import requests, datetime, os

USERNAME = os.environ["GITLAB_USERNAME"]
URL = f"https://gitlab.com/users/{USERNAME}/calendar.json"

response = requests.get(URL, headers={"Accept": "application/json"})
data = response.json()

today = datetime.date.today()
start = today - datetime.timedelta(days=364)

# Align start to the nearest Sunday before/on start date
while start.weekday() != 6:  # 6 = Sunday
    start -= datetime.timedelta(days=1)

# Build week columns
weeks = []
current_week = []
d = start
while d <= today:
    day_str = str(d)
    count = data.get(day_str, 0)
    current_week.append((day_str, count))
    if len(current_week) == 7:
        weeks.append(current_week)
        current_week = []
    d += datetime.timedelta(days=1)
if current_week:
    weeks.append(current_week)

max_val = max((c for _, c in sum(weeks, [])), default=1) or 1

def color(count):
    if count == 0: return "#161b22"
    r = count / max_val
    if r < 0.25: return "#0e4429"
    if r < 0.50: return "#006d32"
    if r < 0.75: return "#26a641"
    return "#39d353"

CELL = 11
GAP  = 3
ML   = 24   # margin left
MT   = 38   # margin top

# Month labels
month_labels = []
for wi, week in enumerate(weeks):
    first_day = datetime.date.fromisoformat(week[0][0])
    if first_day.day <= 7:
        x = ML + wi * (CELL + GAP)
        month_labels.append(
            f'<text x="{x}" y="{MT - 6}" fill="#8b949e" font-size="9" font-family="sans-serif">'
            f'{first_day.strftime("%b")}</text>'
        )

# Day labels (Mon, Wed, Fri)
day_labels = []
for di, label in [(1, "Mon"), (3, "Wed"), (5, "Fri")]:
    y = MT + di * (CELL + GAP) + CELL - 1
    day_labels.append(
        f'<text x="0" y="{y}" fill="#8b949e" font-size="9" font-family="sans-serif">{label}</text>'
    )

# Rects
rects = []
for wi, week in enumerate(weeks):
    for di, (day_str, count) in enumerate(week):
        x = ML + wi * (CELL + GAP)
        y = MT + di * (CELL + GAP)
        rects.append(
            f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{color(count)}">'
            f'<title>{day_str}: {count} contribution{"s" if count != 1 else ""}</title></rect>'
        )

total = sum(c for _, c in sum(weeks, []))
width  = ML + len(weeks) * (CELL + GAP) + 30
height = MT + 7 * (CELL + GAP) + 42

legend_x = width - 5 * (CELL + GAP) - 60
legend_colors = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
legend = [f'<text x="{legend_x - 4}" y="{height - 6}" fill="#8b949e" font-size="9" font-family="sans-serif">Less</text>']
for i, c in enumerate(legend_colors):
    lx = legend_x + 28 + i * (CELL + GAP)
    legend.append(f'<rect x="{lx}" y="{height - 16}" width="{CELL}" height="{CELL}" rx="2" fill="{c}"/>')
legend.append(f'<text x="{legend_x + 28 + 5*(CELL+GAP) + 2}" y="{height - 6}" fill="#8b949e" font-size="9" font-family="sans-serif">More</text>')

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" style="background:#0d1117;border-radius:8px;padding:8px">
  <text x="{ML}" y="14" fill="#e6edf3" font-size="11" font-family="sans-serif" font-weight="600">
    {total} GitLab contributions in the last year - {USERNAME}
  </text>
  {"".join(month_labels)}
  {"".join(day_labels)}
  {"".join(rects)}
  {"".join(legend)}
</svg>'''

os.makedirs("assets", exist_ok=True)
with open("assets/gitlab-contributions.svg", "w") as f:
    f.write(svg)

print(f"Done — {total} contributions plotted across {len(weeks)} weeks")
