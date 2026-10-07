with source as (
    select * from {{ source('raw', 'observations') }}
),

renamed as (
    select
        PATIENT      as patient_id,
        ENCOUNTER    as encounter_id,
        DATE         as observation_date,
        CODE         as observation_code,
        DESCRIPTION  as description,
        VALUE        as value,
        UNITS        as units,
        TYPE         as observation_type
    from source
)

select * from renamed