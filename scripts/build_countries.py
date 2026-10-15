"""Build countries.js and copy flag SVGs for the site.

Usage: python3 -I scripts/build_countries.py <path-to-hampusborgos/country-flags checkout>

Flag images: https://github.com/hampusborgos/country-flags (public domain, from Wikimedia Commons).
Aspect ratios are read from each SVG's viewBox; the ratio labels below are the official
proportions (hoist : fly). Official government links come from data/official_links.tsv.
"""
import json, os, re, shutil, sys

SRC = sys.argv[1]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 193 UN members, plus the Holy See, Palestine, Kosovo and Taiwan.
CODES = """AD AE AF AG AL AM AO AR AT AU AZ BA BB BD BE BF BG BH BI BJ BN BO BR BS BT BW BY BZ
CA CD CF CG CH CI CL CM CN CO CR CU CV CY CZ DE DJ DK DM DO DZ EC EE EG ER ES ET FI FJ FM FR GA GB
GD GE GH GM GN GQ GR GT GW GY HN HR HT HU ID IE IL IN IQ IR IS IT JM JO JP KE KG KH KI KM KN KP KR
KW KZ LA LB LC LI LK LR LS LT LU LV LY MA MC MD ME MG MH MK ML MM MN MR MT MU MV MW MX MY MZ NA NE
NG NI NL NO NP NR NZ OM PA PE PG PH PK PL PS PT PW PY QA RO RS RU RW SA SB SC SD SE SG SI SK SL SM
SN SO SR SS ST SV SY SZ TD TG TH TJ TL TM TN TO TR TT TV TW TZ UA UG US UY UZ VA VC VE VN VU WS XK
YE ZA ZM ZW""".split()

NAMES = {
    "BO": "Bolivia", "BN": "Brunei", "CD": "DR Congo", "CG": "Republic of the Congo", "CN": "China",
    "FM": "Micronesia", "IR": "Iran", "KP": "North Korea", "KR": "South Korea", "LA": "Laos",
    "MD": "Moldova", "PS": "Palestine", "RU": "Russia", "SY": "Syria", "SZ": "Eswatini",
    "TR": "Türkiye", "TW": "Taiwan", "TZ": "Tanzania", "VA": "Vatican City", "VE": "Venezuela",
    "VN": "Vietnam", "ST": "São Tomé and Príncipe", "GM": "The Gambia", "BS": "The Bahamas",
}

# Official proportions where a small-denominator fraction of the viewBox would mislead.
RATIO = {"SV": "189:335", "TG": "1:1.618 (golden ratio)", "NP": "not rectangular"}

# Design types: p = plain geometric design (general rule), e = emblem, figure or writing,
# uk = Union Flag (rotate only), np = Nepal (not rectangular).
EMBLEM = {
    "AD": "a coat of arms", "AF": "an emblem with writing", "AL": "a double-headed eagle",
    "AO": "a machete-and-cog emblem", "AR": "the Sun of May (a sun with a face)",
    "BN": "a crest with Arabic writing", "BO": "a coat of arms",
    "BR": "a starry globe with the motto “Ordem e Progresso”", "BT": "a dragon",
    "BZ": "a coat of arms with a motto", "CR": "a coat of arms", "CY": "a map of the island",
    "DM": "a sisserou parrot", "DO": "a coat of arms with mottos", "EC": "a coat of arms",
    "EG": "the Eagle of Saladin with writing", "ER": "an olive wreath", "ES": "a coat of arms",
    "FJ": "a coat of arms", "GQ": "a coat of arms with a motto", "GT": "a coat of arms with writing",
    "HR": "a coat of arms", "HT": "a coat of arms with a motto",
    "IQ": "the words “Allahu Akbar”", "IR": "an emblem, and the Takbir written along the stripes",
    "KE": "a shield and spears", "KH": "Angkor Wat", "KI": "a frigatebird over a rising sun",
    "KR": "the taegeuk and four trigrams", "KZ": "a sun, an eagle and an ornament",
    "LB": "a cedar tree", "LI": "a crown", "LK": "a lion holding a sword", "LS": "a Basotho hat",
    "MD": "a coat of arms", "ME": "a coat of arms", "MN": "the Soyombo symbol", "MT": "the George Cross",
    "MX": "an eagle on a cactus", "MZ": "a rifle, a hoe and a book", "NI": "a coat of arms with writing",
    "OM": "the national emblem", "PE": "a coat of arms", "PG": "a bird of paradise",
    "PT": "the armillary sphere and coat of arms", "PY": "a different emblem on each side",
    "RS": "a coat of arms", "SA": "the shahada (written creed) and a sword", "SI": "a coat of arms",
    "SK": "a coat of arms", "SM": "a coat of arms", "SV": "a coat of arms with writing",
    "SZ": "a shield and spears", "TJ": "a crown and stars", "TM": "carpet patterns and a crescent",
    "UG": "a grey crowned crane", "UY": "the Sun of May (a sun with a face)",
    "VA": "crossed keys and a papal tiara", "VU": "a boar's tusk and fern leaves",
    "XK": "a map of Kosovo", "ZM": "an eagle", "ZW": "the Zimbabwe Bird",
}

# Colour of the top stripe (horizontal stripes) and of the stripe at the hoist (vertical stripes).
TOP = {
    "AM": "red", "AZ": "blue", "BG": "white", "BO": "red", "BY": "red", "CO": "yellow", "DE": "black",
    "EC": "yellow", "EE": "blue", "EG": "red", "ET": "green", "GA": "green", "GH": "red", "GM": "red",
    "HR": "red", "HU": "red", "ID": "red", "IN": "saffron", "IQ": "red", "IR": "green", "JO": "black",
    "KE": "black", "KW": "green", "LS": "blue", "LT": "yellow", "LU": "red", "LY": "red", "MC": "red",
    "MU": "red", "MW": "black", "NE": "orange", "NL": "red", "PH": "blue", "PL": "white", "PS": "black",
    "RS": "red", "RU": "white", "SD": "red", "SI": "white", "SK": "white", "SL": "green", "SS": "black",
    "SY": "green", "TJ": "red", "UA": "blue", "UG": "black", "UZ": "blue", "VE": "yellow", "YE": "red",
    "AE": "green", "BJ": "yellow", "MG": "red",
}
HOIST = {
    "FR": "blue", "IT": "green", "IE": "green", "BE": "black", "RO": "blue", "TD": "blue", "ML": "green",
    "GN": "red", "CI": "orange", "MX": "green", "MD": "blue", "CM": "green", "SN": "green", "PT": "green",
    "VA": "yellow", "DZ": "green", "PK": "white", "MT": "white", "AD": "blue", "AE": "red", "BJ": "green",
    "MG": "white",
}

# What sits in the canton, for flags where that is the thing to check.
CANTON = {
    "US": "the blue union with the stars", "GR": "the blue canton with the white cross",
    "AU": "the Union Flag", "NZ": "the Union Flag", "TV": "the Union Flag", "FJ": "the Union Flag",
    "MY": "the blue canton with the crescent and star", "LR": "the blue canton with the white star",
    "CL": "the blue square with the white star", "TO": "the white canton with the red cross",
    "TW": "the blue canton with the white sun", "TG": "the red canton with the white star",
    "UY": "the Sun of May", "WS": "the blue canton with the Southern Cross",
}

NOTES = {
    "US": "The US Flag Code says that against a wall, horizontal or vertical, the union goes uppermost and to the flag's own right, which is the observer's left. In a window it is placed the same way as seen from the street. Over the middle of a street, hang it vertically with the union to the north on an east–west street and to the east on a north–south street.",
    "CA": "Canadian Heritage says that when the flag hangs vertically, the top of the maple leaf points to the left as seen by the observer. These rules are mandatory on federal properties and at federal events.",
    "GB": "The Flag Institute says the broad white diagonal goes uppermost in the top-left corner whether the flag hangs horizontally or vertically. Turning it over as well would put it upside down.",
    "PH": "Philippine law (Republic Act 8491) has the blue stripe on top in peacetime and the red stripe on top only in a state of war. Hung vertically, the blue field goes on the viewer's left in peacetime.",
    "PL": "White on top. Upside down, it shows the red-over-white colours of Indonesia and Monaco.",
    "ID": "Red on top. Monaco's flag has the same colours but different proportions (4:5), and Poland's is white over red.",
    "MC": "Red on top. Indonesia's flag has the same colours but different proportions (2:3).",
    "DE": "Germany's official flags with the federal eagle are also made as vertical banners with the eagle upright.",
    "LI": "Flags of the World describes Liechtenstein's vertical flag as the horizontal design turned a quarter turn anticlockwise, with the crown kept upright in the top-left corner.",
    "SA": "The flag is made double-sided so the shahada reads correctly, right to left, from either side. Turning a normal flag sideways leaves the writing running vertically. Purpose-made vertical versions with the inscription and sword rotated are reported, and some sources say it should not be hung vertically at all.",
    "PY": "Paraguay's flag has the national coat of arms on the front and the treasury seal on the back. Turning it over for vertical hanging shows the back.",
    "AF": "The picture shows the black, red and green tricolour of the former Islamic Republic. Since 2021 the Taliban government has used a white flag with the shahada written on it. Both carry writing.",
    "BO": "The picture shows the state flag with the coat of arms. The plain civil flag without it follows the general rule.",
    "CR": "The picture shows the state flag with the coat of arms. The plain civil flag without it follows the general rule.",
    "PE": "The picture shows the state flag with the coat of arms. The plain civil flag without it follows the general rule.",
    "RS": "The picture shows the state flag with the coat of arms. The plain national flag without it follows the general rule.",
    "NP": "Nepal's flag is two stacked pennants and the only non-rectangular national flag. The hoist is the straight left edge. There is no standard vertical form, so display it in its own shape.",
    "KR": "The arrangement of the trigrams and of the red and blue halves of the taegeuk changes if the flag is turned the wrong way, so check it carefully against the picture.",
    "SY": "The picture shows the green, white and black flag with three red stars that the 2025 Constitutional Declaration made the national flag. The earlier red, white and black flag with two green stars is no longer official.",
    "CH": "Square and symmetrical, so it looks the same whichever way it hangs.",
    "BR": "Brazil is sometimes listed among countries with a special design for vertical hanging, but that is not confirmed in official sources here.",
}

# Fallback source where no government page was found: the English Wikipedia article.
WIKI = {
    "BS": "Flag_of_the_Bahamas", "CF": "Flag_of_the_Central_African_Republic", "CN": "Flag_of_China",
    "KM": "Flag_of_the_Comoros", "CG": "Flag_of_the_Republic_of_the_Congo", "CI": "Flag_of_Ivory_Coast",
    "GM": "Flag_of_the_Gambia", "GE": "Flag_of_Georgia_(country)", "MH": "Flag_of_the_Marshall_Islands",
    "FM": "Flag_of_the_Federated_States_of_Micronesia", "SB": "Flag_of_Solomon_Islands",
    "ST": "Flag_of_S%C3%A3o_Tom%C3%A9_and_Pr%C3%ADncipe", "TL": "Flag_of_Timor-Leste", "TR": "Flag_of_Turkey",
    "AE": "Flag_of_the_United_Arab_Emirates", "BN": "Flag_of_Brunei", "SZ": "Flag_of_Eswatini",
}

def load_links():
    links = {}
    with open(os.path.join(ROOT, "data", "official_links.tsv"), encoding="utf-8") as fh:
        next(fh)
        for line in fh:
            code, url, label = line.rstrip("\n").split("\t")
            links[code.upper()] = (url, label)
    return links

def aspect(code):
    s = open(os.path.join(SRC, "svg", code.lower() + ".svg"), encoding="utf-8").read()
    if re.search(r"<script|javascript:|\son\w+=|<foreignObject|href=\"https?:", s, re.I):
        raise SystemExit("unexpected content in " + code)
    head = s[:3000]
    vb = re.search(r'viewBox="([^"]+)"', head)
    if vb:
        p = [float(x) for x in re.split(r"[ ,]+", vb.group(1).strip())]
        return p[2] / p[3]
    w = float(re.search(r'<svg[^>]*\swidth="([\d.]+)', head).group(1))
    h = float(re.search(r'<svg[^>]*\sheight="([\d.]+)', head).group(1))
    return w / h

def ratio_label(a):
    from fractions import Fraction
    f = Fraction(1 / a).limit_denominator(40)
    return f"{f.numerator}:{f.denominator}"

names = json.load(open(os.path.join(SRC, "countries.json"), encoding="utf-8"))
links = load_links()
out = []
os.makedirs(os.path.join(ROOT, "flags"), exist_ok=True)
for c in CODES:
    a = aspect(c)
    t = "uk" if c == "GB" else "np" if c == "NP" else "e" if c in EMBLEM else "p"
    row = {"c": c.lower(), "n": NAMES.get(c, names[c]), "a": round(a, 4), "r": RATIO.get(c, ratio_label(a)), "t": t}
    if c in EMBLEM: row["em"] = EMBLEM[c]
    if c in TOP: row["top"] = TOP[c]
    if c in HOIST: row["hoist"] = HOIST[c]
    # Unicode flag emoji: the two regional indicator symbols for the ISO code. All 197 countries
    # here have one in the Unicode RGI emoji list (Kosovo uses XK).
    row["emoji"] = "".join(chr(0x1F1E6 + ord(ch) - ord("A")) for ch in c)
    if c in CANTON: row["canton"] = CANTON[c]
    if c in NOTES: row["note"] = NOTES[c]
    if c in links:
        row["src"], row["srcLabel"], row["gov"] = links[c][0], links[c][1], 1
    else:
        title = WIKI.get(c, "Flag_of_" + row["n"].replace(" ", "_"))
        row["src"], row["srcLabel"], row["gov"] = "https://en.wikipedia.org/wiki/" + title, "Wikipedia: " + title.replace("_", " ").replace("%C3%A3", "ã").replace("%C3%A9", "é").replace("%C3%AD", "í"), 0
    out.append(row)
    shutil.copyfile(os.path.join(SRC, "svg", c.lower() + ".svg"), os.path.join(ROOT, "flags", c.lower() + ".svg"))

out.sort(key=lambda r: r["n"])
with open(os.path.join(ROOT, "countries.js"), "w", encoding="utf-8") as fh:
    fh.write("// Generated by scripts/build_countries.py. Hoist : fly proportions, design type and hanging notes per country.\n")
    fh.write("window.COUNTRIES = " + json.dumps(out, ensure_ascii=False, indent=0) + ";\n")
print(len(out), "countries")
