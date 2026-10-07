with source as (
    select * from {{ source('raw', 'encounters') }}
),

renamed as (
    select
        Id                as encounter_id,
        PATIENT           as patient_id,
        START             as start_time,
        STOP              as stop_time,
        ENCOUNTERCLASS    as encounter_class,
        DESCRIPTION       as description,
        REASONDESCRIPTION as reason_description
    from source
)

select * from renamed