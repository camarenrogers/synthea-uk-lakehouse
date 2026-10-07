with source as (
    select * from {{ source('raw', 'conditions') }}
),

renamed as (
    select
        PATIENT      as patient_id,
        ENCOUNTER    as encounter_id,
        START        as start_date,
        STOP         as stop_date,
        CODE         as condition_code,
        DESCRIPTION  as description
    from source
)

select * from renamed