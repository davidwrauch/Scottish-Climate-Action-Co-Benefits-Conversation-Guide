# Scottish Climate Action Co-Benefits: Distributional Analysis (R & Python)

## TL;DR

* Climate co-benefits are not evenly distributed across communities
* Less deprived (more affluent) areas tend to receive larger total benefits
* This pattern appears in both Scotland and England, and is stronger in England
* Results were consistent across both R and Python implementations

---

## What this is

This project looks at how the benefits of climate interventions are distributed across communities with different levels of deprivation.

The main question is:

> Are climate co-benefits flowing more to deprived communities, or to more affluent ones?

I ran the analysis in both **R and Python** to:

* sanity check results across tools
* understand how workflows differ
* make the project more portable

---

## Data

The analysis uses small-area level data for:

* modeled climate co-benefits (air quality, congestion, etc.)
* deprivation rankings:

  * **SIMD (Scotland)**
  * **IMD (England)**

Each row represents a small geographic area (data zone / LSOA).

---

## Approach

At a high level:

* join co-benefit data with deprivation indices
* create quintiles / deciles of deprivation
* calculate correlations between deprivation rank and benefits
* visualize relationships with scatterplots and smoothed trends
* break results out by individual co-benefits

Spearman correlation is used since:

* the data is skewed
* relationships are not strictly linear

---

## What I found

Across both Scotland and England:

* There is a **positive correlation between deprivation rank and total co-benefits**
* Since higher rank = less deprived, this means:

  * **more affluent areas tend to receive greater total benefits**

Roughly:

* Scotland: ~0.40 correlation
* England: ~0.52 correlation

So the pattern exists in both, but is stronger in England.

A small share of Scottish neighborhoods (~1.5%) actually show negative total co-benefits.

---

## Co-benefit breakdown

Looking at individual benefit types:

* Some benefits are more evenly distributed
* Others are more skewed toward less deprived areas
* The overall pattern is not driven by a single variable

This suggests the distributional impact is fairly broad across categories.

---

## R vs Python

The same analysis was implemented in both:

* **R**: tidyverse, corrr, ggplot
* **Python**: pandas, scipy, seaborn

Results were very similar across both languages.

Main differences:

* R made correlation workflows slightly easier
* Python required a bit more manual setup, but was equally flexible

---

## Why this matters

This kind of analysis is useful for:

* understanding distributional impacts of climate policy
* identifying whether interventions are equitable
* avoiding unintended bias toward already advantaged areas

It’s a simple setup, but the pattern it reveals is important.

---

## Repo structure

```text
.
├── r/
│   └── analysis.R
├── python/
│   └── analysis.py
├── data/
│   └── (input files)
```

---

## How to run

### Python

```bash
conda activate classification
python analysis.py
```

### R

Run the script in RStudio:

```r
source("analysis.R")
```

---

## Takeaway

Even when policies are designed broadly, their benefits may not be evenly distributed.

In this case, climate co-benefits appear to skew toward less deprived areas, which is worth considering when designing or evaluating interventions.

---

## If I kept going

* look at geographic clustering of benefits
* incorporate population weighting
* explore causal drivers rather than just correlation
