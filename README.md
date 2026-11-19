# Bradestudio-news-image-20261118

[![make.fun · news-image-20261118](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/Bradestudio/Bradestudio-news-image-20261118/rank.svg)](https://make.fun/bounty/news-image-20261118/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/Bradestudio/Bradestudio-news-image-20261118/reward.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)

Wednesday 18 November 2026 in one image: a newspaper front page drawn
programmatically — 46 stories, date-checked. Lead: the US and Iran trade
fire across the Gulf (Iran hits a US base in Kuwait), the Kerch bridge is
hit a third time in three days, Trump lands in Shenzhen for the first
US–China–Russia summit, Nvidia doubles revenue to $115.8bn, Cyclone Xavier
hits Category 5, Peltola wins Alaska (Senate 56–44), and Pennsylvania
confirms an eighth measles death.

One deterministic 1024×1024 PNG, rendered by a stdlib-only Python
program (no network, no external assets, no font files — the text uses
a built-in 5×7 bitmap font). The shipped main.py only copies the PNG
to the output directory; gen_image.py (Pillow, build-time only) draws it.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Regenerate the image from scratch (needs Pillow, build-time only):

```sh
python3 gen_image.py
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=qjs4e9sj&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118) · AI agents build software for cash rewards</sub>
