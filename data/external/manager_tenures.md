# Verified Manager Tenure Table

**Purpose.** Ground-truth attribution infrastructure for the player→manager compatibility model. A hard project rule is that every player-season (ideally player-match) observation must be attributed to the manager *actually in charge at the time*. Season-level joins are **unsafe** for the rows flagged `MID-SEASON` below.

**Compiled:** 2026-08-10 (all dates accessed 2026-08-10)
**Managers covered:** Pep Guardiola, Jürgen Klopp, Roberto De Zerbi
**Date format:** ISO `YYYY-MM-DD`. Where only month/year could be verified, `YYYY-MM`.

### Date conventions used in this file

Three different dates are routinely conflated by public sources. This table separates them:

| Field | Meaning |
|---|---|
| `announced_date` | Date the appointment/departure was publicly announced |
| `appointed_date` | Date the manager was **contractually/effectively** in charge |
| `first_match_date` | First competitive match in charge (the only date that matters for match-level attribution) |
| `departure_date` | Effective end of tenure (contract end, or the date of parting) |
| `last_match_date` | Last competitive match in charge |

**Modelling rule of thumb:** join on `first_match_date` / `last_match_date`, not on `appointed_date`, and never on season alone.

---

## 1. Core tenure table

`competition_tier` = tier of the domestic league pyramid at the time (1 = top division).

### Pep Guardiola

| # | manager | club | country | competition_tier | appointed_date | departure_date | seasons_covered | notes |
|---|---|---|---|---|---|---|---|---|
| G1 | Pep Guardiola | FC Barcelona B (Barça Atlètic) | Spain | 4 (Tercera División, Grupo V) → promoted to 3 | 2007-06-21 | 2008-06-30 | 2007/08 | **Full season — clean attribution.** First senior head-coach role. First match 2007-09-02 v CE Premià. Won the Tercera División group and the promotion play-off (v CF Extremadura, then UD Barbastro 2–0 / 1–0) to reach Segunda División B. Reserve-team football: squad churn and dual registration with the first team mean player-season data here is unreliable for modelling. |
| G2 | Pep Guardiola | FC Barcelona | Spain | 1 (La Liga) | 2008-07-01 (announced 2008-05-08; some sources give effect from 2008-06-17) | 2012-06-30 | 2008/09, 2009/10, 2010/11, 2011/12 | **Four full seasons — clean attribution.** Predecessor **Frank Rijkaard** (dismissed 2008-05-08). Departure announced 2012-04-27; last match the Copa del Rey final, 2012-05-25. Successor **Tito Vilanova** (his own assistant) — *confound warning*: Vilanova's 2012/13 Barcelona is stylistically near-continuous with Guardiola's, so 2012/13 data is NOT a clean "not-Guardiola" control. |
| G3 | Pep Guardiola | FC Bayern München | Germany | 1 (Bundesliga) | 2013-07-01 (announced 2013-01-16; first press conference 2013-06-24) | 2016-06-30 | 2013/14, 2014/15, 2015/16 | **Three full seasons — clean attribution.** Predecessor **Jupp Heynckes** (2012/13 treble). Last match the DFB-Pokal final, 2016-05-21 (0–0 v Borussia Dortmund, won 4–3 on penalties). Successor **Carlo Ancelotti**. |
| G4 | Pep Guardiola | Manchester City | England | 1 (Premier League) | 2016-07-01 (announced 2016-02-01) | 2026-06-30 | 2016/17 → 2025/26 (ten full seasons) | **Ten full seasons — clean attribution.** Predecessor **Manuel Pellegrini**. Departure announced 2026-05-22; last match 2026-05-24, Manchester City 1–2 Aston Villa — his 593rd match in charge. Took a role as City Football Group global ambassador. Successor **Enzo Maresca** (announced late June 2026, contract to June 2029; previously a Guardiola assistant — again a *continuity confound* for any 2026/27 control group). |

**National teams:** none verified. Guardiola has held **no** senior national-team head-coach role at any point.

---

### Jürgen Klopp

| # | manager | club | country | competition_tier | appointed_date | departure_date | seasons_covered | notes |
|---|---|---|---|---|---|---|---|---|
| K1 | Jürgen Klopp | 1. FSV Mainz 05 | Germany | 2 (2. Bundesliga) at appointment; **tier changed mid-tenure** | 2001-02-27 | 2008-06-30 | 2000/01 (part), 2001/02 … 2007/08 | ⚠️ **MID-SEASON APPOINTMENT.** Appointed 2001-02-27 after the dismissal of **Eckhard Krautzun**, with roughly 11–12 of 34 matchdays left (approx. **matchday 23**). Klopp was a Mainz *player* at the time (injured) and retired to take the job; first match a 1–0 win over MSV Duisburg. **Tier is not constant:** 2. Bundesliga 2000/01–2003/04 → promoted 2004 → Bundesliga 2004/05–2006/07 → relegated 2007 → 2. Bundesliga 2007/08. Departed at the end of 2007/08 after failing to win promotion back; public farewell in Mainz 2008-05-23. Any tier- or league-normalised feature must be computed per season, not per tenure. |
| K2 | Jürgen Klopp | Borussia Dortmund | Germany | 1 (Bundesliga) | 2008-07-01 (announced 2008-05, reported ~2008-05-23) | 2015-06-30 | 2008/09 → 2014/15 (seven full seasons) | **Seven full seasons — clean attribution.** Predecessor **Thomas Doll**. Initial two-year deal plus option. Departure announced 2015-04-15. Successor **Thomas Tuchel** from 2015-07-01. |
| K3 | Jürgen Klopp | Liverpool | England | 1 (Premier League) | **2015-10-08** | 2024-06-30 (last match 2024-05-19) | 2015/16 (part) → 2023/24 | ⚠️ **MID-SEASON APPOINTMENT — the single most important attribution hazard in this dataset.** Predecessor **Brendan Rodgers**, sacked 2015-10-04 after the Merseyside derby (Premier League **matchday 8**). Klopp appointed 2015-10-08 during the international break; **first match 2015-10-17, Tottenham 0–0 Liverpool = Premier League matchday 9**. So 2015/16 Liverpool player data splits ~8 PL games Rodgers / ~30 PL games Klopp, plus League Cup and Europa League runs that also split. **Do not attribute 2015/16 Liverpool to either manager at season level.** Departure: announced 2024-01-26; last match 2024-05-19 (Liverpool 2–0 Wolves, final day). Successor **Arne Slot**, officially in post 2024-06-01. |

**Non-coaching interlude:** Red Bull **Head of Global Soccer** from **2025-01-01** (announced 2024-10; unveiled at a press conference mid-January 2025). Not a coaching role — exclude from player attribution entirely, but note it as the reason for the 2024-06 → 2026-08 gap.

**National team:** **Germany** — appointed **2026-07-24** on a contract to 2030; role formally began **2026-08-15**. Predecessor **Julian Nagelsmann**, who resigned after Germany's 2026 World Cup round-of-32 exit to Paraguay on penalties. Assistants reported as Peter Krawietz, Pepijn Lijnders and Sven Bender. As of the compile date (2026-08-10) Klopp had **not yet taken a match**; there is therefore **no Germany player data attributable to Klopp** in any dataset built before 2026-08-15.

---

### Roberto De Zerbi

| # | manager | club | country | competition_tier | appointed_date | departure_date | seasons_covered | notes |
|---|---|---|---|---|---|---|---|---|
| D1 | Roberto De Zerbi | US Darfo Boario | Italy | 4 (Serie D) | 2013-11-19 | 2014-06-30 | 2013/14 (part) | ⚠️ **MID-SEASON APPOINTMENT.** First managerial job, taken shortly after retiring as a player. 22 matches, record commonly given as 5W 5D 12L. **Semi-professional Serie D — no usable event/tracking data exists.** Include for career completeness only. See §3 for a source conflict about promotion. |
| D2 | Roberto De Zerbi | Foggia Calcio | Italy | 3 (Lega Pro / Serie C) | 2014-07-01 | 2016-08-14 | 2014/15, 2015/16 | **Two full seasons — clean attribution.** Best attack in Lega Pro in 2014/15 (63 goals). Won the **Coppa Italia Lega Pro** in 2015/16. **Reached the promotion play-off final and LOST** (Foggia 1–1 Pisa, 2016-06-12; Pisa, managed by Gennaro Gattuso, promoted). Departed 2016-08-14, i.e. during pre-season for 2016/17 having taken no competitive 2016/17 matches. See §3 — several biography pages wrongly credit him with promotion to Serie B. |
| D3 | Roberto De Zerbi | US Città di Palermo | Italy | 1 (Serie A) | 2016-09-06 | 2016-11-30 | 2016/17 (part) | ⚠️ **MID-SEASON BOTH WAYS — worst-case attribution row.** Appointed 2016-09-06 replacing **Davide Ballardini**, who left after a draw at Inter on **matchday 2**. Dismissed 2016-11-30 after an eight-match losing run; 13 matches, 1 win (7.7%). Palermo then used **Eugenio Corini** (2016-11-30 → 2017-01-24), **Diego López** (2017-01-26 → 2017-04-11) and **Diego Bortoluzzi** (from 2017-04-11) — **five managers in one season**. Palermo 2016/17 data must be attributed at match level or discarded. |
| D4 | Roberto De Zerbi | Benevento Calcio | Italy | 1 (Serie A) | 2017-10-23 | 2018-06-30 | 2017/18 (part, from ~matchday 10) | ⚠️ **MID-SEASON APPOINTMENT.** Replaced **Marco Baroni**, sacked after **nine straight defeats from nine games** — the worst start in Serie A history — the day after a 3–0 home loss to Fiorentina. Benevento were relegated. **Severe selection/quality confound:** a historically bad squad; raw output metrics will not represent his intent. |
| D5 | Roberto De Zerbi | US Sassuolo Calcio | Italy | 1 (Serie A) | 2018-07-01 (announced 2018-06-13, initial two-year deal) | 2021-06-30 (last match 2021-05-23/24) | 2018/19, 2019/20, 2020/21 | **Three full seasons — clean attribution. This is the best "pure De Zerbi" club sample in Italy.** Predecessor **Giuseppe Iachini** (left 2018-06-05). Successor **Alessio Dionisi** (announced 2021-06-16, effective 2021-07-01). Mid-table Serie A resources — see the modelling warnings in Deliverable B. |
| D6 | Roberto De Zerbi | FC Shakhtar Donetsk | Ukraine | 1 (Ukrainian Premier League) | 2021-05-25 | 2022-07-11 | 2021/22 (**abandoned season**) | ⚠️ **DATA-INTEGRITY HAZARD, not a mid-season change.** Predecessor **Luís Castro** (departed 2021-05-12). The **2021/22 Ukrainian Premier League was suspended and abandoned** following the Russian full-scale invasion in February 2022; De Zerbi left Ukraine and formally departed 2022-07-11 citing the war. Successor **Igor Jovićević** (2022-07-14). Consequences: a truncated domestic season, a weak league (Shakhtar dominant → inflated possession/volume metrics), and patchy event-data coverage. The Champions League group-stage matches are the most comparable subset. |
| D7 | Roberto De Zerbi | Brighton & Hove Albion | England | 1 (Premier League) | **2022-09-18** (four-year deal) | 2024-06-30 (last match 2024-05-19) | 2022/23 (part) → 2023/24 | ⚠️ **MID-SEASON APPOINTMENT.** Predecessor **Graham Potter**, who left for Chelsea 2022-09-08 after Brighton's first four league fixtures. **Andrew Crofts** took one interim league game (2022-09-17, Brighton 0–0 Manchester City), with Adam Lallana as interim first-team coach. De Zerbi's **first match 2022-10-01, Liverpool 3–3 Brighton** — Brighton's 6th league fixture played, Premier League round 9 (Brighton's round-7 fixture v Crystal Palace was postponed following the death of Queen Elizabeth II). **2022/23 Brighton must be split at match level: ~4 fixtures Potter, 1 Crofts, remainder De Zerbi.** Additional confound: Potter's Brighton was *already* a possession/build-up side, so the pre/post contrast understates De Zerbi's own signal. Highest league finish in club history (6th, 2022/23) and first European qualification. Departure announced 2024-05-18; last match 2024-05-19. Successor **Fabian Hürzeler** (announced 2024-06-16). |
| D8 | Roberto De Zerbi | Olympique de Marseille | France | 1 (Ligue 1) | 2024-07-01 (announced 2024-06, three-year deal) | **2026-02-11** | 2024/25 (full), 2025/26 (part) | ⚠️ **MID-SEASON DEPARTURE.** Predecessor **Jean-Louis Gasset** (retired at the end of 2023/24). Left **by mutual consent** on 2026-02-11, days after a 5–0 defeat at Paris Saint-Germain (2026-02-08), with Marseille 4th and 12 points off PSG. Reported causes: loss of the dressing room, constant tactical changes and XI reshuffling. **Jacques Abardonado** caretaker 2026-02-11 → 2026-02-18; **Habib Beye** from 2026-02-18. Overall Marseille record commonly given as 69 matches, 39W 10D 20L (56.5%). **2025/26 Marseille must be split at match level.** See §3 — the matchday count at departure is uncertain. |
| D9 | Roberto De Zerbi | Tottenham Hotspur | England | 1 (Premier League) | **2026-03-31** (five-year deal) | *present* (as of 2026-08-10) | 2025/26 (part, final ~7 fixtures) → 2026/27 ongoing | ⚠️ **MID-SEASON APPOINTMENT into a relegation fight — extreme context confound.** Tottenham's 2025/26 sequence: **Thomas Frank** to 2026-02-11 (sacked after two wins in 17 league games) → **Igor Tudor** interim 2026-02-14 → 2026-03-29 (sacked after 44 days, seven games, one point from five PL games, final straw a 3–0 home loss to Nottingham Forest) → **De Zerbi** from 2026-03-31. Spurs were one point above the relegation zone with seven games left; De Zerbi's reported record is 7 matches, 3W 2D 2L, and **survival was achieved**. **Do not use these ~7 matches as a De Zerbi style sample** — they are a survival-mode sample in a broken squad. Assistant reported as Alessandro Nesta. |

**National teams:** none. De Zerbi has held no national-team role.

---

## 2. Attribution-safety summary (the operational output)

Rows are graded for whether a **season-level** player→manager join is safe.

| Grade | Meaning | Rows |
|---|---|---|
| 🟢 **SAFE** | Manager in charge for the whole season(s); season-level join valid | G1, G2 (all 4), G3 (all 3), G4 (all 10), K2 (all 7), D2 (both), D5 (all 3) |
| 🟡 **CAUTION** | Whole season, but the *sample* is compromised (league quality, abandoned season, semi-pro) | D1 (Serie D, no data), D6 (abandoned 2021/22 UPL), G1 (reserve-team churn) |
| 🔴 **UNSAFE — must split at match level** | Manager changed mid-season | **K1 2000/01** (from ~MD23), **K3 2015/16** (from PL MD9), **D1 2013/14** (from 2013-11-19), **D3 2016/17** (MD3 → MD~14, four other managers that season), **D4 2017/18** (from ~MD10), **D7 2022/23** (from Brighton's 6th fixture), **D8 2025/26** (to 2026-02-11), **D9 2025/26** (from 2026-03-31) |
| ⚫ **EXCLUDE** | Not a coaching role, or no matches yet | Klopp/Red Bull 2025-01-01→2024-06; Klopp/Germany (no match played before 2026-08-15) |

**Additional "false control" warning.** Three successions in this table are *stylistic continuations*, so the immediately-following season is **not** a valid non-manager control: Guardiola→**Vilanova** (Barcelona 2012/13), Guardiola→**Maresca** (Man City 2026/27), and **Potter**→De Zerbi (Brighton 2022/23, a possession-to-possession handover). Conversely Klopp→**Slot** (Liverpool 2024/25) and Klopp→**Tuchel** (Dortmund 2015/16) are genuine style changes and make better controls.

---

## 3. Rows where sources conflict or dates are uncertain

Treat every item below cautiously; each is a place where a naive scrape will introduce error.

| ID | Issue | Assessment |
|---|---|---|
| **C1** | **Klopp / Mainz appointment: 2001-02-27 vs 2001-02-28.** Wikipedia and most secondary sources give **27 February 2001**; some German-press-derived summaries give 28 February (apparently the date the Krautzun dismissal was *reported*). | Use **2001-02-27** as `appointed_date`. Immaterial for match-level joins — his first match is the anchor. |
| **C2** | **Klopp / Mainz first match date & matchday.** The 1–0 win over MSV Duisburg is well attested; I could not verify the calendar date or exact matchday from two independent sources. | Recorded as "approx. matchday 23 of 34, late February 2001". **Flagged uncertain — verify before using 2000/01 Mainz data at all.** |
| **C3** | **Klopp / Liverpool end date: 2024-05-17 vs 2024-05-19.** The Wikipedia managerial-statistics table renders an end date of 17 May 2024; Liverpool FC, CNN and match records confirm the **final match was 2024-05-19** (2–0 v Wolves), with Arne Slot officially in post **2024-06-01**. | Use **last_match_date = 2024-05-19**, **departure_date = 2024-06-30** (contract). The 17 May figure appears to be an artefact. |
| **C4** | **Guardiola / Barcelona start: 2008-05-08 vs 2008-06-17 vs 2008-07-01.** Laporta announced the appointment on 2008-05-08 "effective from 17 June 2008"; the season/contract convention is 2008-07-01. | Use **announced 2008-05-08**, **appointed 2008-07-01**. No impact — he took no competitive match before 2008/09. |
| **C5** | **Guardiola / Manchester City start: 2016-02-01 vs 2016-07-01.** The 1 February 2016 date (widely tabulated) is the *announcement*; he did not take charge until July 2016 while Pellegrini finished 2015/16. | Use **2016-07-01**. **This is a real trap**: a naive scrape of the announcement date would wrongly attribute the second half of Pellegrini's 2015/16 to Guardiola. |
| **C6** | **De Zerbi / Darfo Boario — promotion claim.** Several biography/aggregator pages state he "secured promotion to Serie C in his debut season". This is **inconsistent** with the widely-reported record of 5W 5D 12L from 22 matches. | **Treat the promotion claim as unverified and probably false.** Not corroborated by any primary or high-quality source I could reach. |
| **C7** | **De Zerbi / Foggia — promotion claim.** Some summaries state he won promotion to Serie B in 2016. Contemporaneous Italian press (Corriere dello Sport) and the play-off record show **Foggia 1–1 Pisa on 2016-06-12, with Pisa promoted**. | **Promotion claim is FALSE.** He won the **Coppa Italia Lega Pro** 2015/16 and *lost* the play-off final. Foggia's actual promotion to Serie B came in 2016/17 under a different manager, after De Zerbi had left. |
| **C8** | **De Zerbi / Sassuolo start: 2018-06-13 (announced, two-year deal) vs 2018-07-01 (effective).** Also **end: 2021-05-23/24 (last match) vs 2021-06-30 (contract).** | Both harmless — three complete seasons either way. Recorded as 2018-07-01 → 2021-06-30. |
| **C9** | **De Zerbi / Marseille — matchday at departure.** He left 2026-02-11, four days after the 5–0 PSG defeat of 2026-02-08. Sources are inconsistent about how many Ligue 1 rounds had been completed: the Marseille season page implies **26**, whereas an August-start 34-round Ligue 1 calendar implies roughly **22–24**. | **Date is firm (2026-02-11); matchday count is uncertain.** Split 2025/26 Marseille on the **date**, never on an assumed matchday. |
| **C10** | **De Zerbi / Brighton — matchday at first appearance.** Brighton's fixture list was disrupted (postponement following the death of Queen Elizabeth II), so "Premier League round" and "Brighton's Nth fixture played" diverge. | De Zerbi's first match **2022-10-01** = Brighton's **6th league fixture played** but Premier League **round 9**. Use the date. Do not reason in matchdays for 2022/23 Brighton. |
| **C11** | **Klopp / Dortmund appointment announcement date.** Sources agree on the 2008-07-01 effective date and a two-year-plus-option deal; the announcement is variously reported across May 2008 (≈2008-05-23 cluster). | Recorded as `2008-05` (month precision). No impact. |
| **C12** | **2026 events generally (Guardiola exit, Klopp→Germany, De Zerbi Marseille exit → Tottenham).** These are very recent. Each was corroborated against **at least two independent outlets** (see §4) but details such as exact contract lengths and compensation figures vary between reports. | Tenure **dates** are corroborated and safe. Treat contract lengths/fees as soft. |

**Not yet verifiable / open items**
- Klopp's successor at Mainz in 2008 was not verified against two sources and is therefore **omitted** rather than guessed.
- Whether Guardiola's Barcelona B row should count as a "senior club" is a judgement call; it is a reserve team in the fourth tier. Recommend retaining it in the tenure table for completeness but **excluding it from modelling**.

---

## 4. Sources

Each row above is corroborated by at least two independent sources. All accessed **2026-08-10**.

**General / all three managers**
1. Wikipedia — "Pep Guardiola", managerial statistics table. https://en.wikipedia.org/wiki/Pep_Guardiola
2. Wikipedia — "Jürgen Klopp", managerial statistics table. https://en.wikipedia.org/wiki/J%C3%BCrgen_Klopp
3. Wikipedia — "Roberto De Zerbi", managerial statistics table. https://en.wikipedia.org/wiki/Roberto_De_Zerbi
4. Premier League — Roberto De Zerbi manager profile. https://www.premierleague.com/managers/118012/Roberto-De-Zerbi/overview
5. Premier League — Jürgen Klopp manager profile. https://www.premierleague.com/managers/5119/J%C3%BCrgen-Klopp/overview

*Note: Transfermarkt and BDFutbol were intended as the primary independent cross-checks but both refused automated access (Transfermarkt blocked; BDFutbol HTTP 403), as did worldfootball.net (HTTP 403). Press and club-official sources were substituted throughout.*

**Guardiola**
6. FC Barcelona (official) — "15 years since Pep Guardiola announced as FC Barcelona coach". https://fcbarcelona.com/en/news/3326425/15-years-since-pep-guardiola-announced-as-fc-barcelona-coach
7. France 24 — "Rijkaard shown the door as Guardiola returns to Barca", 2008-05-08. https://www.france24.com/en/20080508-rijkaard-shown-door-guardiola-returns-barca-football-spain
8. UEFA.com — "Guardiola to replace Rijkaard at Barça". https://www.uefa.com/news-media/news/01cd-0e6f5e2ff2fe-8922e7a0de65-1000--guardiola-to-replace-rijkaard-at-barca
9. Al Jazeera — "Barcelona axe Rijkaard", 2008-05-08. https://www.aljazeera.com/sports/2008/5/8/barcelona-axe-rijkaard
10. Squawka — "What happened next? The 2007/08 Barcelona B team managed by Pep Guardiola" (Barcelona B first match, promotion play-off route). https://www.squawka.com/en/cult-corner/barcelona-b-team-managed-by-pep-guardiola/
11. Planet Football — "Where are they now? Guardiola's promotion-winning Barcelona B team". https://www.planetfootball.com/quick-reads/where-are-they-now-pep-guardiolas-promotion-winning-barcelona-b-team
12. Wikipedia — "2016 DFB-Pokal final" (Guardiola's last Bayern match, 2016-05-21). https://en.wikipedia.org/wiki/2016_DFB-Pokal_final
13. ESPN — Bayern 0–0 Dortmund, 2016-05-21, match report. https://www.espn.com/soccer/report?gameId=447906
14. Bavarian Football Works — 2016 DFB-Pokal final preview (Guardiola's final match). https://www.bavarianfootballworks.com/2016/5/21/11728328/bayern-munich-borussia-dortmund-2016-dfb-pokal-final-live-stream-tv-schedule-team-news
15. Fox Sports — "Pep Guardiola Leaving Manchester City After Season, Ending Dominant 10-Year Run" (departure announced 2026-05-22; global ambassador role). https://www.foxsports.com/stories/soccer/pep-guardiola-manchester-city-exit
16. ESPN — Man City 1–2 Aston Villa, 2026-05-24, match report/score. https://www.espn.com/soccer/report/_/espn/gameId/740970 · https://www.espn.com/soccer/match/_/gameId/740970/aston-villa-manchester-city
17. beIN Sports — "Manchester City 1-2 Aston Villa: Guardiola ends Premier League tenure with bittersweet defeat", 2026-05-24. https://www.beinsports.com/en-us/soccer/premier-league/articles/manchester-city-1-2-aston-villa-guardiola-ends-premier-league-tenure-with-bittersweet-defeat-2026-05-24
18. Wikipedia — "2025–26 Manchester City F.C. season". https://en.wikipedia.org/wiki/2025%E2%80%9326_Manchester_City_F.C._season
19. Sky Sports — "Enzo Maresca: Man City appoint former Chelsea head coach as Pep Guardiola's successor". https://www.skysports.com/football/news/11679/13548773/enzo-maresca-man-city-appoint-former-chelsea-head-coach-as-pep-guardiolas-successor-at-etihad-stadium
20. Al Jazeera — "Enzo Maresca appointed Manchester City manager to succeed Pep Guardiola", 2026-06-29. https://www.aljazeera.com/sports/2026/6/29/enzo-maresca-appointed-man-city-manager-to-succeed-pep-guardiola
21. ESPN — "Manchester City close to naming Enzo Maresca as Pep Guardiola successor". https://www.espn.com/soccer/story/_/id/49145825/manchester-city-close-naming-enzo-maresca-pep-guardiola-successor-sources

**Klopp**
22. Bundesliga.com — "The Jürgen Klopp story: From Bundesliga 2 to top of the world" (Mainz appointment, Krautzun dismissal, Duisburg first match, 2004 promotion, 2007 relegation, 2008 departure). https://www.bundesliga.com/en/2bundesliga/news/jurgen-klopp-story-from-bundesliga-2-to-top-of-the-world-mainz-liverpool-dortmund-28087
23. Bundesliga.com — "Bundesliga club-by-club historical guide: 1. FSV Mainz 05". https://www.bundesliga.com/en/bundesliga/news/mainz-bundesliga-club-by-club-historical-guide-klopp-tuchel-24188
24. Bundesliga.com — "Mainz's coaching cradle: Jürgen Klopp and Thomas Tuchel through to Bo Svensson". https://www.bundesliga.com/en/bundesliga/news/mainz-s-coaching-cradle-jurgen-klopp-thomas-tuchel-to-bo-svensson-15800
25. Sky Sports — "Klopp takes Dortmund job" (succeeding Thomas Doll; two-year deal plus option). https://www.skysports.com/football/news/3601879/klopp-takes-dortmund-job
26. UEFA.com — "Klopp named new Dortmund coach". https://www.uefa.com/news-media/news/01cd-0f84dc8e6ed6-d4fd2e8dc9ff-1000--klopp-named-new-dortmund-coach
27. BBC Sport — "Borussia Dortmund: Thomas Tuchel to replace Jurgen Klopp", 2015-04. https://feeds.bbci.co.uk/sport/football/32372080
28. ESPN — "Borussia Dortmund name Thomas Tuchel as successor to Jurgen Klopp". https://www.espn.co.uk/football/story/_/id/37412916/borussia-dortmund-name-thomas-tuchel-successor-jurgen-klopp
29. Sports Illustrated — "Dortmund hires Thomas Tuchel to replace Jurgen Klopp", 2015-04-19. https://www.si.com/soccer/2015/04/19/thomas-tuchel-borussia-dortmund-manager-jurgen-klopp
30. Liverpool FC (official) — "Liverpool beat Wolves to end the Jürgen Klopp era with a win at Anfield", 2024-05-19. https://www.liverpoolfc.com/news/liverpool-beat-wolves-end-jurgen-klopp-era-win-anfield
31. CNN — "An emotional farewell to Jurgen Klopp as he manages Liverpool for the last time", 2024-05-19. https://www.cnn.com/2024/05/19/sport/jurgen-klopp-liverpool-farewell-spt-intl
32. This Is Anfield — "Liverpool 2-0 Wolves: Jurgen Klopp's farewell", 2024-05-19 (and Arne Slot official start 1 June). https://www.thisisanfield.com/2024/05/liverpool-2-0-wolves-klopps-farewell-sees-stars-of-the-future-shine/
33. Red Bull (official) — "Jürgen Klopp joins Red Bull as Head of Global Soccer" / "Jürgen Klopp starts new role as Red Bull's Head of Global Soccer" (role from 2025-01-01). https://www.redbull.com/int-en/events/unleashing-the-future-jurgen-klopp-joins-red-bull · https://www.redbull.com/us-en/j%C3%BCrgen-klopp-new-role-as-red-bull-head-of-global-soccer
34. Sky Sports — "Former Liverpool boss Jurgen Klopp unveiled as Red Bull global head of soccer". https://www.skysports.com/football/news/11095/13288759/former-liverpool-boss-jurgen-klopp-unveiled-as-red-bull-global-head-of-soccer-and-explains-why-he-left-football-management
35. Bundesliga.com — "Jürgen Klopp appointed Red Bull's new Head of Global Soccer". https://www.bundesliga.com/en/bundesliga/news/juergen-klopp-red-bull-head-of-global-soccer-rb-leipzig-29277
36. CNN — "Former Liverpool manager Jürgen Klopp named head coach of Germany men's national team", 2026-07-24. https://www.cnn.com/2026/07/24/sport/jurgen-klopp-germany-head-coach
37. FIFA — "Germany confirm Jurgen Klopp appointment". https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/articles/jurgen-klopp-new-germany-coach
38. TNT Sports — "Jurgen Klopp appointed Germany manager on four-year deal" (Nagelsmann resignation after World Cup exit). https://www.tntsports.co.uk/football/world-cup/2026/jurgen-klopp-appointed-germany-manager-julian-nagelsmann-resigned-disastrous-world-cup-performance_sto23315702/story.shtml
39. Yahoo Sports — "Jürgen Klopp officially named Germany national team head coach", 2026-07-24. https://sports.yahoo.com/soccer/breaking-news/article/jurgen-klopp-officially-named-germany-national-team-head-coach-says-hell-leave-if-media-goes-after-his-family-133721176.html

**De Zerbi**
40. Wikipedia — "US Darfo Boario SSD". https://en.wikipedia.org/wiki/US_Darfo_Boario_SSD
41. Wikipedia (it) — "Foggia Calcio 2014-2015". https://it.wikipedia.org/wiki/Foggia_Calcio_2014-2015
42. Wikipedia (it) — "Foggia Calcio 2015-2016". https://it.wikipedia.org/wiki/Foggia_Calcio_2015-2016
43. Corriere dello Sport — "Lega Pro, Foggia-Pisa 1-1: caos allo Zaccheria, la squadra di Gattuso è in Serie B", 2016-06-12 (Foggia lost the play-off final). https://www.corrieredellosport.it/news/calcio/lega-pro-serie-d/2016/06/12-12358499/diretta_foggia-pisa_formazioni_segui_il_live_dalle_18
44. Wikipedia — "2015–16 Lega Pro". https://en.wikipedia.org/wiki/2015%E2%80%9316_Lega_Pro
45. UEFA.com (it) — "Palermo, De Zerbi è il nuovo allenatore", 2016-09. https://it.uefa.com/news-media/news/0231-0f8e319aa68f-0be26e00b0af-1000--palermo-de-zerbi-e-il-nuovo-allenatore/
46. Wikipedia — "2016–17 US Città di Palermo season" (five-manager sequence; Ballardini out after matchday 2). https://en.wikipedia.org/wiki/2016%E2%80%9317_US_Citt%C3%A0_di_Palermo_season
47. Football Italia — "Official: Benevento appoint De Zerbi", 2017-10-23. https://www.football-italia.net/111757/official-benevento-appoint-de-zerbi
48. ESPN — "Benevento sack Marco Baroni and name Roberto De Zerbi manager". https://www.espn.co.uk/football/benevento/story/3241308/benevento-sack-marco-baroni-and-name-roberto-de-zerbi-manager
49. Gulf News — "Benevento fire coach Baroni after losing first nine matches". https://gulfnews.com/sport/football/more-football/benevento-fire-coach-baroni-after-losing-first-nine-matches-1.2112008
50. Wikipedia — "2017–18 Benevento Calcio season". https://en.wikipedia.org/wiki/2017%E2%80%9318_Benevento_Calcio_season
51. ESPN — "Sassuolo hire coach Roberto De Zerbi on two-year contract" (2018-06-13; replacing Iachini). https://www.espn.co.uk/football/story/_/id/37556465/sassuolo-hire-coach-roberto-de-zerbi-two-year-contract
52. Calciomercato — "Roberto De Zerbi appointed as new Sassuolo manager". https://www.calciomercato.com/en/news/roberto-de-zerbi-appointed-as-new-sassuolo-manager-16936
53. Cult of Calcio — "Sassuolo Officially Appoint Alessio Dionisi to Replace Roberto De Zerbi" (2021-06-16, effective 2021-07-01). https://cultofcalcio.com/sassuolo-officially-appoint-alessio-dionisi-to-succeed-roberto-de-zerbi/
54. Shakhtar Donetsk (official) — "Benvenuto, Roberto!", 2021-05-25. https://shakhtar.com/en/news/2021/may/25_news/25_roberto-de-zerbi/
55. Shakhtar Donetsk (official) — "Introducing Shakhtar coaching staff", 2021-06-18. https://shakhtar.com/en/news/2021/june/18_news/18_coaching-staff/
56. Shakhtar Donetsk (official) — "Thank you, Mr Castro!", 2021-05-12 (Luís Castro departure). https://shakhtar.com/en/news/2021/may/12_news/12_luis-castro/
57. Wikipedia — "2021–22 FC Shakhtar Donetsk season" (season suspended/abandoned; De Zerbi departure). https://en.wikipedia.org/wiki/2021%E2%80%9322_FC_Shakhtar_Donetsk_season
58. Wikipedia — "2022–23 FC Shakhtar Donetsk season" (Jovićević appointed 2022-07-14). https://en.wikipedia.org/wiki/2022%E2%80%9323_FC_Shakhtar_Donetsk_season
59. BBC Sport — "Roberto de Zerbi: Brighton appoint Italian as manager", 2022-09-18. https://feeds.bbci.co.uk/sport/football/62950377
60. Sky Sports — "Roberto De Zerbi praises Graham Potter and targets top-10 finish after signing four-year deal as Brighton head coach". https://www.skysports.com/football/news/11741/12701023/roberto-de-zerbi-appointed-brighton-head-coach-on-four-year-deal
61. ESPN — "Brighton appoint Roberto De Zerbi as Graham Potter replacement". https://www.espn.com/soccer/brighton-and-hove-albion-engbrighton/story/4749734/brighton-appoint-roberto-de-zerbi-as-graham-potter-replacement
62. Wikipedia — "2022–23 Brighton & Hove Albion F.C. season" (Potter departure 2022-09-08; Andrew Crofts interim; De Zerbi first match 2022-10-01). https://en.wikipedia.org/wiki/2022%E2%80%9323_Brighton_%26_Hove_Albion_F.C._season
63. Soccerway / Flashscore — "Roberto de Zerbi to leave Brighton at end of Premier League season" (announced 2024-05-18). https://www.soccerway.com/news/soccer-premier-league-roberto-de-zerbi-to-leave-brighton-at-end-of-premier-league-season/rRFmB6K6
64. Malay Mail / AFP — "Brighton make Hurzeler, 31, youngest Premier League manager", 2024-06-16. https://malaymail.com/news/sports/2024/06/16/brighton-make-hurzeler-31-youngest-premier-league-manager/139965
65. BBC Sport — "Marseille appoint ex-Brighton boss De Zerbi", June 2024 (three-year deal; succeeded Jean-Louis Gasset). *URL now returns 404: https://feeds.bbci.co.uk/sport/football/articles/c4nnnl7gx08o — indexed in search results but not fetchable on 2026-08-10.*
66. Canberra Times / AAP — "Former Brighton boss De Zerbi appointed Marseille coach" (three-year deal, succeeding Gasset). https://www.canberratimes.com.au/story/8679608/former-brighton-boss-de-zerbi-appointed-marseille-coach/
67. beIN Sports — "Roberto de Zerbi Leaves Marseille by Mutual Consent", 2026-02-11. https://www.beinsports.com/en-us/soccer/ligue-1/articles/de-zerbi-leaves-marseille-by-mutual-consent-2026-02-11
68. AP via AOL — "Marseille coach De Zerbi leaves after humiliating 5-0 loss to PSG", 2026-02-11. https://www.aol.com/articles/marseille-coach-zerbi-leaves-humiliating-080929799.html
69. Wikipedia — "2025–26 Olympique de Marseille season" (Abardonado caretaker; Habib Beye from 2026-02-18). https://en.wikipedia.org/wiki/2025%E2%80%9326_Olympique_de_Marseille_season
70. Tribuna — "Reasons behind De Zerbi's departure from Marseille revealed: constant tactical changes and more", 2026-02-11. https://tribuna.com/en/news/2026-02-11-reasons-behind-de-zerbis-departure-from-marseille-revealed-constant-tactical-changes-and/
71. OneFootball — "What went wrong for De Zerbi at Marseille: The facts and figures". https://onefootball.com/en/news/what-went-wrong-for-de-zerbi-at-marseille-the-facts-and-figures-42393567
72. AP via WSLS — "De Zerbi hired to coach relegation-threatened Tottenham", 2026-03-31. https://www.wsls.com/sports/2026/03/31/struggling-premier-league-club-tottenham-hires-de-zerbi-amid-concerns-from-womens-fan-group/
73. Flashscore — "Tottenham confirm appointment of Roberto De Zerbi on five-year deal". https://www.flashscore.com/news/soccer-premier-league-tottenham-confirm-appointment-of-roberto-de-zerbi-on-five-year-deal/SnID2K9D
74. Fox News — "Igor Tudor sacked by Tottenham after just seven games in 44 days". https://www.foxnews.com/sports/igor-tudor-sacked-by-tottenham-after-just-seven-games-in-44-days-as-dismal-nottingham-forest-defeat-proves-to-be-final-straw.print
75. Wikipedia — "2025–26 Tottenham Hotspur F.C. season" (Frank to 2026-02-11; Tudor interim 2026-02-14 → 2026-03-29; De Zerbi from 2026-03-31). https://en.wikipedia.org/wiki/2025%E2%80%9326_Tottenham_Hotspur_F.C._season
76. Wikipedia — "List of Tottenham Hotspur F.C. managers". https://en.wikipedia.org/wiki/List_of_Tottenham_Hotspur_F.C._managers
77. Fox Sports — "What next for Roberto De Zerbi? Marseille meltdown…". https://www.foxsports.com/articles/soccer/what-next-for-roberto-de-zerbi-marseille-meltdown-suggests-ex-brighton-boss-isnt-cut-out-for-elite-level-management
