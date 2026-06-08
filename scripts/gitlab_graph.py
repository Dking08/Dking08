import requests, datetime, os

USERNAME = os.environ["GITLAB_USERNAME"]
URL = f"https://gitlab.com/users/{USERNAME}/calendar.json"

response = requests.get(URL, headers={"Accept": "application/json"})
data = response.json()

today = datetime.date.today()
start = today - datetime.timedelta(days=364)

while start.weekday() != 6:
    start -= datetime.timedelta(days=1)

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

# GitLab's actual blue contribution palette (from the screenshot)
def color(count):
    if count == 0: return "#1f1f3a"
    r = count / max_val
    if r < 0.25: return "#3a3a7a"
    if r < 0.50: return "#5252b0"
    if r < 0.75: return "#6e6ecf"
    return "#8b8be8"

CELL = 11
GAP  = 3
ML   = 38
MT   = 52

# Official GitLab logo — fox mark only, scaled down to fit header
GITLAB_LOGO = '''<g transform="translate(6, 2) scale(0.072)">
  <path fill="#e24329" d="M301.95924,174.37243l-.2134-.55822-21.19899-55.30908c-.4236-1.08359-1.18542-1.99642-2.17699-2.62689-.98837-.63373-2.14749-.93253-3.32305-.87014-1.1689.06239-2.29195.48925-3.20809,1.21821-.90957.73554-1.56629,1.73047-1.87493,2.85346l-14.31327,43.80662h-57.90965l-14.31327-43.80662c-.30864-1.12299-.96536-2.11791-1.87493-2.85346-.91614-.72895-2.03911-1.15582-3.20809-1.21821-1.17548-.06239-2.33468.23641-3.32297.87014-.99166.63047-1.75348,1.5433-2.17707,2.62689l-21.19891,55.31237-.21348.55493c-6.28158,16.38521-.92929,34.90803,13.05891,45.48782.02621.01641.04922.03611.07552.05582l.18719.14119,32.29094,24.17392,15.97151,12.09024,9.71951,7.34871c2.34117,1.77316,5.57877,1.77316,7.92002,0l9.71943-7.34871,15.96822-12.09024,32.48142-24.31511c.02958-.02299.05588-.04269.08538-.06568,13.97834-10.57977,19.32735-29.09604,13.04905-45.47796Z"/>
  <path fill="#fc6d26" d="M301.95924,174.37243l-.2134-.55822c-10.5174,2.16062-20.20405,6.6099-28.49844,12.81593-.1346.0985-25.20497,19.05805-46.55171,35.19699,15.84998,11.98517,29.6477,22.40405,29.6477,22.40405l32.48142-24.31511c.02958-.02299.05588-.04269.08538-.06568,13.97834-10.57977,19.32735-29.09604,13.04905-45.47796Z"/>
  <path fill="#fca326" d="M197.0447,244.23117l15.97151,12.09024,9.71951,7.34871c2.34117,1.77316,5.57877,1.77316,7.92002,0l9.71943-7.34871,15.96822-12.09024s-13.79772-10.41888-29.6477-22.40405c-15.85327,11.98517-29.65099,22.40405-29.65099,22.40405Z"/>
  <path fill="#fc6d26" d="M180.14069,186.63014c-8.29111-6.20274-17.97446-10.65531-28.49507-12.81264l-.21348.55493c-6.28158,16.38521-.92929,34.90803,13.05891,45.48782.02621.01641.04922.03611.07552.05582l.18719.14119,32.29094,24.17392s13.79772-10.41888,29.65099-22.40405c-21.34673-16.13894-46.42031-35.09848-46.55499-35.19699Z"/>
</g>'''

# Month labels
month_labels = []
for wi, week in enumerate(weeks):
    first_day = datetime.date.fromisoformat(week[0][0])
    if first_day.day <= 7:
        x = ML + wi * (CELL + GAP)
        month_labels.append(
            f'<text x="{x}" y="{MT - 6}" fill="#9f9daa" font-size="9" font-family="sans-serif">'
            f'{first_day.strftime("%b")}</text>'
        )

# Day labels
day_labels = []
for di, label in [(1, "Mon"), (3, "Wed"), (5, "Fri")]:
    y = MT + di * (CELL + GAP) + CELL - 1
    day_labels.append(
        f'<text x="14" y="{y}" fill="#9f9daa" font-size="9" font-family="sans-serif">{label}</text>'
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
width  = ML + len(weeks) * (CELL + GAP) + 50
height = MT + 7 * (CELL + GAP) + 36

# Legend
legend_colors = ["#1f1f3a", "#3a3a7a", "#5252b0", "#6e6ecf", "#8b8be8"]
legend_x = width - len(legend_colors) * (CELL + GAP) - 100
legend = []
legend.append(f'<text x="{legend_x - 2}" y="{height - 6}" fill="#9f9daa" font-size="9" font-family="sans-serif">Less</text>')
for i, c in enumerate(legend_colors):
    lx = legend_x + 24 + i * (CELL + GAP)
    legend.append(f'<rect x="{lx}" y="{height - 16}" width="{CELL}" height="{CELL}" rx="2" fill="{c}"/>')
legend.append(f'<text x="{legend_x + 24 + len(legend_colors)*(CELL+GAP) + 2}" y="{height - 6}" fill="#9f9daa" font-size="9" font-family="sans-serif">More</text>')

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" style="background:#1a1a2e;border-radius:8px">
  {GITLAB_LOGO}
  <text x="34" y="18" fill="#fc6d26" font-size="13" font-family="sans-serif" font-weight="700">GitLab</text>
  <text x="34" y="32" fill="#c7c5d0" font-size="10" font-family="sans-serif">{total} contributions in the last year · {USERNAME}</text>
  {"".join(month_labels)}
  {"".join(day_labels)}
  {"".join(rects)}
  {"".join(legend)}
</svg>'''

os.makedirs("assets", exist_ok=True)
with open("assets/gitlab-contributions.svg", "w", encoding="utf-8") as f:
    f.write(svg)

print(f"Done — {total} contributions plotted across {len(weeks)} weeks")
