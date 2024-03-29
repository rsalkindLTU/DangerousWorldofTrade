-- This file contains all the schema definitions for each of the required files.

-- There are 4 main tables:
--      listings
--      stations
--      commodity_reference
--      systems

-- We assume that the table is just getting created for the first time, from scratch
-- For each table, the schema is listed below:

-- listings:
-- LISTINGS TABLE START
CREATE TABLE listings (
    id integer PRIMARY KEY,
    station_id integer,
    commodity_id integer,
    supply integer,
    supply_bracket integer,
    buy_price integer,
    sell_price integer,
    demand integer,
    demand_bracket integer,
    collected_at integer
);
-- LISTINGS TABLE END

-- Stations
-- STATIONS TABLE START
CREATE TABLE stations (
    id integer PRIMARY KEY, -- REQUIRED
    name text, -- REQUIRED
    system_id integer, -- REQUIRED
    --updated_at integer,
    max_landing_pad_size text, -- REQUIRED
    --distance_to_star integer,
    --government_id integer,
    --government text,
    --allegince_id integer,
    --allegince text,
    --states blob,
    --type_id integer,
    --'type' text,
    has_blackmarket integer, -- Is bool -- REQUIRED
    has_market integer, -- Is bool -- REQUIRED
    has_refuel integer, -- Is bool -- REQUIRED
    has_repair integer, -- Is bool -- REQUIRED
    has_rearm integer, -- Is bool -- REQUIRED
    has_outfitting integer, -- Is bool -- REQUIRED
    has_shipyard integer, -- Is bool -- REQUIRED
    has_docking integer, -- Is bool -- REQUIRED
    has_commodities integer -- Is bool -- REQUIRED
    --import_commodities blob,
    --export_commodities blob,
    --prohibited_commodities blob,
    --economies blob,
    --shipyard_updated_at integer,
    --outfitting_updated_at integer,
    --market_updated_at integer,
    --is_planetary integer, -- Is bool
    --selling_ships blob,
    --selling_modules blob,
    --settlement_size_id integer,
    --settlement_size text,
    --settlement_security_id integer,
    --settlement_security text,
    --body_id integer,
    --controlling_minor_faction_id integer
);
-- STATIONS TABLE END

-- Systems (Larger file (3gb) but less rows than the last one holy)
-- SYSTEMS TABLE START
CREATE TABLE systems (
    id integer PRIMARY KEY, -- REQUIRED
    edsm_id integer, -- REQUIRED
    name text, -- REQUIRED
    x real, -- REQUIRED
    y real, -- REQUIRED
    z real, -- REQUIRED
    --population integer,
    is_populated integer, -- Is bool??? -- REQUIRED
    --government_id integer,
    --government text,
    --allegiance_id integer,
    --allegiance text,
    --security_id integer,
    --security text,
    --primary_economy_id integer,
    --primary_economy text,
    --'power' text,
    --power_state text,
    --power_state_id integer,
    needs_permit integer -- Is bool -- REQUIRED
    --updated_at integer,
    --simbad_ref text,
    --controlling_minor_faction_id integer,
    --controlling_minor_faction text,
    --reserve_type_id integer,
    --reserve_type text
);
-- SYSTEMS TABLE END

-- Commodity reference
-- COMMODITIES TABLE START
CREATE TABLE commodities (
    id integer PRIMARY KEY, -- REQUIRED
    name text, -- REQUIRED
    --category_id integer,
    average_price integer, -- REQUIRED
    is_rare integer -- Is bool -- REQUIRED
    --max_buy_price integer,
    --max_sell_price integer,
    --min_buy_price integer,
    --min_sell_price integer,
    --buy_price_lower_average integer, -- Is bool
    --sell_price_upper_average integer,
    --is_non_marketable integer, -- Is Bool
    --ed_id integer,
    --category blob
);
-- COMMODITIES TABLE END
