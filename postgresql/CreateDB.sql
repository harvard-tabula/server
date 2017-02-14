CREATE TABLE users (
    userId character varying(36) NOT NULL,
    email character varying(255)
);

CREATE TABLE profile (
    userHash character varying(36) NOT NULL,
    concentration character varying(255),
    gender character varying(255),
    ethnicity character varying(255),
    codingYears int
);

CREATE TABLE courses (
    courseId character varying(255) NOT NULL,
    courseNumber int,
    description character varying(255)
);

CREATE TABLE classHistory (
    userHash character varying(36) NOT NULL,
    courseId character varying(255) NOT NULL,
    grade character varying(255),
    semester character varying(255),
    workload int,
    enjoyment int,
    learning int,
    difficulty int
);

CREATE TABLE interests (
	userHash character varying(36) NOT NULL,
	interest int
);

CREATE TABLE languages (
	userHash character varying(36) NOT NULL,
	language int
);

CREATE TABLE milestones (
	userHash character varying(36) NOT NULL,
	milestone int
);