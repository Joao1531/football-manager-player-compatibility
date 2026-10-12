# Explanatory Video Script — CRISP-DM Applied to This Project

**Purpose (per Guidelines, `MIAD TFM_ Exemplos propostas final project.pdf`, page 4):** a video detailing each step of the CRISP-DM methodology as implemented in this specific project — accessible to a non-technical audience, educational about *how* CRISP-DM was applied here specifically, not a generic explainer of what CRISP-DM is in the abstract.

**Format recommendation:** hybrid screen recording. A handful of simple slides for structure (title, pipeline diagram, closing summary), cut together with live screen recording of the actual running Streamlit app (`localhost:8501`) and 2-3 quick cuts to notebook output. Your own voice narrates over all of it — this is not a slide deck read aloud.

**Target length:** 9-10 minutes. Every number below is the final, corrected, verified figure as of this session — do not use any older draft of this script.

**Before recording:** make sure the app is running (`streamlit run app/streamlit_app.py` from the project root, or reuse the already-running instance at `localhost:8501`), and have `notebooks/04_player_manager_compatibility.ipynb` open in a browser tab so you can scroll to specific cells on cue.

---

## Scene 0 — Cold open (0:00–0:30)

**Visual:** Title card. Three manager photos (already prepared at `report/assets/photos/*_sq.jpg`) with names, then the research question typed on screen.

**Say:**
"Can you teach a machine what makes Guardiola play like Guardiola, Klopp like Klopp, and De Zerbi like De Zerbi — and then tell a specific player how well he'd fit each one, and why? That's the question this project set out to answer. I'll walk you through how, using CRISP-DM, and I'll be honest about a finding that surprised even me while I was building this."

---

## Scene 1 — Business Understanding (0:30–1:45)

**Visual:** Simple diagram, built as a slide: `raw stats → football concepts → tactical dimensions → manager profile ↔ player profile → compatibility score → explanation`.

**Say:**
"Football clubs make expensive recruitment decisions on tactical fit all the time, often on gut feel and video review alone. The idea here: model a manager's playing philosophy as a set of measurable football characteristics, model a player the same way, and compare them, with the system able to *explain* its answer in football language, not just output a bare number.

One rule shaped everything downstream, and it's the single most important business rule in the whole project. A player's stats can only count toward a manager's profile for the exact matches that manager was actually in charge of that team, at match-date precision, never for the whole season. Managers get sacked or hired mid-season constantly. Liverpool's 2015/16 season, for example, split between Brendan Rodgers and Jürgen Klopp after just eight league games. Get this rule wrong, even slightly, and the whole model is silently measuring the wrong thing from the very first step."

---

## Scene 2 — Data Understanding (1:45–3:15)

**Visual:** Cut to a simple table slide: two data sources, coverage summary. Then cut briefly to `data/external/manager_tenures.md` scrolled to the Liverpool 2015/16 row, showing the mid-season split flagged in red/bold.

**Say:**
"Before writing a line of modelling code, I audited two real public data sources directly, by downloading and querying them, not by trusting their documentation. StatsBomb's open data is rich but sparse for these three managers. It covers Guardiola's Barcelona years in real depth, but has almost nothing for Klopp and literally zero matches for De Zerbi. The other source, FBref and Opta match-level statistics, covers all three managers from the 2017/18 season onward, but not before, which meant Guardiola's Barcelona and Bayern years, and Klopp's whole Dortmund era, were out of reach for this project's two-week timeline. I actually searched hard for an alternative before accepting that, and confirmed no adequate substitute exists.

I also built a fully verified table of exactly when each manager was in charge of which club, twenty separate tenure entries, each cross-checked against at least two independent sources. Eight of those twenty entries had to be flagged unsafe for season-level use, including two of the richest data seasons available, because of exactly this kind of mid-season change."

**Say (continued):**
"One thing I only discovered much later, during evaluation, and I'll come back to this: a chunk of the Italian and French league data I thought I had turned out to be completely missing specific statistical columns for the exact seasons I needed. That's a good example of why you always re-check your assumptions rather than trusting that a row existing means the data inside it is actually populated."

---

## Scene 3 — Data Preparation (3:15–4:00)

**Visual:** Quick cut to the integrity audit output, or a simple before/after diagram showing one club's season split into two colour-coded blocks by manager.

**Say:**
"With the tenure table verified, I built a dataset where every single match row is tagged with the correct manager, split at the exact match date where a manager changed, never at the season boundary. Before any modelling began, I ran an integrity check specifically looking for two things, any row outside its manager's correct window, and any duplicate match row. Both checks came back completely clean. Only after that passed did I move on to feature engineering."

---

## Scene 4 — Modelling, the Football Knowledge Layer (4:00–5:30)

**Visual:** The pipeline diagram again, this time zoomed into the concept and dimension layer. Cut briefly to the app's Tactical Profile tab, showing the radar chart for a selected player against the three managers.

**Say:**
"Here's the core modelling idea, and it's the one I'd defend most strongly if asked. I did not feed raw statistics into a black box. I built an explicit knowledge layer by hand. Raw numbers, things like progressive passes or touches inside the penalty area, get grouped into ten named football concepts, progressive passing, pressing intensity, box presence, and so on. Those ten concepts combine into seven broader tactical dimensions, anchored on a published, peer-reviewed, statistically validated taxonomy of football playing styles from the academic literature, not something I invented from scratch.

Every player and every manager ends up as a vector across these seven dimensions. A player's compatibility with a manager is the cosine similarity between their two vectors. I deliberately chose this over training a classifier to predict which manager a player played under, because a classifier, with only three classes and a small sample, would have the easiest possible shortcut available to it: just learn which club a player belongs to, since club and manager are almost perfectly correlated in this data. A similarity between two named, football-defined profiles can't take that shortcut, and because every dimension is named and traceable, I can always say exactly which football characteristics are driving any given score, not just report a number."

---

## Scene 5 — Evaluation, the honest part (5:30–7:45)

This is the most important section of the video. Do not rush it, and do not soften it.

**Visual:** Cut to the club-bias similarity numbers (can be read directly from `outputs/tables/club_bias_similarity_matrix_v2.csv` or just stated on screen as text). Then cut to the corrected accuracy progression as a simple three-step slide: 32.8% → 37.8% → 42.1%. Then cut to `outputs/tables/dimension_permutation_importance.csv` or the equivalent notebook cell output, highlighting pressing intensity's row.

**Say:**
"When I ran the club identity bias check, does the model actually pick up something about the manager, or just about which club has better players, I got a result that looked almost too clean. Two of De Zerbi's clubs looked like the statistical opposite of every other club in the dataset. That's suspicious, not exciting, so I dug into why instead of reporting it as a finding.

I found two real bugs. First, missing data was silently being converted into a literal zero instead of being left as genuinely unknown, which makes a total absence of data look, statistically, exactly like an extreme real observation. Second, I confirmed that specific statistical blocks for two leagues simply weren't published by the source for the seasons I needed, a gap the earlier row-level integrity check hadn't caught, because it checked whether the right matches were present, not whether the columns inside them were actually filled in.

Once both bugs were fixed, here's the honest first result. The model matched a player to the manager he actually played under thirty two point eight percent of the time, statistically no better than pure chance among three managers. And critically, that was true even for the two managers with perfect data coverage, Guardiola and Klopp, who came out at ninety eight percent similar to each other. That single fact tells you the problem wasn't missing data. It's that the features themselves were picking up which club has a stronger squad almost as strongly as anything about the manager specifically.

I didn't stop there. Recovering additional season-level data for the two affected leagues raised the figure to thirty seven point eight percent. Then, reviewing the whole pipeline specifically as a football analyst rather than an engineer, I found and fixed three concrete weaknesses, positions grouped too coarsely, pressing statistics not adjusted for how much possession a team's opponents actually had, and goalkeeper distribution data that had been collected but never used. Fixing all three raised the final figure to forty two point one percent, and I ran a formal significance test on that number specifically, because a single point estimate doesn't tell you how solid it is. A bootstrap confidence interval gives a range of thirty seven point eight to forty six point two percent, and a permutation test gives a p value of zero point zero zero zero two against the real chance baseline for this sample. That's genuinely, statistically significant. It's real.

Now, the part I want to be completely honest about, because it's the most interesting finding in the whole project. Pressing intensity turned out to be, by a wide margin, the single strongest dimension in the entire feature set, worth about seven and a half percentage points of accuracy on its own. That matches football analysis of Klopp's gegenpressing being his defining signature. But when I looked at the actual manager profiles, Guardiola's team score on possession-adjusted pressing intensity is marginally *higher* than Klopp's, not lower. That's the opposite of the popular narrative. De Zerbi's score is clearly the lowest of the three, exactly as expected, since his whole approach happens on the ball rather than off it. But the Guardiola versus Klopp result surprised me, and the most likely explanation is that Manchester City's possession dominance is so extreme in this sample that the possession adjustment, which corrects for how much of the ball a team's opponents have, actually over-corrects for a team this dominant. That's not a flaw I'm hiding. It's a concrete example of exactly the kind of squad-strength confound this whole project has been honest about from the start."

---

## Scene 6 — Deployment, and a live look at the application (7:45–9:15)

**Visual:** Full screen recording, live, of the running application. Suggested navigation, in order:
1. Show the sidebar. Select Season `2021/22`, League `Bundesliga`, Club `Dortmund`, Player `Erling Haaland`.
2. Point out the limitations warning banner at the top, visible before any result.
3. Show the Manager Fit tab: three manager cards, Guardiola as best fit, similarity score and dimension count.
4. Scroll to the explanation box: "Best fit: Pep Guardiola", the evidence and limiting-factor bullets.
5. Click the Tactical Profile tab: the radar chart.
6. Click the Playing-Style Cluster tab: the PCA scatter, Haaland's star marker near the cluster boundary.
7. Optionally: open the "Manager formation profiles" expander on the Tactical Profile tab, pointing out Klopp's 86.5% formation stability versus De Zerbi's 56.1%.

**Say:**
"All of this is built into a working, interactive application, not just a notebook. You can search any player from the top five European leagues, see their compatibility with all three managers, and read exactly why. Let me show you with a real example, Erling Haaland's 2021/22 season at Dortmund.

Guardiola comes out as the best fit here. The explanation says why: box presence is the strongest positive contributor, an extremely high rate of touches and shots inside the penalty area for his position. Pressing intensity is the biggest factor working against an even stronger match, exactly what you'd expect from a striker whose defensive workload off the ball is limited compared to his goal threat. Every single number here is traceable back to a named football characteristic. Nothing is a black box.

I also explored something I hadn't originally planned, using each match's starting formation, which had been sitting in the raw data unused since early in the project. It turns out Klopp is by far the most tactically settled of the three managers, using his main formation in nearly nine of every ten matches, while De Zerbi is the most fluid, using fifteen different formations across his career. I chose to report this descriptively rather than as a full model dimension, because it's only measurable for the specific clubs in my sample, a small population I didn't want to overstate the reliability of."

---

## Scene 7 — Closing (9:15–9:45)

**Visual:** Closing slide, three lines: "The pipeline works. Discrimination is real but limited, 42.1%, statistically significant. Pressing intensity is the strongest, most honestly examined signal."

**Say:**
"I'm not shipping a recruitment tool on this model. Forty two percent, while real and statistically significant, is not high enough to responsibly hand a club a definitive answer, and I say so, prominently, inside the application itself. What I am delivering is a complete, working, honestly evaluated pipeline, a knowledge-grounded feature system, and a rigorous account of exactly where it works, where it doesn't, and why, including a mistake I found in my own manager-profile analysis and corrected before showing you today. In data science, a well-diagnosed, honestly reported result, including its own corrections, is a real contribution. That's this project."

---

## Production notes

- **Keep code and notebooks mostly off-screen.** The two exceptions worth a quick, deliberate cut are the club-bias similarity numbers before the bug fix (Scene 5) and the permutation importance table showing pressing intensity's dominance (Scene 5). Everything else should be narrated over the diagram slides or the live app, not read off a notebook.
- **Scene 5 is the section most likely to come up in a defence.** Rehearse it until it's fluent without notes. It is this project's strongest evidence of methodological rigour, not a weakness to minimise, and the pressing-intensity correction specifically demonstrates that the same discipline was applied to this project's own writing, not just to its code.
- **Do not round the significance numbers up or down for effect.** Say "thirty seven point eight to forty six point two percent," not "roughly forty percent." The precision itself is part of the honesty this project is built on.
- **If you fluff the Guardiola/Klopp pressing explanation on the first take, just re-record that one paragraph.** It's the one part of the script where getting the causal reasoning slightly wrong (implying it's a flaw rather than a squad-strength confound) would misrepresent the finding.
