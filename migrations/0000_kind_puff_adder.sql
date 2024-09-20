CREATE TABLE IF NOT EXISTS "netaid-users" (
	"id" bigserial PRIMARY KEY NOT NULL,
	"name" varchar(100) NOT NULL,
	"password" varchar(100) NOT NULL,
	"aadhar_no" bigint NOT NULL
);
