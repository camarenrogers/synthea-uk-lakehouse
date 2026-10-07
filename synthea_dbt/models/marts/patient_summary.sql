with patients as (
    select * from {{ ref('stg_patients') }}
),

encounters as (
    select * from {{ ref('stg_encounters') }}
),

encounter_counts as (
    select
        patient_id,
        count(*)                           as total_encounters,
        count(distinct encounter_class)    as distinct_encounter_types,
        min(start_time)                    as first_encounter,
        max(start_time)                    as last_encounter
    from encounters
    group by patient_id)

    select
        p.patient_id,
        p.gender,
        p.race,
        p.ethnicity,
        p.city,
        p.county,
        p.birth_date,
        date_diff('year', cast(p.birth_date as date), current_date) as age,
        coalesce(ec.total_encounters, 0) as total_encounters,
        coalesce(ec.distinct_encounter_types, 0) as distinct_encounter_types,
        ec.first_encounter,
        ec.last_encounter
    from patients p
    left join encounter_counts ec on p.patient_id = ec.patient_id