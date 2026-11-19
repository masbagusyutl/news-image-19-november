#!/usr/bin/env python3
"""Render a one-page newspaper front page summing up 19 November 2026.

Draws everything with PIL from the story list below: masthead, lead story
with a flat drawn illustration, a four-column story grid grouped by region
and field, a UTC timeline strip and a date-check footer. Output is a
1024x1024 PNG at most 1 MiB.
"""

import os
import textwrap

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

PAGE_W, PAGE_H = 1024, 1024
PAPER = (248, 244, 232)
INK = (24, 24, 22)
NAVY = (31, 58, 95)
RED = (163, 22, 33)
GOLD = (176, 141, 60)
GREY = (105, 100, 88)
RULE = (180, 172, 150)

FONT_DIR = "/usr/share/fonts/truetype/noto"


def font(name, size):
    path = os.path.join(FONT_DIR, name)
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


SERIF_B = lambda s: font("NotoSerif-Bold.ttf", s)
SERIF_R = lambda s: font("NotoSerif-Regular.ttf", s)
SANS_B = lambda s: font("NotoSans-Bold.ttf", s)
SANS_R = lambda s: font("NotoSans-Regular.ttf", s)


def wrap(draw, text, fnt, width):
    """Wrap text to fit pixel width, measuring each candidate line."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


LEAD = {
    "kicker": "LEAD STORY  •  SHENZHEN, CHINA",
    "headline": "TRUMP, XI AND PUTIN MEET IN SHENZHEN",
    "summary": (
        "The leaders of the United States, China and Russia hold a first-ever "
        "trilateral meeting on the sidelines of the APEC summit, with nuclear "
        "arms control on the agenda. Analysts expect symbolism, not a deal."
    ),
    "source": "BusinessWorld  •  Le Monde  •  Reuters",
}

# (section, headline, summary, source)
STORIES = [
    ("AMERICAS",
     "Jeffries set to be first Black Speaker",
     "House Democrats nominate Hakeem Jeffries for Speaker; he would be the first Black Speaker.",
     "NDTV / BBC"),
    ("AMERICAS",
     "House Democrats order Trump allies to save records",
     "Incoming Oversight chair Robert Garcia tells 12 Trump allies and relatives to preserve records.",
     "The Guardian / Cyprus Mail"),
    ("AMERICAS",
     "Liu Yunping makes history in House caucus",
     "Liu Yunping elected House Democratic Caucus chair, the first Taiwanese American.",
     "SimpleLife.news"),
    ("AMERICAS",
     "Peltola wins Alaska, Democrats keep 56-44 Senate edge",
     "Democrat Mary Peltola wins in Alaska, securing a 56-44 Senate majority for Democrats.",
     "The Daily Jagran"),
    ("AMERICAS",
     "US proposes tougher green-card rules",
     "Washington proposes stricter rules for employment-based green cards.",
     "The Daily Jagran"),
    ("EUROPE",
     "EU proposes \u20ac45bn loan for Ukraine",
     "Brussels proposes a \u20ac45bn loan for Kyiv, to be repaid once Russia pays reparations.",
     "Financial Times / Jagran Josh"),
    ("EUROPE",
     "M\u00e9lenchon \u2018could win\u2019 French presidency",
     "France\u2019s justice minister says M\u00e9lenchon could win the next presidential election.",
     "Jagran Josh"),
    ("EUROPE",
     "UK caps ground rent from 2028",
     "Leaseholders in England and Wales will have ground rent capped from 2028.",
     "BBC / The Guardian"),
    ("EUROPE",
     "UK inflation rises to 3.6%",
     "British inflation rose to 3.6% in October, the highest in a year, figures show.",
     "Reuters"),
    ("EUROPE",
     "Google rejects UK call to remove Brand video",
     "Google rejects a UK request to remove a Russell Brand YouTube video, sources say.",
     "BBC / The Guardian"),
    ("MIDDLE EAST",
     "Israeli troops launch Gaza ground operation",
     "Displaced Palestinians flee tents as Israeli troops open a rare ground operation.",
     "Crypto Economics News"),
    ("MIDDLE EAST",
     "US and Iran trade fire again",
     "US forces strike a missile site on Iran\u2019s Qeshm Island after Iran hit a US radar facility in Bahrain.",
     "SimpleLife.news"),
    ("MIDDLE EAST",
     "US sanctions three over Hezbollah links",
     "Washington sanctions three entities and three people over alleged Hezbollah funding links.",
     "OFAC / AppiSToS"),
    ("MIDDLE EAST",
     "Saudi Arabia: danger has passed in south",
     "Riyadh says the danger has passed in three southern cities after alerts.",
     "Jagran Josh"),
    ("MIDDLE EAST",
     "Somalia accuses UAE of secret bases",
     "Mogadishu accuses the UAE of secretly building military bases without federal approval.",
     "Disclosure News"),
    ("MIDDLE EAST",
     "Tanker hit in Strait of Hormuz",
     "A tanker is reported struck in the engine room near Khasab; the crew are safe, UKMTO says.",
     "UKMTO / AppiSToS"),
    ("ASIA-PACIFIC",
     "Cyclone Akvan bears down on India\u2019s east coast",
     "Akvan is likely to cross between Machilipatnam and Puri, officials say, as railways brace.",
     "The Hindu / Jagran Josh"),
    ("ASIA-PACIFIC",
     "India and Japan review defence ties",
     "Ministers hold a 2+2 dialogue in Tokyo on bilateral defence and strategic cooperation.",
     "Jagran Josh / The Hindu"),
    ("ASIA-PACIFIC",
     "Modi meets Prince and Princess of Wales",
     "India\u2019s prime minister discusses boosting UK\u2013India ties with the royal couple.",
     "The Hindu"),
    ("ASIA-PACIFIC",
     "Nvidia halts H-series chip shipments to China",
     "Nvidia says it has stopped shipping H-series chips to mainland China.",
     "SimpleLife.news"),
    ("ASIA-PACIFIC",
     "Australia sanctions Israeli settlers",
     "Canberra sanctions Israeli settlers and organisations over West Bank expansion.",
     "The Daily Jagran"),
    ("ASIA-PACIFIC",
     "ASX falls for a fifth straight session",
     "Australia\u2019s sharemarket closes lower again as Wall Street jitters and wage data rattle investors.",
     "Kalgoorlie Miner"),
    ("AFRICA",
     "Trump drops South Africa and Rwanda from AGOA",
     "Washington removes both countries from the African trade preference programme.",
     "BAHJOM Weekly Recap"),
    ("AFRICA",
     "Cocaine and pills seized in eastern Libya",
     "Officials say cocaine and millions of pills were seized in eastern Libya.",
     "Jagran Josh"),
    ("AFRICA",
     "Morocco maps defence industry to 2035",
     "Rabat targets 50,000 jobs and 65% export revenue from its defence industry by 2035.",
     "Hespress English"),
    ("BUSINESS & MARKETS",
     "Anthropic prices record $81.3bn IPO at $83",
     "The Claude maker\u2019s debut is the largest IPO ever; shares start trading on Nasdaq as ANT.",
     "Reuters / Bloomberg"),
    ("BUSINESS & MARKETS",
     "Nvidia\u2019s acting chief promises earlier pay rises",
     "Acting chief Colette Kress tells staff pay rises come in December.",
     "SimpleLife.news / Reuters"),
    ("BUSINESS & MARKETS",
     "Fed minutes point to more rate rises",
     "Most officials expect further hikes if inflation and jobs develop as expected, minutes show.",
     "Reuters / SimpleLife.news"),
    ("BUSINESS & MARKETS",
     "Oil falls as WTI drops 3.2% to $83.26",
     "Crude slides amid Middle East developments and rising risk aversion.",
     "Reuters / SimpleLife.news"),
    ("BUSINESS & MARKETS",
     "Gold sinks to 14-month low of $3,735",
     "Gold falls 3% as the dollar hits a fresh 19-month high.",
     "Reuters"),
    ("TECHNOLOGY",
     "Senators warn AI cyber threats outpace defences",
     "US senators warn the White House that AI-enabled cyber threats are outpacing defences.",
     "Jagran Josh"),
    ("TECHNOLOGY",
     "Alleged Russian spy arrested in Silicon Valley",
     "A suspected Russian espionage agent is arrested over targeting a Silicon Valley tech firm.",
     "Crypto Economics News"),
    ("TECHNOLOGY",
     "NSA network outage disrupts spies\u2019 work",
     "The NSA\u2019s classified internal network suffered an outage, forcing staff to adjust schedules.",
     "CNN / Disclosure News"),
    ("TECHNOLOGY",
     "Microsoft in talks to sell AI services to ByteDance",
     "Microsoft is reportedly in talks to sell AI services to ByteDance, drawing House scrutiny.",
     "SimpleLife.news"),
    ("SCIENCE",
     "Voyager 1 reaches one light-day from Earth",
     "NASA\u2019s probe, flying for almost 50 years, passes the milestone; confirmation due at a briefing.",
     "Disclosure News / Jagran Josh"),
    ("SCIENCE",
     "Earth\u2019s missing billion years may be explained",
     "Scientists say they may have found why over a billion years of geological history is missing.",
     "Space.com"),
    ("SCIENCE",
     "Bacterial toxin tied to early bowel cancer rise",
     "A bacterial toxin is linked to a surge in early-onset bowel cancer, researchers report.",
     "Nexus Europa"),
    ("CULTURE & SPORT",
     "GTA VI launches to a 99 on Metacritic",
     "Rockstar\u2019s game begins its global rollout after a 13-year wait, to near-perfect reviews.",
     "AP / Helsinki Times"),
    ("CULTURE & SPORT",
     "Duckett\u2019s 133 seals England\u2019s ODI series win",
     "England beat Australia by 97 runs in Hobart to take the series 2\u20131, their first there since 2018.",
     "Badiyaa / BBC"),
    ("CULTURE & SPORT",
     "Atalanta fight back to beat Chelsea 2\u20131",
     "Chelsea drop out of the Champions League top eight; Manchester City win again.",
     "BBC"),
    ("CULTURE & SPORT",
     "Greenwood double lifts Marseille in Europe",
     "Mason Greenwood scores twice as Marseille win 3\u20132 at Union Saint-Gilloise.",
     "BBC"),
]

# (time label, short label)
TIMELINE = [
    ("00:00 UTC", "GTA VI unlocks in Britain and Europe"),
    ("00:13 UTC", "Anthropic prices its IPO at $83"),
    ("00:15 UTC", "England\u2019s ODI series win reported"),
    ("00:22 UTC", "Democrats nominate Jeffries"),
    ("10:16 UTC", "Voyager 1 passes one light-day"),
    ("14:30 UTC", "Anthropic shares start trading"),
    ("THU", "Trump, Xi, Putin meet in Shenzhen"),
]


def draw_masthead(d):
    d.line([(20, 12), (1004, 12)], fill=INK, width=3)
    name = "THE WORLD LEDGER"
    f = SERIF_B(46)
    d.text(((PAGE_W - d.textlength(name, font=f)) / 2, 20), name,
           font=f, fill=INK)
    date = "THURSDAY  19  NOVEMBER  2026"
    f2 = SANS_B(19)
    d.text(((PAGE_W - d.textlength(date, font=f2)) / 2, 74), date,
           font=f2, fill=RED)
    tag = "One day\u2019s world news, on one page  \u2014  every story first reported on this day"
    f3 = SERIF_R(13)
    d.text(((PAGE_W - d.textlength(tag, font=f3)) / 2, 100), tag,
           font=f3, fill=GREY)
    d.line([(20, 120), (1004, 120)], fill=INK, width=2)
    d.line([(20, 123), (1004, 123)], fill=INK, width=1)


def draw_lead(d):
    y0 = 132
    # kicker
    d.text((20, y0), LEAD["kicker"], font=SANS_B(11), fill=RED)
    # headline, two lines
    f = SERIF_B(27)
    lines = wrap(d, LEAD["headline"], f, 730)
    y = y0 + 18
    for ln in lines[:2]:
        d.text((20, y), ln, font=f, fill=INK)
        y += 32
    # summary
    f2 = SANS_R(13)
    for ln in wrap(d, LEAD["summary"], f2, 730)[:3]:
        d.text((20, y), ln, font=f2, fill=INK)
        y += 17
    d.text((20, y + 2), "Source: " + LEAD["source"], font=SANS_R(10),
           fill=GREY)
    draw_lead_art(d, 780, y0 - 4, 224, 108)
    d.line([(20, 246), (1004, 246)], fill=RULE, width=1)


def draw_lead_art(d, x, y, w, h):
    """Flat illustration: a globe beside a Shenzhen-style skyline."""
    d.rectangle([x, y, x + w, y + h], fill=(233, 228, 210),
                outline=RULE, width=1)
    # sky
    d.rectangle([x, y, x + w, y + 62], fill=(214, 226, 238))
    # sun
    d.ellipse([x + w - 52, y + 8, x + w - 22, y + 38], fill=GOLD)
    # towers
    base = y + h
    towers = [(6, 34, 22), (30, 58, 20), (52, 44, 24), (78, 70, 20),
              (100, 52, 22), (124, 78, 20), (146, 46, 22), (170, 62, 20),
              (192, 40, 22)]
    for tx, th, tw in towers:
        d.rectangle([x + tx, base - th - 18, x + tx + tw, base - 18],
                    fill=NAVY)
    # ground
    d.rectangle([x, y + h - 18, x + w, y + h], fill=(120, 110, 88))
    # globe, left
    cx, cy, r = x + 34, y + 34, 24
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(158, 196, 222),
              outline=NAVY, width=2)
    d.ellipse([cx - 10, cy - r, cx + 10, cy + r], outline=NAVY, width=1)
    d.line([(cx - r, cy), (cx + r, cy)], fill=NAVY, width=1)
    d.arc([cx - r, cy - 14, cx + r, cy + 14], 200, 340, fill=NAVY, width=1)
    # three banners for the three leaders' countries
    for i, col in enumerate((RED, NAVY, GOLD)):
        bx = x + 78 + i * 16
        d.rectangle([bx, y + 66, bx + 10, y + 92], fill=col)


def section_header(d, x, y, w, label):
    d.rectangle([x, y, x + w, y + 18], fill=NAVY)
    d.text((x + 6, y + 3), label, font=SANS_B(11), fill=(255, 255, 255))
    return 22


def item_height(d, headline, summary, width):
    hl = wrap(d, headline, SANS_B(11), width)
    sl = wrap(d, summary, SANS_R(10), width)
    return len(hl[:2]) * 14 + len(sl[:2]) * 12 + 5, hl[:2], sl[:2]


def draw_item(d, x, y, width, headline, summary):
    h, hl, sl = item_height(d, headline, summary, width)
    yy = y
    for ln in hl:
        d.text((x, yy), ln, font=SANS_B(11), fill=INK)
        yy += 14
    for ln in sl:
        d.text((x, yy), ln, font=SANS_R(10), fill=(58, 56, 48))
        yy += 12
    return h


def draw_grid(d):
    top, bottom = 254, 886
    cols, gutter, margin = 4, 12, 20
    cw = (PAGE_W - 2 * margin - (cols - 1) * gutter) // cols
    xs = [margin + i * (cw + gutter) for i in range(cols)]
    col = 0
    y = top
    current = None
    for section, headline, summary, _src in STORIES:
        h, _, _ = item_height(d, headline, summary, cw)
        need = h + (22 if section != current else 0)
        if y + need > bottom:
            col += 1
            if col >= cols:
                raise RuntimeError("grid overflow: stories do not fit")
            y = top
            current = None
            need = h + 22
        if section != current:
            y += section_header(d, xs[col], y, cw, section)
            current = section
        y += draw_item(d, xs[col], y, cw, headline, summary)
        y += 1
    # vertical rules between columns
    for i in range(1, cols):
        rx = xs[i] - gutter // 2
        d.line([(rx, top), (rx, bottom)], fill=RULE, width=1)


def draw_timeline(d):
    y0 = 896
    d.rectangle([20, y0, 1004, y0 + 62], fill=NAVY)
    d.text((32, y0 + 6), "THE DAY IN UTC", font=SANS_B(11),
           fill=(255, 214, 130))
    slots = 7
    sw = (984 - 24) / slots
    for i, (t, label) in enumerate(TIMELINE):
        x = 32 + i * sw
        d.ellipse([x, y0 + 30, x + 7, y0 + 37], fill=(255, 214, 130))
        d.text((x + 11, y0 + 26), t, font=SANS_B(10), fill=(255, 255, 255))
        for j, ln in enumerate(wrap(d, label, SANS_R(9), sw - 14)[:2]):
            d.text((x, y0 + 40 + j * 11), ln, font=SANS_R(9),
                   fill=(220, 224, 232))


def draw_footer(d):
    y = 968
    d.line([(20, y), (1004, y)], fill=INK, width=2)
    check = ("DATE CHECK \u2014 Every story on this page happened, or was first "
             "reported, on Thursday 19 November 2026.")
    d.text((20, y + 7), check, font=SANS_B(11), fill=INK)
    src = ("Sources: Reuters \u2022 BBC \u2022 AP \u2022 Bloomberg \u2022 The Guardian "
           "\u2022 Le Monde \u2022 BusinessWorld \u2022 NDTV \u2022 The Hindu \u2022 "
           "Financial Times \u2022 CNN \u2022 Metacritic \u2022 Space.com \u2022 "
           "Hespress \u2022 UKMTO \u2022 OFAC \u2022 Full list in MODEL.md")
    for j, ln in enumerate(wrap(d, src, SANS_R(10), 984)[:2]):
        d.text((20, y + 26 + j * 13), ln, font=SANS_R(10), fill=GREY)


def main():
    img = Image.new("RGB", (PAGE_W, PAGE_H), PAPER)
    d = ImageDraw.Draw(img)
    draw_masthead(d)
    draw_lead(d)
    draw_grid(d)
    draw_timeline(d)
    draw_footer(d)
    img.save(OUT, "PNG", optimize=True)
    size = os.path.getsize(OUT)
    print(f"wrote {OUT}: {PAGE_W}x{PAGE_H}, {size} bytes")
    if size > 1048576:
        raise SystemExit("entry.png exceeds 1 MiB")


if __name__ == "__main__":
    main()
