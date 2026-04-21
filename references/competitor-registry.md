# Competitor Registry

Curated catalog of the Fourth competitive landscape for use by the `firecrawl-plugin` skills. Every URL in this file is verified as of 2026-04-20. If you discover a broken link, update this file before scraping.

Competitors are grouped by category:

- **all-in-one** - Restaurant-focused platforms spanning accounting, inventory, scheduling, HR, payroll
- **HCM** - Horizontal human capital management vendors with a hospitality vertical
- **point-solution** - Single-capability tools (usually scheduling-first) encroaching on workforce management

Every competitor entry lists the known public pages and the JSON schema from `extraction-schemas/` to use when scraping each page type.

---

## Restaurant365 (R365)

- **Category:** all-in-one
- **Primary URL:** https://www.restaurant365.com/

### Known pages

| Page | URL | Schema to use |
|------|-----|---------------|
| Pricing (gated) | https://www.restaurant365.com/pricing/ | pricing-page.json |
| Pricing plans | https://www.restaurant365.com/pricing-plans/ | pricing-page.json |
| Plan comparisons | https://www.restaurant365.com/plan-comparisons/ | pricing-page.json |
| Product - Operations | https://www.restaurant365.com/operations/ | feature-comparison.json |
| Product - Restaurant management | https://www.restaurant365.com/restaurant-management/ | feature-comparison.json |
| Product - Food cost software | https://www.restaurant365.com/restaurant-food-cost-software/ | feature-comparison.json |
| Case studies hub | https://www.restaurant365.com/resource-category/case-studies/ | (list page - follow links) |
| Case study - Villa Restaurant Group | https://www.restaurant365.com/case-studies/villa-restaurant-group-cuts-prime-cost-while-reducing-turnover-with-restaurant365/ | case-study.json |
| Case study - Food Fight Restaurant Group | https://www.restaurant365.com/case-studies/food-fight-restaurant-group/ | case-study.json |
| Case study - On-Call Restaurant Accounting | https://www.restaurant365.com/case-studies/on-call-restaurant-accounting-triples-client-base/ | case-study.json |
| Resource center / blog | https://www.restaurant365.com/resource-center/ | (navigation) |
| In the news / press | https://www.restaurant365.com/in-the-news/restaurant365-announces-winners-of-the-2025-customer-excellence-awards/ | press-release.json |
| About | https://www.restaurant365.com/about-us/ | (general) |

### Notes

Primary head-to-head competitor for Fourth in the restaurant vertical. Positions as "all-in-one" covering accounting + inventory + workforce + payroll. Claims 40,000+ restaurants on platform. Maps to Fourth's `vs-R365` KB doc. Pricing is "per location, per month" billed annually or quarterly - specific numbers are gated behind a demo form.

---

## 7shifts

- **Category:** point-solution (scheduling-first, expanding into payroll)
- **Primary URL:** https://www.7shifts.com/

### Known pages

| Page | URL | Schema to use |
|------|-----|---------------|
| Pricing | https://www.7shifts.com/pricing/ | pricing-page.json |
| Restaurant scheduling software | https://www.7shifts.com/restaurant-employee-scheduling-software/ | feature-comparison.json |
| Restaurant payroll software | https://www.7shifts.com/restaurant-payroll-software/ | feature-comparison.json |
| Compare: 7shifts vs When I Work | https://www.7shifts.com/compare/7shifts-vs-wheniwork/ | feature-comparison.json |
| Compare: 7shifts vs HotSchedules | https://www.7shifts.com/compare/7shifts-vs-hotschedules/ | feature-comparison.json |
| Customer stories hub | https://www.7shifts.com/customers/ | (list page) |
| Case studies hub | https://www.7shifts.com/resources/case-studies/ | (list page) |
| Case study - Burrito Boyz | https://www.7shifts.com/blog/burrito-boyz-case-study/ | case-study.json |
| Case study - Fresh Restaurants | https://www.7shifts.com/blog/fresh-restaurants-7shifts-case-study/ | case-study.json |
| Blog | https://www.7shifts.com/blog/ | (navigation) |
| AI info page | https://www.7shifts.com/ai-info/ | (general) |

### Notes

Claims 55,000+ quick and full-service restaurants. Free tier ($0 Comp plan) plus paid tiers. Payroll add-on starts at $39.99/mo/location plus $6/employee. Directly addressed in Fourth's `vs-point-solutions` KB doc. Aggressive comparison-page SEO strategy makes their compare URLs a goldmine for competitive positioning.

---

## Toast (Payroll and Team Management)

- **Category:** point-solution (POS-first, bundling payroll + scheduling)
- **Primary URL:** https://pos.toasttab.com/

### Known pages

| Page | URL | Schema to use |
|------|-----|---------------|
| Payroll and Team Management | https://pos.toasttab.com/products/payroll | feature-comparison.json |
| Restaurant employee scheduling | https://pos.toasttab.com/products/restaurant-employee-scheduling-software | feature-comparison.json |
| Restaurant employee tools | https://pos.toasttab.com/solutions/restaurant-employee-tools | feature-comparison.json |
| Pricing | requires sales contact (no public per-feature pricing page; see https://pos.toasttab.com/ main CTA) | pricing-page.json |
| Customer stories | https://pos.toasttab.com/customers | (list page) |
| Success stories blog | https://pos.toasttab.com/blog/on-the-line/success-stories | (navigation) |
| News / press | https://pos.toasttab.com/news/toast-introduces-payroll-and-team-management-for-restaurants | press-release.json |
| Blog (On the Line) | https://pos.toasttab.com/blog/on-the-line | (navigation) |

### Notes

POS is their wedge; payroll + scheduling is a bolt-on. Threat vector: existing Toast POS customers may adopt the Team Management add-on rather than seek a separate workforce vendor like Fourth. Toast partners with Sling for scheduling in some configurations.

---

## Deputy

- **Category:** point-solution (scheduling + time tracking)
- **Primary URL:** https://www.deputy.com/

### Known pages

| Page | URL | Schema to use |
|------|-----|---------------|
| Pricing | https://www.deputy.com/pricing | pricing-page.json |
| Features | https://www.deputy.com/features | feature-comparison.json |
| Scheduling software | https://www.deputy.com/features/scheduling-software | feature-comparison.json |
| Smart / AI scheduling | https://www.deputy.com/features/smart-scheduling | feature-comparison.json |
| Enterprise and multi-location | https://www.deputy.com/enterprise | feature-comparison.json |
| Customer stories (AU hub) | https://www.deputy.com/au/customers | (list page) |
| Case study - Mud Bay | https://www.deputy.com/au/customers/mud-bay | case-study.json |
| Case study - ACE Hardware | https://www.deputy.com/customers/ace-hardware | case-study.json |
| Case study - UNTUCKit | https://www.deputy.com/au/customers/untuckit | case-study.json |
| Blog | https://www.deputy.com/blog | (navigation) |
| Resource center | https://www.deputy.com/resources | (navigation) |

### Notes

As of October 2025, Deputy introduced Lite / Core / Pro plans. Add-ons include Analytics+, Messaging+, Deputy HR (AU/UK/US), and Deputy Payroll (AU only). Multi-region (AU, UK, US). Strong in hospitality + retail verticals. Covered in `vs-point-solutions`.

---

## When I Work

- **Category:** point-solution (scheduling-first)
- **Primary URL:** https://wheniwork.com/

### Known pages

| Page | URL | Schema to use |
|------|-----|---------------|
| Pricing | https://wheniwork.com/pricing | pricing-page.json |
| Customer stories | https://wheniwork.com/customer-stories | (list page) |
| Compare: When I Work vs Homebase | https://wheniwork.com/blog/homebase-vs-wheniwork | feature-comparison.json |
| Compare: 7shifts vs When I Work | https://wheniwork.com/blog/7shifts-vs-wheniwork | feature-comparison.json |
| Compare: Sling vs When I Work | https://wheniwork.com/blog/getsling-vs-wheniwork | feature-comparison.json |
| Help / billing FAQ | https://help.wheniwork.com/articles/frequently-asked-account-billing-questions/ | (reference) |
| Blog | https://wheniwork.com/blog | (navigation) |

### Notes

Starts at $2.50/user/month (single-location) and $5/user/month (multi-location). 14-day free trial, no credit card required. Generalist scheduling tool with hospitality as one of many verticals. Lower-cost threat to Fourth at the SMB end.

---

## Homebase

- **Category:** point-solution (scheduling + payroll for SMB)
- **Primary URL:** https://www.joinhomebase.com/

### Known pages

| Page | URL | Schema to use |
|------|-----|---------------|
| Pricing | https://www.joinhomebase.com/pricing | pricing-page.json |
| Pricing (alt) | https://joinhomebase.com/homebase-prices/ | pricing-page.json |
| Payroll | https://www.joinhomebase.com/payroll | feature-comparison.json |
| Free scheduling landing | https://www.joinhomebase.com/free-scheduling | feature-comparison.json |
| Compare landing | https://www.joinhomebase.com/compare | feature-comparison.json |
| Compare: Homebase vs Square | https://www.joinhomebase.com/compare/homebase-vs-square | feature-comparison.json |
| Payroll comparison | https://www.joinhomebase.com/compare-payroll | feature-comparison.json |
| Customer stories hub | https://www.joinhomebase.com/customers | (list page) |
| Case study - Brooklyn Tea | https://www.joinhomebase.com/customers/brooklyn-tea-homebase-case-study-scheduling-communications | case-study.json |
| Blog | https://www.joinhomebase.com/blog | (navigation) |

### Notes

Free Basic plan up to 10 employees at one location. Paid tiers: Essentials, Plus, All-in-One. Payroll add-on is $39/mo base plus $6/employee/mo. Heaviest in SMB restaurants, retail, and services. Covered in `vs-point-solutions`.

---

## Push Operations

- **Category:** all-in-one (narrower - payroll + scheduling + time)
- **Primary URL:** https://www.pushoperations.com/

### Known pages

| Page | URL | Schema to use |
|------|-----|---------------|
| Homepage | https://www.pushoperations.com/ | feature-comparison.json |
| Pricing | requires sales contact (no public pricing page) | pricing-page.json |
| Payroll | https://www.pushoperations.com/solutions/payroll | feature-comparison.json |
| Scheduling | https://www.pushoperations.com/solutions/scheduling | feature-comparison.json |
| Time tracking | https://www.pushoperations.com/solutions/time-tracking | feature-comparison.json |
| Hiring and onboarding | https://www.pushoperations.com/solutions/hiring-and-onboarding | feature-comparison.json |
| Restaurant industry page | https://www.pushoperations.com/industry/restaurants | feature-comparison.json |
| Case studies hub | https://www.pushoperations.com/resource-categories/case-studies | (list page) |
| FAQ | https://www.pushoperations.com/faq | (reference) |
| About | https://www.pushoperations.com/company | (general) |

### Notes

Canada-based, expanding in US. Payroll-first positioning with "run payroll in 10 minutes." Restaurant vertical focus. Smaller threat than R365 but relevant in Canada + North American SMB restaurant segment. Verify pricing page before use - no public pricing URL confirmed.

---

## Paycom

- **Category:** HCM
- **Primary URL:** https://www.paycom.com/

### Known pages

| Page | URL | Schema to use |
|------|-----|---------------|
| Software overview | https://www.paycom.com/software/ | feature-comparison.json |
| Payroll software | https://www.paycom.com/software/payroll/ | feature-comparison.json |
| HR management software | https://www.paycom.com/software/hr-management/ | feature-comparison.json |
| Employee self-service | https://www.paycom.com/software/employee-self-service/ | feature-comparison.json |
| Small business | https://www.paycom.com/who-we-help/small-business/ | feature-comparison.json |
| Mid-size business | https://www.paycom.com/who-we-help/medium-business/ | feature-comparison.json |
| Enterprise HRIS | https://www.paycom.com/who-we-help/large-business/ | feature-comparison.json |
| Pricing | requires sales contact (no public per-seat pricing) | pricing-page.json |
| Case studies hub | https://www.paycom.com/resources/case-studies/ | (list page) |
| Food franchise case study (PDF) | https://www.paycom.com/PDF/case-studies/Paycom%20WOTC%20Case%20Study.pdf | case-study.json |
| Reviews | https://www.paycom.com/about/reviews/ | (general) |
| Blog / resources | https://www.paycom.com/resources/blog/ | (navigation) |

### Notes

Horizontal HCM player. Heavy marketing emphasis on Beti (self-service payroll) and IWant (AI search). Threat in multi-vertical employers where hospitality is one segment - not purpose-built for restaurants. Covered in `vs-HCM`.

---

## UKG (Ultimate Kronos Group)

- **Category:** HCM (with hospitality vertical)
- **Primary URL:** https://www.ukg.com/

### Known pages

| Page | URL | Schema to use |
|------|-----|---------------|
| Homepage | https://www.ukg.com/ | (general) |
| UKG Pro HCM | https://www.ukg.com/products/ukg-pro | feature-comparison.json |
| UKG Pro Workforce Management | https://www.ukg.com/products/ukg-pro-workforce-management | feature-comparison.json |
| Workforce Management | https://www.ukg.com/products/workforce-management | feature-comparison.json |
| Hospitality industry solution | https://www.ukg.com/industry-solutions/hospitality | feature-comparison.json |
| Hospitality + food service | https://www.ukg.com/industry-solutions/hospitality-food-service | feature-comparison.json |
| Pricing | requires sales contact (no public pricing) | pricing-page.json |
| Customer stories hub | https://www.ukg.com/customers | (list page) |
| Case study - GPS Hospitality | https://www.ukg.com/customer-stories/gps-hospitality | case-study.json |
| Case study - Aimbridge Hospitality | https://www.ukg.com/customers/aimbridge-hospitality | case-study.json |
| Newsroom - Aimbridge announcement | https://www.ukg.com/company/newsroom/hospitality-giant-revolutionizes-frontline-worker-experience-ukg | press-release.json |
| Hospitality blog | https://www.ukg.com/blog/hr-leaders/supporting-hospitality-workforce-key-learnings-and-insights-employee-retention-engagement-and-success-our-customers | (navigation) |

### Notes

Biggest HCM threat in upmarket hospitality. Claims 77% of Fortune 1000 hospitality organizations use UKG. Flagship customer Aimbridge Hospitality. Fourth competes most directly on the mid-market / chain-restaurant side where UKG feels too enterprise. Covered in `vs-HCM`.

---

## Paylocity

- **Category:** HCM
- **Primary URL:** https://www.paylocity.com/

### Known pages

| Page | URL | Schema to use |
|------|-----|---------------|
| Homepage | https://www.paylocity.com/ | (general) |
| HR / HCM product | https://www.paylocity.com/products/hr/ | feature-comparison.json |
| Integrations | https://www.paylocity.com/products/capabilities/integrations/ | feature-comparison.json |
| Small business payroll | https://www.paylocity.com/who-we-serve/company-size/small/payroll/ | feature-comparison.json |
| Pricing | https://www.paylocity.com/pricing/ (per-employee model, no public dollar amounts) | pricing-page.json |
| Case studies hub | https://www.paylocity.com/why-paylocity/case-studies/ | (list page) |
| Case study - Oliver Winery | https://www.paylocity.com/why-paylocity/case-studies/how-oliver-winery-transformed-hr-operations-with-paylocity/ | case-study.json |
| Case study - Stonewall Kitchen | https://www.paylocity.com/resources/case-studies/case-study-modernizing-hr-to-streamline-seasonal-hiring/ | case-study.json |
| Resource library | https://www.paylocity.com/resources/ | (navigation) |

### Notes

Mid-market HCM, per-employee-per-month pricing (no per-payroll-run fees). Less hospitality-focused than UKG but picks up mid-size operators that want a horizontal platform. Covered in `vs-HCM`.

---

## ADP Workforce Now

- **Category:** HCM
- **Primary URL:** https://www.adp.com/

### Known pages

| Page | URL | Schema to use |
|------|-----|---------------|
| Workforce Now overview | https://www.adp.com/what-we-offer/products/adp-workforce-now.aspx | feature-comparison.json |
| Workforce Now capabilities | https://www.adp.com/what-we-offer/products/adp-workforce-now/capabilities.aspx | feature-comparison.json |
| Workforce Now payroll | https://www.adp.com/what-we-offer/products/adp-workforce-now/payroll.aspx | feature-comparison.json |
| Options and pricing (gated) | https://www.adp.com/what-we-offer/products/adp-workforce-now/compare-options.aspx | pricing-page.json |
| Package comparison PDF | https://www.adp.com/-/media/pdf/adp-wfn-compare-packages.pdf | pricing-page.json |
| Client success stories | https://www.adp.com/resources/what-others-say/testimonials/c/client-success-stories.aspx | (list page) |
| Time and Labor success story | https://www.adp.com/resources/what-others-say/testimonials/p/pia-saks-melanie-wiegert-hannah-hill.aspx | case-study.json |
| ReThink Q client stories | https://rethinkq.adp.com/client-stories/ | (list page) |
| Login | https://www.adp.com/logins/adp-workforce-now.aspx | (non-marketing) |

### Notes

The 800-lb gorilla of payroll. Packages: base payroll+HR, Select (adds benefits), Plus (adds time+attendance). Pricing gated behind 1-888 form. Fourth does not usually compete on price - competes on hospitality-specific depth. Covered in `vs-HCM`.

---

## How to add a competitor

To add a new competitor to this registry:

1. **Verify every URL manually** by visiting it in a browser. If a page requires login or redirects, mark it `requires sales contact` or `requires registration` rather than linking to a 404.
2. **Copy the H2 template** from an existing entry. Fill in: category, primary URL, known pages table, notes section.
3. **Tag each known page with a schema** from `extraction-schemas/` (pricing-page.json, case-study.json, feature-comparison.json, press-release.json). Navigation / general pages can be left unschemed.
4. **Run a validation scrape** on at least one page with the assigned schema before committing: `firecrawl scrape <url> --schema-file references/extraction-schemas/<schema>.json`. If extraction fails, either fix the schema or downgrade the page to a navigation-only entry.

When a competitor goes out of business, is acquired, or pivots away from hospitality, move them to an `archive/` section at the bottom of this file rather than deleting - historical URLs are still useful for comparison against current reality.
