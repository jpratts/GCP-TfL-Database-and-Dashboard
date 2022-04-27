# Our pipeline is automatically collecting data from various APIs and storing them in various tables.

## How can we turn this into a training dataset for our ML model? We can submit a SQL query on GCP to create a new table holding the information of interest.

```sql
INSERT INTO 
`PROJECT_NAME.tfl_data.ml_train`
(percentageOfBaseline, feels_day, clouds, uv, date, dow)

SELECT
ct.percentageOfBaseline,
wt.feels_day,
wt.clouds,
wt.uv,
wt.dt,
CAST(EXTRACT(DAYOFWEEK FROM (PARSE_DATE("%d/%m/%Y", wt.dt))) AS STRING ) AS dow

FROM
  `tfl-PROJECT_NAME.tfl_data.crowd_table` AS ct

INNER JOIN PROJECT_NAME.tfl_data.weather_table AS wt
ON ct.date = wt.dt;
```
