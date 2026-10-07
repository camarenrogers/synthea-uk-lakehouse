with source as (
    select * from {{ source('raw', 'patients') }}
),

renamed as (
    select
        Id          as patient_id,
        BIRTHDATE   as birth_date,
        DEATHDATE   as death_date,
        GENDER      as gender,
        RACE        as race,
        ETHNICITY   as ethnicity,
        CITY        as city,
        STATE       as state,
        COUNTY      as county
    from source
)

select * from renamed
