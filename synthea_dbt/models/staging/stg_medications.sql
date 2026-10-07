with source as (
    select * from {{ source('raw', 'medications') }}
),

renamed as (
    select
        PATIENT      as patient_id,
        ENCOUNTER    as encounter_id,
        START        as start_date,
        STOP         as stop_date,
        CODE         as medication_code,
        DESCRIPTION  as description,
        REASONDESCRIPTION as reason_description
    from source
)

select * from renamed