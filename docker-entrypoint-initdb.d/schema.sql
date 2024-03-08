
-- Connect to the database
\c leads_db;

-- Tables definitions

-- Create table `buyer`
CREATE TABLE public.buyer (
	slug VARCHAR(50) NOT NULL, 
	name VARCHAR(50) NOT NULL, 
	PRIMARY KEY (slug), 
	UNIQUE (name)
);

-- Create table `buyer_tier_dealer_coverage`
CREATE TABLE public.buyer_tier_dealer_coverage (
	buyer_tier_slug VARCHAR(50) NOT NULL, 
	dealer_code VARCHAR(50) NOT NULL, 
	zipcode VARCHAR(255) NOT NULL, 
	distance INTEGER, 
	PRIMARY KEY (buyer_tier_slug, dealer_code, zipcode)
);

-- Create table `country`
CREATE TABLE public.country (
	slug VARCHAR(50) NOT NULL, 
	name VARCHAR(50) NOT NULL, 
	abbr VARCHAR(50) NOT NULL, 
	PRIMARY KEY (slug), 
	UNIQUE (name), 
	UNIQUE (abbr)
);

-- Create table `make`
CREATE TABLE public.make (
	slug VARCHAR(50) NOT NULL, 
	name VARCHAR(50) NOT NULL, 
	PRIMARY KEY (slug), 
	UNIQUE (name)
);

-- Create table `year`
CREATE TABLE public.year (
	slug VARCHAR(50) NOT NULL, 
	name VARCHAR(50) NOT NULL, 
	PRIMARY KEY (slug), 
	UNIQUE (name)
);

-- Create table `buyer_make`
CREATE TABLE public.buyer_make (
	buyer_slug VARCHAR(50) NOT NULL, 
	make_slug VARCHAR(50) NOT NULL, 
	PRIMARY KEY (buyer_slug, make_slug), 
	FOREIGN KEY(buyer_slug) REFERENCES public.buyer (slug), 
	FOREIGN KEY(make_slug) REFERENCES public.make (slug)
);

-- Create table `buyer_tier`
CREATE TABLE public.buyer_tier (
	buyer_slug VARCHAR(50) NOT NULL, 
	slug VARCHAR(50) NOT NULL, 
	name VARCHAR(50) NOT NULL, 
	PRIMARY KEY (buyer_slug, slug), 
	UNIQUE (buyer_slug, name), 
	FOREIGN KEY(buyer_slug) REFERENCES public.buyer (slug)
);

-- Create table `buyer_year`
CREATE TABLE public.buyer_year (
	buyer_slug VARCHAR(50) NOT NULL, 
	year_slug VARCHAR(50) NOT NULL, 
	PRIMARY KEY (buyer_slug, year_slug), 
	FOREIGN KEY(buyer_slug) REFERENCES public.buyer (slug), 
	FOREIGN KEY(year_slug) REFERENCES public.year (slug)
);

-- Create table `country_state`
CREATE TABLE public.country_state (
	country_slug VARCHAR(50) NOT NULL, 
	slug VARCHAR(50) NOT NULL, 
	name VARCHAR(50) NOT NULL, 
	abbr VARCHAR(50) NOT NULL, 
	PRIMARY KEY (country_slug, slug), 
	UNIQUE (country_slug, name), 
	UNIQUE (country_slug, abbr), 
	FOREIGN KEY(country_slug) REFERENCES public.country (slug)
);

-- Create table `make_model`
CREATE TABLE public.make_model (
	make_slug VARCHAR(50) NOT NULL, 
	slug VARCHAR(50) NOT NULL, 
	name VARCHAR(50) NOT NULL, 
	PRIMARY KEY (make_slug, slug), 
	UNIQUE (make_slug, name), 
	FOREIGN KEY(make_slug) REFERENCES public.make (slug)
);

-- Create table `make_year`
CREATE TABLE public.make_year (
	make_slug VARCHAR(50) NOT NULL, 
	year_slug VARCHAR(50) NOT NULL, 
	PRIMARY KEY (make_slug, year_slug), 
	FOREIGN KEY(make_slug) REFERENCES public.make (slug), 
	FOREIGN KEY(year_slug) REFERENCES public.year (slug)
);

-- Create table `buyer_dealer`
CREATE TABLE public.buyer_dealer (
	buyer_slug VARCHAR(50) NOT NULL, 
	code VARCHAR(50) NOT NULL, 
	name VARCHAR(255), 
	address VARCHAR(255), 
	city VARCHAR(255), 
	state VARCHAR(50), 
	zipcode VARCHAR(255), 
	country_slug VARCHAR(50), 
	phone VARCHAR(255), 
	PRIMARY KEY (buyer_slug, code), 
	UNIQUE (buyer_slug, name, address, city, state, zipcode), 
	FOREIGN KEY(country_slug, state) REFERENCES public.country_state (country_slug, abbr), 
	FOREIGN KEY(buyer_slug) REFERENCES public.buyer (slug)
);

-- Create table `buyer_make_model`
CREATE TABLE public.buyer_make_model (
	buyer_slug VARCHAR(50) NOT NULL, 
	make_slug VARCHAR(50) NOT NULL, 
	model_slug VARCHAR(50) NOT NULL, 
	PRIMARY KEY (buyer_slug, make_slug, model_slug), 
	FOREIGN KEY(buyer_slug, make_slug) REFERENCES public.buyer_make (buyer_slug, make_slug), 
	FOREIGN KEY(make_slug, model_slug) REFERENCES public.make_model (make_slug, slug), 
	FOREIGN KEY(buyer_slug) REFERENCES public.buyer (slug)
);

-- Create table `buyer_make_year`
CREATE TABLE public.buyer_make_year (
	buyer_slug VARCHAR(50) NOT NULL, 
	make_slug VARCHAR(50) NOT NULL, 
	year_slug VARCHAR(50) NOT NULL, 
	PRIMARY KEY (buyer_slug, make_slug, year_slug), 
	FOREIGN KEY(buyer_slug, make_slug) REFERENCES public.buyer_make (buyer_slug, make_slug), 
	FOREIGN KEY(make_slug, year_slug) REFERENCES public.make_year (make_slug, year_slug)
);

-- Create table `buyer_tier_make`
CREATE TABLE public.buyer_tier_make (
	buyer_slug VARCHAR(50) NOT NULL, 
	tier_slug VARCHAR(50) NOT NULL, 
	make_slug VARCHAR(50) NOT NULL, 
	PRIMARY KEY (buyer_slug, tier_slug, make_slug), 
	FOREIGN KEY(buyer_slug, tier_slug) REFERENCES public.buyer_tier (buyer_slug, slug), 
	FOREIGN KEY(buyer_slug, make_slug) REFERENCES public.buyer_make (buyer_slug, make_slug)
);

-- Create table `buyer_tier_year`
CREATE TABLE public.buyer_tier_year (
	buyer_slug VARCHAR(50) NOT NULL, 
	tier_slug VARCHAR(50) NOT NULL, 
	year_slug VARCHAR(50) NOT NULL, 
	PRIMARY KEY (buyer_slug, tier_slug, year_slug), 
	FOREIGN KEY(buyer_slug, tier_slug) REFERENCES public.buyer_tier (buyer_slug, slug), 
	FOREIGN KEY(buyer_slug, year_slug) REFERENCES public.buyer_year (buyer_slug, year_slug)
);

-- Create table `legacy_buyer_tier`
CREATE TABLE public.legacy_buyer_tier (
	buyer_slug VARCHAR(50) NOT NULL, 
	buyer_tier_slug VARCHAR(50) NOT NULL, 
	legacy_id INTEGER NOT NULL, 
	legacy_name VARCHAR(50) NOT NULL, 
	PRIMARY KEY (buyer_slug, buyer_tier_slug), 
	UNIQUE (legacy_id), 
	UNIQUE (legacy_name), 
	FOREIGN KEY(buyer_slug, buyer_tier_slug) REFERENCES public.buyer_tier (buyer_slug, slug)
);

-- Create table `make_model_year`
CREATE TABLE public.make_model_year (
	make_slug VARCHAR(50) NOT NULL, 
	model_slug VARCHAR(50) NOT NULL, 
	year_slug VARCHAR(50) NOT NULL, 
	PRIMARY KEY (make_slug, model_slug, year_slug), 
	FOREIGN KEY(make_slug, model_slug) REFERENCES public.make_model (make_slug, slug), 
	FOREIGN KEY(make_slug, year_slug) REFERENCES public.make_year (make_slug, year_slug)
);

-- Create table `buyer_dealer_make`
CREATE TABLE public.buyer_dealer_make (
	buyer_slug VARCHAR(50) NOT NULL, 
	dealer_code VARCHAR(50) NOT NULL, 
	make_slug VARCHAR(50) NOT NULL, 
	PRIMARY KEY (buyer_slug, dealer_code, make_slug), 
	FOREIGN KEY(buyer_slug, dealer_code) REFERENCES public.buyer_dealer (buyer_slug, code), 
	FOREIGN KEY(buyer_slug, make_slug) REFERENCES public.buyer_make (buyer_slug, make_slug)
);

-- Create table `buyer_dealer_year`
CREATE TABLE public.buyer_dealer_year (
	buyer_slug VARCHAR(50) NOT NULL, 
	dealer_code VARCHAR(50) NOT NULL, 
	year_slug VARCHAR(50) NOT NULL, 
	PRIMARY KEY (buyer_slug, dealer_code, year_slug), 
	FOREIGN KEY(buyer_slug, dealer_code) REFERENCES public.buyer_dealer (buyer_slug, code), 
	FOREIGN KEY(buyer_slug, year_slug) REFERENCES public.buyer_year (buyer_slug, year_slug)
);

-- Create table `buyer_make_model_year`
CREATE TABLE public.buyer_make_model_year (
	buyer_slug VARCHAR(50) NOT NULL, 
	make_slug VARCHAR(50) NOT NULL, 
	model_slug VARCHAR(50) NOT NULL, 
	year_slug VARCHAR(50) NOT NULL, 
	PRIMARY KEY (buyer_slug, make_slug, model_slug, year_slug), 
	FOREIGN KEY(buyer_slug, make_slug, model_slug) REFERENCES public.buyer_make_model (buyer_slug, make_slug, model_slug), 
	FOREIGN KEY(buyer_slug, make_slug, year_slug) REFERENCES public.buyer_make_year (buyer_slug, make_slug, year_slug)
);

-- Create table `buyer_tier_make_model`
CREATE TABLE public.buyer_tier_make_model (
	buyer_slug VARCHAR(50) NOT NULL, 
	tier_slug VARCHAR(50) NOT NULL, 
	make_slug VARCHAR(50) NOT NULL, 
	model_slug VARCHAR(50) NOT NULL, 
	PRIMARY KEY (buyer_slug, tier_slug, make_slug, model_slug), 
	FOREIGN KEY(buyer_slug, tier_slug, make_slug) REFERENCES public.buyer_tier_make (buyer_slug, tier_slug, make_slug), 
	FOREIGN KEY(buyer_slug, make_slug, model_slug) REFERENCES public.buyer_make_model (buyer_slug, make_slug, model_slug)
);

-- Create table `buyer_tier_make_year`
CREATE TABLE public.buyer_tier_make_year (
	buyer_slug VARCHAR(50) NOT NULL, 
	tier_slug VARCHAR(50) NOT NULL, 
	make_slug VARCHAR(50) NOT NULL, 
	year_slug VARCHAR(50) NOT NULL, 
	PRIMARY KEY (buyer_slug, tier_slug, make_slug, year_slug), 
	FOREIGN KEY(buyer_slug, tier_slug, make_slug) REFERENCES public.buyer_tier_make (buyer_slug, tier_slug, make_slug), 
	FOREIGN KEY(buyer_slug, tier_slug, year_slug) REFERENCES public.buyer_tier_year (buyer_slug, tier_slug, year_slug)
);

-- Create table `buyer_dealer_make_model`
CREATE TABLE public.buyer_dealer_make_model (
	buyer_slug VARCHAR(50) NOT NULL, 
	dealer_code VARCHAR(50) NOT NULL, 
	make_slug VARCHAR(50) NOT NULL, 
	model_slug VARCHAR(50) NOT NULL, 
	PRIMARY KEY (buyer_slug, dealer_code, make_slug, model_slug), 
	FOREIGN KEY(buyer_slug, dealer_code, make_slug) REFERENCES public.buyer_dealer_make (buyer_slug, dealer_code, make_slug), 
	FOREIGN KEY(buyer_slug, make_slug, model_slug) REFERENCES public.buyer_make_model (buyer_slug, make_slug, model_slug)
);

-- Create table `buyer_dealer_make_year`
CREATE TABLE public.buyer_dealer_make_year (
	buyer_slug VARCHAR(50) NOT NULL, 
	dealer_code VARCHAR(50) NOT NULL, 
	make_slug VARCHAR(50) NOT NULL, 
	year_slug VARCHAR(50) NOT NULL, 
	PRIMARY KEY (buyer_slug, dealer_code, make_slug, year_slug), 
	FOREIGN KEY(buyer_slug, dealer_code, make_slug) REFERENCES public.buyer_dealer_make (buyer_slug, dealer_code, make_slug), 
	FOREIGN KEY(buyer_slug, dealer_code, year_slug) REFERENCES public.buyer_dealer_year (buyer_slug, dealer_code, year_slug)
);

-- Create table `buyer_tier_make_model_year`
CREATE TABLE public.buyer_tier_make_model_year (
	buyer_slug VARCHAR(50) NOT NULL, 
	tier_slug VARCHAR(50) NOT NULL, 
	make_slug VARCHAR(50) NOT NULL, 
	model_slug VARCHAR(50) NOT NULL, 
	year_slug VARCHAR(50) NOT NULL, 
	PRIMARY KEY (buyer_slug, tier_slug, make_slug, model_slug, year_slug), 
	FOREIGN KEY(buyer_slug, tier_slug, make_slug, model_slug) REFERENCES public.buyer_tier_make_model (buyer_slug, tier_slug, make_slug, model_slug), 
	FOREIGN KEY(buyer_slug, tier_slug, make_slug, year_slug) REFERENCES public.buyer_tier_make_year (buyer_slug, tier_slug, make_slug, year_slug)
);

-- Create table `buyer_dealer_make_model_year`
CREATE TABLE public.buyer_dealer_make_model_year (
	buyer_slug VARCHAR(50) NOT NULL, 
	dealer_code VARCHAR(50) NOT NULL, 
	make_slug VARCHAR(50) NOT NULL, 
	model_slug VARCHAR(50) NOT NULL, 
	year_slug VARCHAR(50) NOT NULL, 
	PRIMARY KEY (buyer_slug, dealer_code, make_slug, model_slug, year_slug), 
	FOREIGN KEY(buyer_slug, dealer_code, make_slug, model_slug) REFERENCES public.buyer_dealer_make_model (buyer_slug, dealer_code, make_slug, model_slug), 
	FOREIGN KEY(buyer_slug, dealer_code, make_slug, year_slug) REFERENCES public.buyer_dealer_make_year (buyer_slug, dealer_code, make_slug, year_slug)
);
