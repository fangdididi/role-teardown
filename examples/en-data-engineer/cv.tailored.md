# Alex Moreno
Senior Data Engineer · Lisbon (open to Rotterdam hybrid; needs visa sponsorship) · alex.moreno@example.com

## Summary
Data engineer, 6 years building production data pipelines in Python and SQL for delivery businesses. At Rotafresh I made courier GPS events that arrive up to 2 hours late count toward the right delivery day, using Kafka event-time windows, and put data quality tests with alerting on 120 dbt models.

## Experience

### Data Engineer, Rotafresh (meal-kit delivery), Lisbon · 2021–present
- Rebuilt the order-to-doorstep pipeline in Python and SQL; nightly run time fell from 3h10 to 40 min, so ETA reports were ready before the 7:00 dispatch meeting.
- Handled late-arriving courier GPS pings (up to 2 h late) with Kafka event-time windows and a 3 h watermark; next-day reports: revised 1 day in 5 before, never in 9 months since.
- Added data quality tests and Slack alerting to 120 dbt models and ran the incident review after each failure; issues caught before business hours rose from about 30% to 85%.
- Backfilled 18 months of delivery history after a schema change, in 6 partitioned runs with row-count checks, with zero dashboard downtime.
- Mentored a junior engineer from first commit to solo on-call in 5 months; reviewed about 15 of her dbt and Python pull requests a month.

### Junior Data Engineer, Banco Atlantico, Porto · 2019–2021
- Migrated 14 cron-based ETL jobs on PostgreSQL to Apache Airflow 2 with retries and SLAs; failed overnight runs fell from about 6 a month to 1.

## Skills
Python, SQL, dbt, Apache Airflow, Kafka (event-time windows, watermarks), PostgreSQL, Snowflake, Docker, Git. Learning: BigQuery and Google Cloud Platform (GCP), currently in the Google Cloud data engineering course labs.

## Education
BSc Computer Engineering, Universidade do Minho, 2019

## Languages
English (professional, all work documentation since 2021), Portuguese (native)
