# Hanging Flags Vertically

A static site that shows how to hang every country's flag horizontally and vertically.

- **The rule:** keep the canton (the upper corner next to the pole) at the top left as the viewer sees it. For most flags that means a quarter turn and then turning the flag over.
- **Every country:** 197 flags (UN members plus the Holy See, Palestine, Kosovo and Taiwan), each with a picture, horizontal and vertical directions, official proportions, sizes at that ratio, and links to buy one.
- **Exceptions:** the Union Flag (quarter turn only), flags with writing or emblems, Nepal.

Open `index.html` in a browser, or serve the folder with any static host (for example GitHub Pages). Link straight to a country with its ISO code, e.g. `index.html#de`.

## Files

- `index.html` – the page
- `countries.js` – generated country data
- `flags/` – flag SVGs from [hampusborgos/country-flags](https://github.com/hampusborgos/country-flags) (public domain, from Wikimedia Commons)
- `scripts/build_countries.py` – regenerates `countries.js` and `flags/` from a checkout of that repository:

```sh
git clone --depth 1 https://github.com/hampusborgos/country-flags.git /tmp/country-flags
python3 scripts/build_countries.py /tmp/country-flags
```

Directions, design types and notes per country live in `scripts/build_countries.py`.
