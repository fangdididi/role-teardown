Subject: Senior Data Engineer, Delivery Intelligence: late depot scans

Hi Parcelwise team,

Your posting says depot scans land up to 6 hours late and the ETA model trains on incomplete days. I have fixed a smaller version of that problem. At Rotafresh, courier GPS pings arrive up to 2 hours late; with Kafka event-time windows and a 3-hour watermark, our next-day delivery reports went from being revised 1 day in 5 to not at all for 9 months.

The rest of the role is familiar ground: I moved 14 cron jobs to Airflow, put tests and alerting on 120 dbt models, and mentor a junior engineer through code review.

In my first 60 days I would map how late each depot's scans really arrive, set a watermark per depot, and add one Airflow check that blocks training on an incomplete day.

My stack gap is BigQuery; I work in Snowflake today and am doing the Google Cloud labs now. I would need visa sponsorship, which I see you offer.

Alex Moreno
