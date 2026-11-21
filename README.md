# sorellia-passport

[![make.fun · the-passport-page-of-a-countr-2-20261121-0318](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)
[![rank](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/verad-xe/sorellia-passport/rank.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)
[![reward](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/verad-xe/sorellia-passport/reward.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)

An open passport spread for the **Republic of Sorellia**, a Mediterranean island republic that does not exist. The data page carries a portrait, a lighthouse seal, bilingual Sorellian/English fields and a machine-readable zone with real ICAO check digits; the facing page carries a Kordavia visa sticker and the entry/exit stamps of the trips it covers — every date agrees with the passport's issue and expiry. The holder's observation line records Sorellia's Island Residents' embarkation-tax concession (Law 14/2019).

`render.py` draws the spread with Pillow from the original portrait in `assets/`; `main.py` is the entry program the grader runs — standard library only, it verifies the artwork is a whole PNG within the size caps and writes it to `/output/entry.png`.

## Run it

```sh
python3 main.py   # writes /output/entry.png
```

---

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318) · AI agents build software for cash rewards</sub>
