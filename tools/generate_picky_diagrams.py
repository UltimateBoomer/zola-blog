"""Regenerate Picky diagrams with Python's standard library. Sprite pixels are embedded
from Pixiverse's assets/sprites/onboarding/running chicken.png (first 16x16 frame).
Run: python3 tools/generate_picky_diagrams.py
SVG animation is explanatory, not a recording or benchmark of the Godot runtime.
"""
from pathlib import Path
from html import escape
import re
from math import hypot, sin, pi, exp

DEMO_SPEED = 60.0  # SVG units per second, shared by all three routes.
DEMO_CYCLE = 9.0  # Includes a pause after the longest route finishes.
OUT = Path(__file__).resolve().parents[1] / "content/blog/2026-09-30-pixiverse-picky"
SPRITE = '<rect x="5" y="2" width="1" height="1" fill="#3A3A50"/><rect x="6" y="2" width="1" height="1" fill="#3A3A50"/><rect x="7" y="2" width="1" height="1" fill="#3A3A50"/><rect x="8" y="2" width="1" height="1" fill="#3A3A50"/><rect x="9" y="2" width="1" height="1" fill="#3A3A50"/><rect x="5" y="3" width="1" height="1" fill="#3A3A50"/><rect x="6" y="3" width="1" height="1" fill="#CB2A2A"/><rect x="7" y="3" width="1" height="1" fill="#CB2A2A"/><rect x="8" y="3" width="1" height="1" fill="#CB2A2A"/><rect x="9" y="3" width="1" height="1" fill="#CB2A2A"/><rect x="10" y="3" width="1" height="1" fill="#3A3A50"/><rect x="5" y="4" width="1" height="1" fill="#3A3A50"/><rect x="6" y="4" width="1" height="1" fill="#CB2A2A"/><rect x="7" y="4" width="1" height="1" fill="#CB2A2A"/><rect x="8" y="4" width="1" height="1" fill="#CB2A2A"/><rect x="9" y="4" width="1" height="1" fill="#CB2A2A"/><rect x="10" y="4" width="1" height="1" fill="#CB2A2A"/><rect x="11" y="4" width="1" height="1" fill="#3A3A50"/><rect x="4" y="5" width="1" height="1" fill="#3A3A50"/><rect x="5" y="5" width="1" height="1" fill="#F1FFE6"/><rect x="6" y="5" width="1" height="1" fill="#CB2A2A"/><rect x="7" y="5" width="1" height="1" fill="#CB2A2A"/><rect x="8" y="5" width="1" height="1" fill="#CB2A2A"/><rect x="9" y="5" width="1" height="1" fill="#CB2A2A"/><rect x="10" y="5" width="1" height="1" fill="#CB2A2A"/><rect x="11" y="5" width="1" height="1" fill="#3A3A50"/><rect x="3" y="6" width="1" height="1" fill="#3A3A50"/><rect x="4" y="6" width="1" height="1" fill="#F1FFE6"/><rect x="5" y="6" width="1" height="1" fill="#F1FFE6"/><rect x="6" y="6" width="1" height="1" fill="#F1FFE6"/><rect x="7" y="6" width="1" height="1" fill="#F1FFE6"/><rect x="8" y="6" width="1" height="1" fill="#F1FFE6"/><rect x="9" y="6" width="1" height="1" fill="#F1FFE6"/><rect x="10" y="6" width="1" height="1" fill="#F1FFE6"/><rect x="11" y="6" width="1" height="1" fill="#F1FFE6"/><rect x="12" y="6" width="1" height="1" fill="#3A3A50"/><rect x="3" y="7" width="1" height="1" fill="#3A3A50"/><rect x="4" y="7" width="1" height="1" fill="#F1FFE6"/><rect x="5" y="7" width="1" height="1" fill="#F1FFE6"/><rect x="6" y="7" width="1" height="1" fill="#F1FFE6"/><rect x="7" y="7" width="1" height="1" fill="#F1FFE6"/><rect x="8" y="7" width="1" height="1" fill="#F1FFE6"/><rect x="9" y="7" width="1" height="1" fill="#F1FFE6"/><rect x="10" y="7" width="1" height="1" fill="#F1FFE6"/><rect x="11" y="7" width="1" height="1" fill="#F1FFE6"/><rect x="12" y="7" width="1" height="1" fill="#F1FFE6"/><rect x="13" y="7" width="1" height="1" fill="#3A3A50"/><rect x="1" y="8" width="1" height="1" fill="#3A3A50"/><rect x="2" y="8" width="1" height="1" fill="#3A3A50"/><rect x="3" y="8" width="1" height="1" fill="#3A3A50"/><rect x="4" y="8" width="1" height="1" fill="#F1FFE6"/><rect x="5" y="8" width="1" height="1" fill="#F1FFE6"/><rect x="6" y="8" width="1" height="1" fill="#F1FFE6"/><rect x="7" y="8" width="1" height="1" fill="#3A3A50"/><rect x="8" y="8" width="1" height="1" fill="#F1FFE6"/><rect x="9" y="8" width="1" height="1" fill="#F1FFE6"/><rect x="10" y="8" width="1" height="1" fill="#3A3A50"/><rect x="11" y="8" width="1" height="1" fill="#F1FFE6"/><rect x="12" y="8" width="1" height="1" fill="#F1FFE6"/><rect x="13" y="8" width="1" height="1" fill="#3A3A50"/><rect x="1" y="9" width="1" height="1" fill="#3A3A50"/><rect x="2" y="9" width="1" height="1" fill="#F1FFE6"/><rect x="3" y="9" width="1" height="1" fill="#3A3A50"/><rect x="4" y="9" width="1" height="1" fill="#F1FFE6"/><rect x="5" y="9" width="1" height="1" fill="#F1FFE6"/><rect x="6" y="9" width="1" height="1" fill="#F1FFE6"/><rect x="7" y="9" width="1" height="1" fill="#3A3A50"/><rect x="8" y="9" width="1" height="1" fill="#F1FFE6"/><rect x="9" y="9" width="1" height="1" fill="#F1FFE6"/><rect x="10" y="9" width="1" height="1" fill="#3A3A50"/><rect x="11" y="9" width="1" height="1" fill="#F1FFE6"/><rect x="12" y="9" width="1" height="1" fill="#F1FFE6"/><rect x="13" y="9" width="1" height="1" fill="#3A3A50"/><rect x="1" y="10" width="1" height="1" fill="#3A3A50"/><rect x="2" y="10" width="1" height="1" fill="#F1FFE6"/><rect x="3" y="10" width="1" height="1" fill="#F1FFE6"/><rect x="4" y="10" width="1" height="1" fill="#F1FFE6"/><rect x="5" y="10" width="1" height="1" fill="#F1FFE6"/><rect x="6" y="10" width="1" height="1" fill="#F1FFE6"/><rect x="7" y="10" width="1" height="1" fill="#F1FFE6"/><rect x="8" y="10" width="1" height="1" fill="#F8D239"/><rect x="9" y="10" width="1" height="1" fill="#F8D239"/><rect x="10" y="10" width="1" height="1" fill="#F1FFE6"/><rect x="11" y="10" width="1" height="1" fill="#F1FFE6"/><rect x="12" y="10" width="1" height="1" fill="#F1FFE6"/><rect x="13" y="10" width="1" height="1" fill="#3A3A50"/><rect x="1" y="11" width="1" height="1" fill="#3A3A50"/><rect x="2" y="11" width="1" height="1" fill="#F1FFE6"/><rect x="3" y="11" width="1" height="1" fill="#F1FFE6"/><rect x="4" y="11" width="1" height="1" fill="#F1FFE6"/><rect x="5" y="11" width="1" height="1" fill="#F1FFE6"/><rect x="6" y="11" width="1" height="1" fill="#F1FFE6"/><rect x="7" y="11" width="1" height="1" fill="#F1FFE6"/><rect x="8" y="11" width="1" height="1" fill="#D93232"/><rect x="9" y="11" width="1" height="1" fill="#F8D239"/><rect x="10" y="11" width="1" height="1" fill="#F8D239"/><rect x="11" y="11" width="1" height="1" fill="#F1FFE6"/><rect x="12" y="11" width="1" height="1" fill="#F1FFE6"/><rect x="13" y="11" width="1" height="1" fill="#3A3A50"/><rect x="2" y="12" width="1" height="1" fill="#3A3A50"/><rect x="3" y="12" width="1" height="1" fill="#F1FFE6"/><rect x="4" y="12" width="1" height="1" fill="#F1FFE6"/><rect x="5" y="12" width="1" height="1" fill="#F1FFE6"/><rect x="6" y="12" width="1" height="1" fill="#F1FFE6"/><rect x="7" y="12" width="1" height="1" fill="#F1FFE6"/><rect x="8" y="12" width="1" height="1" fill="#D93232"/><rect x="9" y="12" width="1" height="1" fill="#F1FFE6"/><rect x="10" y="12" width="1" height="1" fill="#F1FFE6"/><rect x="11" y="12" width="1" height="1" fill="#F1FFE6"/><rect x="12" y="12" width="1" height="1" fill="#3A3A50"/><rect x="3" y="13" width="1" height="1" fill="#3A3A50"/><rect x="4" y="13" width="1" height="1" fill="#F1FFE6"/><rect x="5" y="13" width="1" height="1" fill="#F1FFE6"/><rect x="6" y="13" width="1" height="1" fill="#F1FFE6"/><rect x="7" y="13" width="1" height="1" fill="#F1FFE6"/><rect x="8" y="13" width="1" height="1" fill="#F1FFE6"/><rect x="9" y="13" width="1" height="1" fill="#F1FFE6"/><rect x="10" y="13" width="1" height="1" fill="#F1FFE6"/><rect x="11" y="13" width="1" height="1" fill="#3A3A50"/><rect x="4" y="14" width="1" height="1" fill="#3A3A50"/><rect x="5" y="14" width="1" height="1" fill="#F8D239"/><rect x="6" y="14" width="1" height="1" fill="#3A3A50"/><rect x="7" y="14" width="1" height="1" fill="#3A3A50"/><rect x="8" y="14" width="1" height="1" fill="#3A3A50"/><rect x="9" y="14" width="1" height="1" fill="#3A3A50"/><rect x="10" y="14" width="1" height="1" fill="#F8D239"/><rect x="11" y="14" width="1" height="1" fill="#3A3A50"/><rect x="4" y="15" width="1" height="1" fill="#3A3A50"/><rect x="5" y="15" width="1" height="1" fill="#3A3A50"/><rect x="6" y="15" width="1" height="1" fill="#3A3A50"/><rect x="9" y="15" width="1" height="1" fill="#3A3A50"/><rect x="10" y="15" width="1" height="1" fill="#3A3A50"/><rect x="11" y="15" width="1" height="1" fill="#3A3A50"/>'

def text(x,y,s,size=16,color="#dce7ef"):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}">{escape(s)}</text>'

def line(points,color="#56d6ba",dash=""):
    return f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="{dash}"/>'

def picky(x,y,path=None):
    inner=f'<g transform="translate(-24,-42) scale(3)" shape-rendering="crispEdges">{SPRITE}</g>'
    if path:
        points = [(int(px), int(py)) for px, py in re.findall(r"[ML](-?\d+) (-?\d+)", path)]
        distance = sum(hypot(bx - ax, by - ay) for (ax, ay), (bx, by) in zip(points, points[1:]))
        arrival = distance / DEMO_SPEED / DEMO_CYCLE
        path = re.sub(r"([ML])(\d+) (\d+)", lambda m: f"{m[1]}{int(m[2])-x} {int(m[3])-y}", path)
        # A 3-unit hop every 0.32 s, synchronized across routes and idle on arrival.
        walk_seconds = distance / DEMO_SPEED
        bob_times = [0.0]
        bob_values = ["0 0"]
        step = 1
        while step * 0.16 < walk_seconds:
            bob_times.append(step * 0.16 / DEMO_CYCLE)
            bob_values.append("0 -3" if step % 2 else "0 0")
            step += 1
        bob_times.extend([arrival, 1.0])
        bob_values.extend(["0 0", "0 0"])
        times = ";".join(f"{t:.12g}" for t in bob_times)
        values = ";".join(bob_values)
        walking = f'<g>{inner}<animateTransform attributeName="transform" type="translate" values="{values}" keyTimes="{times}" dur="{DEMO_CYCLE:g}s" repeatCount="indefinite" calcMode="linear"/></g>'
        return f'<g class="moving" transform="translate({x},{y})">{walking}<animateMotion path="{path}" dur="{DEMO_CYCLE:g}s" repeatCount="indefinite" calcMode="linear" keyPoints="0;1;1" keyTimes="0;{arrival:.12g};1"/></g><g class="still" transform="translate({x},{y})">{inner}</g>'
    return f'<g transform="translate({x},{y})">{inner}</g>'

def svg(name,w,h,title,desc,body):
    data=f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">
<title id="title">{escape(title)}</title><desc id="desc">{escape(desc)}</desc>
<style>text {{ font-family: 'DejaVu Sans', sans-serif; }} .still {{ display:none; }} @media (prefers-reduced-motion:reduce) {{ .moving {{display:none}} .still {{display:inline}} }}</style>
<rect width="{w}" height="{h}" rx="18" fill="#101c2c"/>{body}</svg>'''
    (OUT/name).write_text(data)

body=text(28,40,"Three ways to follow the same player",25)
for i,(title,sub,route,path,color) in enumerate([
    ("Direct steering","Aim at the current player position.","70,220 294,290","M70 220 L145 243","#fa8d8d"),
    ("Grid A*","Search the walkable cells for a route.","70,220 102,220 102,162 262,162 262,290 294,290","M70 220 L102 220 L102 162 L262 162 L262 290 L294 290","#82baff"),
    ("Breadcrumb following","Replay the player’s recent footsteps.","70,220 70,370 294,370 294,290","M70 220 L70 370 L294 370 L294 290","#56d6ba")]):
    x=24+i*370
    body+=f'<g transform="translate({x},95)"><rect width="354" height="405" rx="12" fill="#1b2b40"/>'
    body+=text(18,32,title,21)+text(18,58,sub,13)
    for gx in range(38,330,32):
        body+=f'<path d="M{gx} 110 V390" stroke="#2c4055" stroke-width="1"/>'
    for gy in range(130,391,32):
        body+=f'<path d="M38 {gy} H326" stroke="#2c4055" stroke-width="1"/>'
    body+='<rect x="150" y="190" width="64" height="144" rx="4" fill="#69798f"/>'+text(160,263,"wall",14)
    body+=line("70,220 70,370 294,370 294,290","#7b8ea5","3 9")
    body+=line(route,color,"8 6" if i==0 else "")
    if i==2:
        for bx,by in [(70,330),(70,370),(145,370),(220,370),(294,370),(294,290)]:
            body+=f'<circle cx="{bx}" cy="{by}" r="5" fill="{color}"/>'
    body+='<circle cx="294" cy="290" r="12" fill="#f5cf71" stroke="#101c2c" stroke-width="3"/>'+text(266,266,"player",13)
    body+=picky(70,220,path)
    body+=text(18,92,["No route search","Computed route","Recorded route"][i],14,color)
    body+='</g>'
body+=text(40,531,"Blocked at the wall",16,"#fa8d8d")+text(410,531,"Can choose a different corridor",16,"#82baff")+text(780,531,"Uses the corridor the player took",16,"#56d6ba")
body+=line("40,562 88,562","#7b8ea5","3 9")+text(100,568,"player’s earlier walk",14,"#a5b7cb")
svg("picky-route-comparison.svg",1134,626,"Direct steering, grid A*, and breadcrumb following", "Picky moves toward a player beyond a wall. Direct steering stops at the wall. Grid search routes above it; breadcrumbs replay the player's route below it. The player is shown at the final destination.",body)

# Sample the movement and queue together so every visual shows the same state.
# Queue operations follow the game, with demo sample/reach distances and
# distance-based speed easing. Playback is slowed for this demo.
# Collision/stuck recovery is unnecessary on this clear route.
FPS = 84  # Approximately 60 displayed frames/s at the slowed playback rate.
DT = 1 / 168
DURATION = 10.24
PLAYBACK_DURATION = DURATION * 1.4
SAMPLE_DISTANCE = 6.0
DEMO_WAYPOINT_REACH_DISTANCE = 4.0
DEMO_FOLLOW_DISTANCE = 12.0
PLAYER_SPEED = 50.0
DESIRED_PLAYER_GAP = 26.0
MIN_FOLLOW_SPEED = 20.0
MAX_FOLLOW_SPEED = 75.0
SPEED_RESPONSE = 8.0
LOOP = [(24.0, 24.0), (104.0, 24.0), (104.0, 72.0), (24.0, 72.0), (24.0, 24.0)]

def player_at(t):
    remaining = (t * PLAYER_SPEED) % 256
    for a, b in zip(LOOP, LOOP[1:]):
        length = hypot(b[0] - a[0], b[1] - a[1])
        if remaining < length:
            dx, dy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
            return (a[0] + dx * remaining, a[1] + dy * remaining), (dx, dy)
        remaining -= length
    raise AssertionError("Unreachable loop position")

states = []
chicken = (4.0, 24.0)
follow_speed = PLAYER_SPEED
queue = [LOOP[0]]
next_frame = 0
for tick in range(round(DURATION / DT)):
    t = tick * DT
    player, direction = player_at(t)
    if not queue or hypot(player[0] - queue[-1][0], player[1] - queue[-1][1]) >= SAMPLE_DISTANCE:
        queue.append(player)
        queue = queue[-6:]
    while len(queue) > 1 and hypot(chicken[0] - queue[0][0], chicken[1] - queue[0][1]) <= DEMO_WAYPOINT_REACH_DISTANCE:
        queue.pop(0)
    follow = (player[0] - direction[0] * 8, player[1] - direction[1] * 8)
    walking = hypot(chicken[0] - follow[0], chicken[1] - follow[1]) > DEMO_FOLLOW_DISTANCE
    gap = hypot(player[0] - chicken[0], player[1] - chicken[1])
    target_speed = max(MIN_FOLLOW_SPEED, min(MAX_FOLLOW_SPEED,
        PLAYER_SPEED + 3.0 * (gap - DESIRED_PLAYER_GAP))) if walking else 0.0
    follow_speed += (target_speed - follow_speed) * (1 - exp(-SPEED_RESPONSE * DT))
    if walking:
        dx, dy = queue[0][0] - chicken[0], queue[0][1] - chicken[1]
        length = hypot(dx, dy)
        if length:
            chicken = (chicken[0] + dx / length * follow_speed * DT, chicken[1] + dy / length * follow_speed * DT)
    else:
        chicken = tuple(round(v) for v in chicken)
    if t + DT / 2 >= next_frame / FPS:
        states.append((t, player, chicken, list(queue), walking))
        next_frame += 1
assert all(1 <= len(state[3]) <= 6 for state in states)

body = text(28,40,"Following the breadcrumb trail",25)
body += '<defs><g id="queue-picky" shape-rendering="crispEdges">' + SPRITE + '</g></defs>'
body += '<rect x="36" y="76" width="544" height="384" rx="12" fill="#1b2b40"/>'
body += '<rect x="608" y="76" width="324" height="384" rx="12" fill="#1b2b40"/>'
for x in range(0,129,16):
    sx = 52 + x * 4
    body += f'<path d="M{sx} 92 V444" stroke="#32475f"/>' + text(sx-8,478,str(x),12,"#a5b7cb")
for y in range(0,89,16):
    sy = 92 + y * 4
    body += f'<path d="M52 {sy} H564" stroke="#32475f"/>' + text(8,sy+4,str(y),12,"#a5b7cb")
body += text(585,478,"x",13,"#a5b7cb") + text(12,72,"y",13,"#a5b7cb")
body += '<rect x="244" y="252" width="128" height="64" rx="5" fill="#69798f"/>'
body += text(630,110,"Queue",21) + text(630,137,"oldest → newest",14,"#a5b7cb")
body += '<circle cx="46" cy="506" r="7" fill="#f5cf71"/>' + text(61,511,"Player",14)
body += '<circle cx="160" cy="506" r="5" fill="#56d6ba"/>' + text(173,511,"Breadcrumb",14)

def state_graphic(state):
    t, player, chicken, q, walking = state
    def screen(point):
        return 52 + point[0] * 4, 92 + point[1] * 4
    points = " ".join(f"{x:.2f},{y:.2f}" for x,y in map(screen,[chicken] + q))
    frame = line(points,"#56d6ba")
    for i, point in enumerate(q):
        x,y = screen(point)
        color = "#f5cf71" if i == 0 else "#56d6ba"
        frame += f'<circle cx="{x:.2f}" cy="{y:.2f}" r="5" fill="{color}"/>'
        row = 177 + i * 44
        frame += f'<circle cx="646" cy="{row}" r="12" fill="{color}"/>'
        frame += text(642,row+5,str(i+1),13,"#101c2c")
        frame += text(674,row+5,f"({point[0]:.0f}, {point[1]:.0f})",17)
        if i == 0:
            frame += text(825,row+5,"target",13,"#f5cf71")
    x,y = screen(player)
    frame += f'<circle cx="{x:.2f}" cy="{y:.2f}" r="10" fill="#f5cf71" stroke="#101c2c" stroke-width="3"/>'
    x,y = screen(chicken)
    # Small walking bob, independent of the ground point/trail.
    bob = -3 * abs(sin(t * pi / 0.32)) if walking else 0
    frame += f'<g transform="translate({x-24:.2f},{y-42+bob:.2f}) scale(3)"><use href="#queue-picky"/></g>'
    frame += text(864,110,f"{len(q)}/6",16,"#56d6ba")
    return frame

body += '<g class="moving">'
for i,state in enumerate(states):
    start = i / len(states)
    end = (i+1) / len(states)
    if i == 0:
        times,values = f"0;{end:.12g};1", "1;0;0"
    elif i == len(states)-1:
        times,values = f"0;{start:.12g};1", "0;1;0"
    else:
        times,values = f"0;{start:.12g};{end:.12g};1", "0;1;0;0"
    body += f'<g opacity="{1 if i==0 else 0}">{state_graphic(state)}<animate attributeName="opacity" values="{values}" keyTimes="{times}" dur="{PLAYBACK_DURATION:g}s" repeatCount="indefinite" calcMode="discrete"/></g>'
body += '</g><g class="still">' + state_graphic(states[0]) + '</g>'
svg("picky-breadcrumb-queue.svg",960,534,"Picky following a live breadcrumb queue", "A gold player moves around an obstacle on a coordinate grid. Picky follows the oldest breadcrumb. The side queue shows the same retained coordinates and highlights the current target.",body)
