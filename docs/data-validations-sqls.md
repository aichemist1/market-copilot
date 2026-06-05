1. Overall job status
- This tells you how many normalization jobs are completed, queued, failed, etc.

select status, count(*)
from normalization_jobs
group by status
order by status;


2. Latest ingestion run summary

- This tells you what the run discovered and how much it thinks it normalized/published so far.


select id,
       status,
       files_discovered_count,
       files_downloaded_count,
       records_normalized_count,
       records_published_count,
       started_at,
       completed_at
from ingestion_runs
order by started_at desc
limit 5;


3. Product rows already persisted

- This shows how much data has already landed in the product tables.


select count(*) from congressional_filings;
select count(*) from congressional_transactions;

4. Optional progress view

- A quick one-line view of “done vs remaining”:

select
  sum(case when status = 'completed' then 1 else 0 end) as completed,
  sum(case when status = 'queued' then 1 else 0 end) as queued,
  sum(case when status = 'failed' then 1 else 0 end) as failed,
  count(*) as total
from normalization_jobs;


