# SEP PROJECT — CLAUDE HANDOFF CONTEXT

**Instructions:** Paste this entire document as your FIRST message in any new Claude chat. Then say: *"This is the context of my SEP project — please read it fully, then I'll continue from where we left off."*

---

## WHO I AM

I am a student doing my SEP (entrepreneurship project). I have ~3 months to deliver a **working prototype**. I work full-time on it (40+ hrs/week). I have **almost zero budget**. I am based in Berlin / Europe.

My background: I grew up around my father's company **SwayamVaha Technologies Pvt. Ltd. (SVTPL)** — a 30+ year old industrial automation systems integrator based in India (www.swayamvaha.com). SVTPL integrates panels/automation systems from vendors like Siemens, Rockwell, Honeywell, Emerson into customers' plants across Oil & Gas, Power, Water, Pharma, F&B, and Manufacturing. SVTPL does NOT manufacture panels — they integrate.

I previously thought about GTM/sales but pivoted into **digital twinning for manufacturing**. I have 0 coding background but I'm learning Python as I build.

**Critical reframe:** I am NOT "a tech outsider learning to build software." I am **an industrial automation native** learning the software side. This matters for how I should be coached.

---

## THE VENTURE THESIS

**Problem (validated from 4-7 customer conversations my father helped me arrange):**
1. Unplanned downtime in manufacturing plants
2. Data is present but in several siloed systems — nothing is connected
3. Adding a new product requires trial-and-error on real lines, losing production days
4. Workforce knowledge is uneven — specific people hold critical know-how, creates bottlenecks

**The underlying single problem:** *Factory data and knowledge is scattered. Nothing talks to each other. So everything is slow, risky, and dependent on specific people.*

**The angle I'm taking:** Build an **AI analytics layer that sits on top of existing SCADA systems** (NOT a replacement for SCADA, NOT a full digital twin platform yet). Start with **predictive maintenance using existing SCADA log data** — no new hardware, no installation, just CSV export → analysis → insight report. This is technically a **digital shadow**, which is the standard starting point that becomes a digital twin once you add simulation + what-if capabilities later.

**Why this angle (vs. competing with Siemens/PTC/Deltia):**
- Top of market (Siemens Xcelerator, PTC ThingWorx, Dassault, Cognite) is locked up — large enterprise, 12-month deployments, $150K+ deals
- Middle of market is wide open — SMEs can't afford or operate enterprise platforms
- Brownfield (retrofitting existing factories) is the real job, not greenfield Industry 4.0
- My unfair advantage: SVTPL's existing customer relationships across India + Germany (Mittelstand outreach via AsiaBerlin)

**Why not Deltia (we studied them):** Deltia is computer-vision for *manual assembly lines* (humans assembling things). My customers are in process/discrete manufacturing — different problem, different buyer, different solution. Useful as a template for "start narrow, start with a shadow, expand to twin" but NOT to copy.

---

## CONFIRMED PILOT CUSTOMER

**Umasons Auto Compo Pvt. Ltd. (AITG Group)**
- Aurangabad, Maharashtra, India
- Founded 2000, ~₹100-500 cr revenue, 226 employees
- Tubular fabricated auto components: swing arms, handlebars, crash guards, trailing arms
- **First Indian supplier to BMW Germany (2003)** + Ducati, Bajaj
- Processes: bending, welding, casting, heat treatment, plasma cutting, **35-bath Ni-Cr electroplating, 14-tank powder coating, ED coating**
- Already runs TPM, SAP, ISO — mature on systems
- Has **PLC-controlled surface treatment lines**
- Status: VERBAL YES to pilot, awaiting first technical discovery call

**Why this is a perfect pilot:**
- Manufacturing-mature, automated, data-rich
- Already thinks about efficiency
- Supplies global OEMs (BMW/Ducati) so quality pressure is real
- SVTPL already has relationship
- Discrete/process manufacturing has measurable cycle times, visible failures, easy-to-prove ROI

**Top 3 candidate processes at Umasons for the pilot:**
1. Ni-Cr Electroplating line — 35 baths, massive process data, high cost of failure
2. Powder Coating line — 14-tank, defects = scrap/rework
3. Welding/bending/heat treatment lines — tool wear, dimensional drift

Need to look for a 2nd customer. Don't stop at one yes.

---

## THE 3-MONTH PLAN (TIGHT VERSION)

**Goal deliverable:** A working Python prototype that ingests SCADA-like CSV data, detects anomalies, predicts equipment failures, and shows results on a dashboard — validated by real customer data from Umasons (when available) + Letters of Intent.

### Month 1: Validate problem + start prototype on public data
- Schedule + run discovery call with Umasons technical team (5 questions only)
- Get specific process selected by customer
- Build MVP using **Microsoft Azure Predictive Maintenance dataset** (free, public, perfect for mock-up)
- Learn Python basics (CS50P + paired with Claude)
- Continue looking for 2nd customer

### Month 2: Build the prototype
- Streamlit dashboard
- Anomaly detection (Isolation Forest, scikit-learn — simple is fine)
- Failure prediction logic (LSTM autoencoder or even simpler)
- Optional: basic 2D visualization (skip 3D — too risky for timeline)
- Get SVTPL engineer code reviews (free, invaluable)
- Run analysis on Umasons real data IF received

### Month 3: Customer commitment + SEP package
- Convert demo into 2 Letters of Intent
- Run 1 small paid pilot (€2-5K, concierge MVP style — me + SVTPL engineer manually doing analysis)
- Build SEP submission: working prototype demo + 12-slide deck + 5-10 page report + customer evidence appendix
- CTO advisor credentialing: get Paresh Sarode (SVTPL CTO) as named technical advisor

---

## TECH STACK (FREE-ONLY, ZERO BUDGET)

- **3D viz:** Unity (free Industrial template) OR NVIDIA Omniverse — only attempt if Month 2 is on track, otherwise skip
- **Data simulation + analysis:** Python (pandas, scikit-learn, numpy)
- **Anomaly detection model:** Isolation Forest (simple, works, demoable)
- **Dashboard:** Streamlit (Python-based, free, build in a weekend)
- **Storage:** Local CSV / SQLite (no real DB needed)
- **Version control:** GitHub (free)
- **Pair programming partner:** Claude (paste errors, ask for explanations, learn by doing)

---

## DATASETS I'M USING FOR THE MVP

The MVP/mock-up is built using **publicly available manufacturing datasets** that mimic what real SCADA data looks like:

1. **Microsoft Azure Predictive Maintenance dataset** (primary) — telemetry (voltage, vibration, pressure, rotation), error logs, maintenance records, machine characteristics, failure events. Best fit for the use case.
2. **NASA Bearing Dataset / IMS Cincinnati** — run-to-failure bearing vibration data
3. **NASA CMAPSS Turbofan** — remaining useful life prediction benchmark
4. **Case Western Reserve Bearing Dataset (CWRU)** — bearing fault classification
5. **UCI Hydraulic Systems Condition Monitoring** — multi-sensor condition monitoring

When Umasons gives real CSV, I will modify the prototype to use their actual data instead of these public ones.

---

## CUSTOMER DISCOVERY CALL SCRIPT (5 QUESTIONS ONLY)

When I get on the Umasons call (or any customer call):

1. "Which one production line or process, when it has problems, costs you the most?" (let them define "costs")
2. "What does that problem look like? How do you find out about it today?"
3. "What SCADA or PLC data do you currently log on that line? For how long is it stored?"
4. "If I could give you one insight from that data that you don't have today, what would be most valuable?"
5. "If our analysis works, would you let us pilot it for real on one line for 60 days?"

DO NOT pitch digital twins. DO NOT explain AI. JUST listen and take notes.

---

## DATA POINTS TO ASK FOR (WHEN CUSTOMER SAYS YES)

For a motor / pump / VFD / surface treatment bath:
- Vibration (where applicable)
- Temperature (motor winding, bath temperature)
- Current draw (amps)
- Pressure (where applicable)
- Flow rate (where applicable)
- Run hours / on-off cycles
- **PLUS:** A list of failures, alarms, or unplanned stops in the 30-day window with rough timestamps. This is "ground truth" to validate the analysis.

For Umasons specifically (plating/coating lines):
- Bath chemistry readings
- Temperature per bath
- Current per bath
- Spray speed
- Cycle time per part
- Defect/rework log over 30 days

---

## PRINCIPLES I KEEP FORGETTING (REMIND ME)

1. **One step at a time.** I get overwhelmed when I try to plan all 3 months at once. Focus on this week.
2. **Stop researching, start doing.** I have a habit of reading more instead of executing. Each conversation should end with 1-3 concrete actions, not a reading list.
3. **My SVTPL access is my single biggest moat.** Use it ruthlessly.
4. **Customer evidence > code quality.** Examiners and investors care that someone wants this. Code can be ugly.
5. **The prototype is a demo, not production.** Don't try to build production-grade software in 3 months.
6. **I am NOT "0 tech experience."** I'm an industrial automation native. Stop saying I'm not technical.
7. **Don't pitch the customer "digital twin."** Pitch "free AI analysis of your existing SCADA data."
8. **One yes from a customer is enough to start. Two is the goal.**

---

## WHAT BLOCKS ME MOST OFTEN

- Feeling overwhelmed by too many options/decisions
- Researching instead of executing
- Getting lost in tools/tech instead of customer/problem
- Trying to design a perfect plan instead of doing the next small thing

**When I'm stuck, the right prompt is:** "Give me 3 things to do tomorrow. That's it. No strategy. No long paragraphs. Just 3 things."

---

## CURRENT STATUS (AS OF HANDOFF)

- 2 weeks into the SEP
- 4-7 customer discovery conversations done
- 1 confirmed pilot customer: Umasons Auto Compo (AITG Group)
- Discovery call with Umasons technical team being scheduled
- 2nd customer still being pursued via father
- MVP/mock-up will be built on Microsoft Azure Predictive Maintenance dataset (next concrete step)
- GitHub repo for prototype: TO BE CREATED

---

## HOW TO HELP ME GOING FORWARD

- **Don't write long paragraphs.** I get overwhelmed. Bullet-style is fine but keep it tight.
- **Always end with concrete next actions.** Not strategy. Actions I can do tomorrow.
- **Push back on me when I'm researching instead of executing.**
- **Help me code.** Explain code line-by-line when I paste it. Help me debug. Be my pair programmer.
- **Remind me of my SVTPL advantage.** I forget I have it.
- **Don't let me scope-creep.** If I say "what if I also add X" — push back unless X is essential.
- **Speak directly. Friend-mode, not consultant-mode.** I respond better to honest "you're confused because X" than diplomatic hedging.

---

## NEXT IMMEDIATE STEP

After pasting this context: I'll tell you where I'm at right now (e.g., "I had the Umasons call, here's what they said" OR "Help me set up the MVP code" OR whatever the current need is). Then we go from there — one step at a time.
