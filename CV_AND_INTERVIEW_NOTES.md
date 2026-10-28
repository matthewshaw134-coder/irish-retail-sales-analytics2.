# How to present this project

## CV: Projects section (choose 3–4 bullets)

**Irish Retail Sales Analytics Dashboard** | Python, SQL (SQLite), pandas, matplotlib, JavaScript | [GitHub link]

- Built an end-to-end analytics pipeline for a simulated Irish retailer with 12 stores and an online shop, processing 115,000 orders and 210,000 sales lines covering 2024–2025.
- Cleaned and validated raw point-of-sale data in Python. Resolved 4,000+ data-quality issues (duplicates, inconsistent text, missing and invalid values) and logged each fix for audit.
- Designed a relational SQLite database (star schema, keys, constraints, indexes) and wrote 11 SQL analysis queries using CTEs, joins and window functions (LAG, RANK, NTILE).
- Segmented 17,000 loyalty customers using RFM analysis in SQL. Found that the top 20% generate 39% of sales and identified €1.0m of "at-risk" customer spend for win-back campaigns.
- Built an interactive, mobile-friendly dashboard (KPIs, trends, store league table, footfall heatmap) and turned the findings into recommendations on online investment and staff rostering.

## Short version (one line, for the Skills or Summary section)

Built an end-to-end Irish retail sales dashboard using Python, SQL and JavaScript (210k sales records), covering data cleaning, database design, analysis and business recommendations.

## Interview talking points

**"Tell me about this project."**
I wanted to show the full analyst workflow, not just a chart. I generated realistic Irish retail data with deliberate data-quality problems, cleaned it in Python, loaded it into a SQL database I designed, analysed it with SQL, and presented the results as a dashboard with recommendations.

**"Why synthetic data?"**
Real retail data is confidential. Generating it let me build in the patterns I wanted to analyse, like Black Friday, Christmas, a store refit and online growth, and then check that my analysis actually found them.

**"What was the most interesting finding?"**
Liffey Valley was the only store in decline (−10%), and that alone pulled Dublin's growth down to 3%. The headline regional number hid a single-store problem, which is why it's worth drilling down.

**"What would you do next?"**
Forecast 2026 sales by month, rebuild the dashboard in Power BI, and add a stock or inventory table to analyse sell-through.

**Admin angle (for admin and public-sector roles)**
The same skills apply to admin work: cleaning messy records, keeping data accurate and GDPR-aware, building reports in Excel or SQL, and explaining numbers clearly to non-technical colleagues.

## Putting it online (free)

1. Create a GitHub account and a new public repository called `irish-retail-sales-analytics`.
2. Upload the contents of this folder. The README displays on the front page automatically.
3. To get a live dashboard link, go to **Settings → Pages**, choose your main branch and `/ (root)`, then save. Your dashboard will be at
   `https://<your-username>.github.io/irish-retail-sales-analytics/dashboard/`
4. Put that link on your CV and LinkedIn (Featured section).
5. Replace "(add your repo link)" in `dashboard/template.html`, then re-run `python src/build_dashboard.py`.
