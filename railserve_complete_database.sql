---------------------------------------------------
-- DROP ALL TABLES
---------------------------------------------------

DROP TABLE IF EXISTS pnr_status_tracking CASCADE;
DROP TABLE IF EXISTS refund_request CASCADE;
DROP TABLE IF EXISTS train_platform_assignment CASCADE;
DROP TABLE IF EXISTS complaint_management CASCADE;
DROP TABLE IF EXISTS payment CASCADE;
DROP TABLE IF EXISTS passenger CASCADE;
DROP TABLE IF EXISTS waitlist CASCADE;
DROP TABLE IF EXISTS dynamic_pricing CASCADE;
DROP TABLE IF EXISTS platform_management CASCADE;
DROP TABLE IF EXISTS performance_metrics CASCADE;
DROP TABLE IF EXISTS tatkal_override CASCADE;
DROP TABLE IF EXISTS chart_preparation CASCADE;
DROP TABLE IF EXISTS seat_availability CASCADE;
DROP TABLE IF EXISTS train_status CASCADE;
DROP TABLE IF EXISTS notification_preferences CASCADE;
DROP TABLE IF EXISTS loyalty_program CASCADE;
DROP TABLE IF EXISTS tatkal_time_slot CASCADE;
DROP TABLE IF EXISTS train_route CASCADE;
DROP TABLE IF EXISTS booking CASCADE;
DROP TABLE IF EXISTS train CASCADE;
DROP TABLE IF EXISTS station CASCADE;
DROP TABLE IF EXISTS "user" CASCADE;

---------------------------------------------------
-- CREATE TABLES
---------------------------------------------------

CREATE TABLE station (
	id SERIAL PRIMARY KEY,
	name VARCHAR(100) UNIQUE NOT NULL,
	code VARCHAR(10) UNIQUE NOT NULL,
	city VARCHAR(50) NOT NULL,
	state VARCHAR(50) NOT NULL,
	active BOOLEAN,
	created_at TIMESTAMP
);

CREATE TABLE train (
	id SERIAL PRIMARY KEY,
	number VARCHAR(10) UNIQUE NOT NULL,
	name VARCHAR(100) NOT NULL,
	total_seats INTEGER NOT NULL,
	available_seats INTEGER NOT NULL,
	fare_per_km FLOAT NOT NULL,
	tatkal_seats INTEGER,
	tatkal_fare_per_km FLOAT,
	active BOOLEAN,
	created_at TIMESTAMP
);

CREATE TABLE "user" (
	id SERIAL PRIMARY KEY,
	username VARCHAR(64) UNIQUE NOT NULL,
	email VARCHAR(120) UNIQUE NOT NULL,
	password_hash VARCHAR(256) NOT NULL,
	role VARCHAR(20),
	active BOOLEAN,
	reset_token VARCHAR(100),
	reset_token_expiry TIMESTAMP,
	created_at TIMESTAMP
);

CREATE TABLE booking (
	id SERIAL PRIMARY KEY,
	pnr VARCHAR(10) UNIQUE NOT NULL,
	user_id INTEGER NOT NULL REFERENCES "user"(id),
	train_id INTEGER NOT NULL REFERENCES train(id),
	from_station_id INTEGER NOT NULL REFERENCES station(id),
	to_station_id INTEGER NOT NULL REFERENCES station(id),
	journey_date DATE NOT NULL,
	passengers INTEGER NOT NULL,
	total_amount FLOAT NOT NULL,
	booking_type VARCHAR(10),
	quota VARCHAR(20),
	coach_class VARCHAR(10),
	status VARCHAR(20),
	waitlist_type VARCHAR(10),
	chart_prepared BOOLEAN,
	berth_preference VARCHAR(20),
	current_reservation BOOLEAN,
	booking_date TIMESTAMP,
	cancellation_charges FLOAT,
	loyalty_discount FLOAT
);

CREATE TABLE chart_preparation (
	id SERIAL PRIMARY KEY,
	train_id INTEGER NOT NULL REFERENCES train(id),
	journey_date DATE NOT NULL,
	chart_prepared_at TIMESTAMP,
	final_chart_at TIMESTAMP,
	status VARCHAR(20),
	confirmed_from_waitlist INTEGER,
	cancelled_waitlist INTEGER
);

CREATE TABLE dynamic_pricing (
	id SERIAL PRIMARY KEY,
	train_id INTEGER NOT NULL REFERENCES train(id),
	journey_date DATE NOT NULL,
	coach_class VARCHAR(10) NOT NULL,
	base_fare FLOAT NOT NULL,
	surge_multiplier FLOAT,
	current_occupancy FLOAT,
	demand_factor FLOAT,
	special_event VARCHAR(100),
	updated_at TIMESTAMP
);

CREATE TABLE loyalty_program (
	id SERIAL PRIMARY KEY,
	user_id INTEGER UNIQUE NOT NULL REFERENCES "user"(id),
	membership_number VARCHAR(20) UNIQUE NOT NULL,
	tier VARCHAR(20),
	points_earned INTEGER,
	points_redeemed INTEGER,
	total_journeys INTEGER,
	total_distance FLOAT,
	total_spent FLOAT,
	tier_valid_until DATE,
	benefits_active BOOLEAN,
	joined_date TIMESTAMP,
	last_activity TIMESTAMP
);

CREATE TABLE notification_preferences (
	id SERIAL PRIMARY KEY,
	user_id INTEGER UNIQUE NOT NULL REFERENCES "user"(id),
	email_notifications BOOLEAN,
	sms_notifications BOOLEAN,
	push_notifications BOOLEAN,
	booking_confirmations BOOLEAN,
	journey_reminders BOOLEAN,
	train_delay_alerts BOOLEAN,
	promotional_offers BOOLEAN
);

CREATE TABLE performance_metrics (
	id SERIAL PRIMARY KEY,
	metric_name VARCHAR(100) NOT NULL,
	metric_value FLOAT NOT NULL,
	metric_unit VARCHAR(20),
	train_id INTEGER REFERENCES train(id),
	station_id INTEGER REFERENCES station(id),
	date_recorded DATE NOT NULL,
	time_recorded TIMESTAMP,
	benchmark_value FLOAT,
	variance_percentage FLOAT
);

CREATE TABLE platform_management (
	id SERIAL PRIMARY KEY,
	station_id INTEGER NOT NULL REFERENCES station(id),
	platform_number VARCHAR(10) NOT NULL,
	track_number VARCHAR(10),
	platform_length INTEGER,
	electrified BOOLEAN,
	status VARCHAR(20),
	facilities TEXT,
	wheelchair_accessible BOOLEAN,
	created_at TIMESTAMP
);

CREATE TABLE seat_availability (
	id SERIAL PRIMARY KEY,
	train_id INTEGER NOT NULL REFERENCES train(id),
	from_station_id INTEGER NOT NULL REFERENCES station(id),
	to_station_id INTEGER NOT NULL REFERENCES station(id),
	journey_date DATE NOT NULL,
	coach_class VARCHAR(10) NOT NULL,
	quota VARCHAR(20),
	available_seats INTEGER,
	waiting_list INTEGER,
	rac_seats INTEGER,
	last_updated TIMESTAMP
);

CREATE TABLE tatkal_override (
	id SERIAL PRIMARY KEY,
	is_enabled BOOLEAN,
	enabled_by INTEGER NOT NULL REFERENCES "user"(id),
	enabled_at TIMESTAMP,
	override_message VARCHAR(200),
	coach_classes VARCHAR(200),
	train_ids TEXT,
	valid_until TIMESTAMP
);

CREATE TABLE tatkal_time_slot (
	id SERIAL PRIMARY KEY,
	name VARCHAR(100) NOT NULL,
	coach_classes VARCHAR(200),
	open_time TIME NOT NULL,
	close_time TIME,
	days_before_journey INTEGER,
	active BOOLEAN,
	created_at TIMESTAMP,
	created_by INTEGER REFERENCES "user"(id)
);

CREATE TABLE train_route (
	id SERIAL PRIMARY KEY,
	train_id INTEGER NOT NULL REFERENCES train(id),
	station_id INTEGER NOT NULL REFERENCES station(id),
	sequence INTEGER NOT NULL,
	arrival_time TIME,
	departure_time TIME,
	distance_from_start FLOAT NOT NULL,
	UNIQUE (train_id, sequence)
);

CREATE TABLE train_status (
	id SERIAL PRIMARY KEY,
	train_id INTEGER NOT NULL REFERENCES train(id),
	current_station_id INTEGER REFERENCES station(id),
	status VARCHAR(50),
	delay_minutes INTEGER,
	last_updated TIMESTAMP,
	journey_date DATE NOT NULL
);

CREATE TABLE complaint_management (
	id SERIAL PRIMARY KEY,
	ticket_number VARCHAR(20) UNIQUE NOT NULL,
	user_id INTEGER NOT NULL REFERENCES "user"(id),
	booking_id INTEGER REFERENCES booking(id),
	category VARCHAR(50) NOT NULL,
	subcategory VARCHAR(50),
	priority VARCHAR(10),
	subject VARCHAR(200) NOT NULL,
	description TEXT NOT NULL,
	status VARCHAR(20),
	assigned_to INTEGER REFERENCES "user"(id),
	resolution TEXT,
	satisfaction_rating INTEGER,
	created_at TIMESTAMP,
	resolved_at TIMESTAMP
);

CREATE TABLE passenger (
	id SERIAL PRIMARY KEY,
	booking_id INTEGER NOT NULL REFERENCES booking(id),
	name VARCHAR(100) NOT NULL,
	age INTEGER NOT NULL,
	gender VARCHAR(10) NOT NULL,
	id_proof_type VARCHAR(20) NOT NULL,
	id_proof_number VARCHAR(50) NOT NULL,
	seat_preference VARCHAR(20),
	coach_class VARCHAR(10),
	seat_number VARCHAR(20),
	berth_type VARCHAR(20)
);

CREATE TABLE payment (
	id SERIAL PRIMARY KEY,
	booking_id INTEGER NOT NULL REFERENCES booking(id),
	user_id INTEGER NOT NULL REFERENCES "user"(id),
	amount FLOAT NOT NULL,
	payment_method VARCHAR(20) NOT NULL,
	transaction_id VARCHAR(50),
	status VARCHAR(20),
	created_at TIMESTAMP,
	completed_at TIMESTAMP,
	CONSTRAINT uq_booking_payment_success UNIQUE (booking_id, status)
);

CREATE TABLE pnr_status_tracking (
	id SERIAL PRIMARY KEY,
	booking_id INTEGER NOT NULL REFERENCES booking(id),
	current_status VARCHAR(50) NOT NULL,
	last_updated TIMESTAMP,
	next_update_time TIMESTAMP,
	coach_position VARCHAR(100),
	boarding_time TIME,
	platform_number VARCHAR(10),
	special_instructions TEXT
);

CREATE TABLE refund_request (
	id SERIAL PRIMARY KEY,
	booking_id INTEGER NOT NULL REFERENCES booking(id),
	user_id INTEGER NOT NULL REFERENCES "user"(id),
	reason TEXT NOT NULL,
	amount_paid FLOAT NOT NULL,
	refund_amount FLOAT NOT NULL,
	cancellation_charges FLOAT,
	tdr_number VARCHAR(20) UNIQUE NOT NULL,
	status VARCHAR(20),
	filed_at TIMESTAMP,
	processed_at TIMESTAMP
);

CREATE TABLE train_platform_assignment (
	id SERIAL PRIMARY KEY,
	train_id INTEGER NOT NULL REFERENCES train(id),
	station_id INTEGER NOT NULL REFERENCES station(id),
	platform_id INTEGER NOT NULL REFERENCES platform_management(id),
	journey_date DATE NOT NULL,
	arrival_platform VARCHAR(10),
	departure_platform VARCHAR(10),
	assigned_at TIMESTAMP,
	assigned_by INTEGER REFERENCES "user"(id)
);

CREATE TABLE waitlist (
	id SERIAL PRIMARY KEY,
	booking_id INTEGER NOT NULL REFERENCES booking(id),
	train_id INTEGER NOT NULL REFERENCES train(id),
	journey_date DATE NOT NULL,
	position INTEGER NOT NULL,
	waitlist_type VARCHAR(10),
	created_at TIMESTAMP
);

---------------------------------------------------
-- INSERT ADMIN USER
---------------------------------------------------

INSERT INTO "user" (username, email, password_hash, role, active)
VALUES (
	'admin',
	'admin@railserve.com',
	'scrypt:32768:8:1$PGkSCp7R4LSK0UYp$044fe71c9079852f04e7274e3e79f897a293b61c5a935d0b3de94b7e9ac478d1e353c31a36e947061fb89b850ad6b9059fe5b6ace5617ed69ebfda0ed590ffb6',
	'super_admin',
	TRUE
);

---------------------------------------------------
-- INSERT STATIONS
---------------------------------------------------

INSERT INTO station (code, name, city, state, active) VALUES
('NDLS','NEW DELHI','New Delhi','Delhi',TRUE),
('CSMT','MUMBAI CST','Mumbai','Maharashtra',TRUE),
('MAS','CHENNAI CENTRAL','Chennai','Tamil Nadu',TRUE),
('HWH','HOWRAH JN','Howrah','West Bengal',TRUE),
('SBC','BANGALORE CITY','Bangalore','Karnataka',TRUE),
('BPL','BHOPAL JN','Bhopal','Madhya Pradesh',TRUE),
('LKO','LUCKNOW','Lucknow','Uttar Pradesh',TRUE),
('JP','JAIPUR','Jaipur','Rajasthan',TRUE),
('PUNE','PUNE JN','Pune','Maharashtra',TRUE),
('ADI','AHMEDABAD JN','Ahmedabad','Gujarat',TRUE);

---------------------------------------------------
-- INSERT TRAINS
---------------------------------------------------

INSERT INTO train (number, name, total_seats, available_seats, fare_per_km, tatkal_seats, tatkal_fare_per_km, active) VALUES
('12301','Howrah Rajdhani',1200,1200,0.75,120,0.975,TRUE),
('12302','New Delhi Rajdhani',1200,1200,0.75,120,0.975,TRUE),
('12951','Mumbai Rajdhani',1000,1000,0.8,100,1.04,TRUE),
('12009','Shatabdi Express',800,800,0.85,80,1.105,TRUE),
('12259','Duronto Express',1100,1100,0.7,110,0.91,TRUE);

---------------------------------------------------
-- INSERT TATKAL TIME SLOTS
---------------------------------------------------

INSERT INTO tatkal_time_slot (name, coach_classes, open_time, close_time, days_before_journey, created_by, active)
VALUES
('AC Classes Tatkal','AC1,AC2,AC3,CC','10:00:00','23:59:59',1,1,TRUE),
('Non-AC Classes Tatkal','SL,2S','11:00:00','23:59:59',1,1,TRUE);

---------------------------------------------------
-- INSERT REAL TRAIN ROUTES
---------------------------------------------------
-- Howrah Rajdhani (12301) : HWH -> BHOPAL -> NDLS (simplified with major stops)
INSERT INTO train_route (train_id, station_id, sequence, arrival_time, departure_time, distance_from_start) VALUES
(1, 4, 1, NULL, '05:00:00', 0.0), -- HWH
(1, 6, 2, '14:00:00', '14:10:00', 1100.0), -- BPL
(1, 1, 3, '19:30:00', NULL, 1500.0); -- NDLS


-- New Delhi Rajdhani (12302) : NDLS -> LKO -> PRAYAG (using LKO & BPL as samples)
INSERT INTO train_route (train_id, station_id, sequence, arrival_time, departure_time, distance_from_start) VALUES
(2, 1, 1, NULL, '07:00:00', 0.0), -- NDLS
(2, 7, 2, '11:30:00', '11:35:00', 500.0), -- LKO
(2, 6, 3, '18:00:00', NULL, 1100.0); -- BPL (terminus for example)


-- Mumbai Rajdhani (12951) : CSMT -> PUNE -> NDLS (simplified)
INSERT INTO train_route (train_id, station_id, sequence, arrival_time, departure_time, distance_from_start) VALUES
(3, 2, 1, NULL, '06:30:00', 0.0), -- CSMT
(3, 9, 2, '09:45:00', '09:50:00', 150.0), -- PUNE
(3, 1, 3, '22:00:00', NULL, 1400.0); -- NDLS


-- Shatabdi Express (12009) : MAS -> SBC -> NDLS (simplified)
INSERT INTO train_route (train_id, station_id, sequence, arrival_time, departure_time, distance_from_start) VALUES
(4, 3, 1, NULL, '08:00:00', 0.0), -- MAS
(4, 5, 2, '13:30:00', '13:40:00', 350.0), -- SBC (Bangalore City)
(4, 1, 3, '23:59:00', NULL, 2000.0); -- NDLS (terminus for example)


-- Duronto Express (12259) : ADI -> JP -> NDLS
INSERT INTO train_route (train_id, station_id, sequence, arrival_time, departure_time, distance_from_start) VALUES
(5, 10, 1, NULL, '09:00:00', 0.0), -- ADI
(5, 8, 2, '13:15:00', '13:20:00', 500.0), -- JP
(5, 1, 3, '22:30:00', NULL, 1100.0); -- NDLS


-- ---------------------------------------------------
-- Seat availability per coach class (sample snapshot)
-- Journey date used for these examples: '2025-11-21'
-- Each train will have multiple rows for class / quota combinations
-- ---------------------------------------------------


-- Helper comment: coach classes used in this dataset: AC1, AC2, AC3, CC, SL, 2S


-- Howrah Rajdhani (train_id = 1) seat availability HWH -> NDLS on 2025-11-21
INSERT INTO seat_availability (train_id, from_station_id, to_station_id, journey_date, coach_class, quota, available_seats, waiting_list, rac_seats, last_updated) VALUES
(1, 4, 1, '2025-11-21', 'AC1', 'GN', 6, 0, 0, NOW()),
(1, 4, 1, '2025-11-21', 'AC2', 'GN', 40, 2, 4, NOW()),
(1, 4, 1, '2025-11-21', 'AC3', 'GN', 120, 10, 12, NOW()),
(1, 4, 1, '2025-11-21', 'CC', 'GN', 60, 5, 8, NOW()),
(1, 4, 1, '2025-11-21', 'SL', 'GN', 700, 50, 0, NOW()),
(1, 4, 1, '2025-11-21', '2S', 'GN', 0, 100, 0, NOW());


-- New Delhi Rajdhani (train_id = 2) NDLS -> BPL on 2025-11-21
INSERT INTO seat_availability (train_id, from_station_id, to_station_id, journey_date, coach_class, quota, available_seats, waiting_list, rac_seats, last_updated) VALUES
(2, 1, 6, '2025-11-21', 'AC1', 'GN', 2, 0, 0, NOW()),
(2, 1, 6, '2025-11-21', 'AC2', 'GN', 30, 5, 6, NOW()),
(2, 1, 6, '2025-11-21', 'AC3', 'GN', 100, 20, 10, NOW()),
(2, 1, 6, '2025-11-21', 'CC', 'GN', 40, 10, 5, NOW()),
(2, 1, 6, '2025-11-21', 'SL', 'GN', 500, 80, 0, NOW());


-- Mumbai Rajdhani (train_id = 3) CSMT -> NDLS on 2025-11-21
INSERT INTO seat_availability (train_id, from_station_id, to_station_id, journey_date, coach_class, quota, available_seats, waiting_list, rac_seats, last_updated) VALUES
(3, 2, 1, '2025-11-21', 'AC1', 'GN', 4, 0, 0, NOW()),
(3, 2, 1, '2025-11-21', 'AC2', 'GN', 50, 4, 6, NOW()),
(3, 2, 1, '2025-11-21', 'AC3', 'GN', 150, 12, 20, NOW()),
(3, 2, 1, '2025-11-21', 'CC', 'GN', 80, 6, 8, NOW()),
(3, 2, 1, '2025-11-21', 'SL', 'GN', 650, 40, 0, NOW());


-- Shatabdi Express (train_id = 4) MAS -> NDLS on 2025-11-21
INSERT INTO seat_availability (train_id, from_station_id, to_station_id, journey_date, coach_class, quota, available_seats, waiting_list, rac_seats, last_updated) VALUES
(4, 3, 1, '2025-11-21', 'CC', 'GN', 120, 0, 0, NOW()),
(4, 3, 1, '2025-11-21', 'AC2', 'GN', 80, 10, 6, NOW()),
(4, 3, 1, '2025-11-21', 'AC3', 'GN', 60, 20, 8, NOW()),
(4, 3, 1, '2025-11-21', 'SL', 'GN', 400, 120, 0, NOW());


-- Duronto Express (train_id = 5) ADI -> NDLS on 2025-11-21
INSERT INTO seat_availability (train_id, from_station_id, to_station_id, journey_date, coach_class, quota, available_seats, waiting_list, rac_seats, last_updated) VALUES
(5, 10, 1, '2025-11-21', 'AC1', 'GN', 8, 0, 0, NOW()),
(5, 10, 1, '2025-11-21', 'AC2', 'GN', 70, 6, 8, NOW()),
(5, 10, 1, '2025-11-21', 'AC3', 'GN', 180, 22, 15, NOW()),
(5, 10, 1, '2025-11-21', 'SL', 'GN', 520, 90, 0, NOW());


-- -------------------------
