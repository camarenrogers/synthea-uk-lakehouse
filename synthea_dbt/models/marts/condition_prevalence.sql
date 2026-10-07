with conditions as (
    select * from {{ ref('stg_conditions') }}   
)

select
    description                         as condition,
    count(*)                            as total_occurrences,
    count(distinct patient_id)          as distinct_patients
from conditions
group by description
order by distinct_patients desc
