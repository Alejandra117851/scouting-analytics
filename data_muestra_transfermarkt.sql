-- Datos de muestra estilo Transfermarkt para practicar la Guia 2
-- Genera 3 tablas: competitions, clubs, players

USE mineria_datos;

DROP TABLE IF EXISTS players;
DROP TABLE IF EXISTS clubs;
DROP TABLE IF EXISTS competitions;

CREATE TABLE competitions (
    competition_id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100),
    type VARCHAR(50)
);

CREATE TABLE clubs (
    club_id INT PRIMARY KEY,
    name VARCHAR(100),
    domestic_competition_id VARCHAR(10),
    FOREIGN KEY (domestic_competition_id) REFERENCES competitions(competition_id)
);

CREATE TABLE players (
    player_id INT PRIMARY KEY,
    name VARCHAR(100),
    position VARCHAR(50),
    height_in_cm INT,
    date_of_birth DATE,
    market_value_in_eur BIGINT,
    current_club_id INT,
    FOREIGN KEY (current_club_id) REFERENCES clubs(club_id)
);

INSERT INTO competitions (competition_id, name, type) VALUES
('ES1', 'LaLiga', 'domestic_league'),
('GB1', 'Premier League', 'domestic_league'),
('IT1', 'Serie A', 'domestic_league'),
('L1', 'Bundesliga', 'domestic_league'),
('FR1', 'Ligue 1', 'domestic_league'),
('CL', 'Champions League', 'international_cup');

INSERT INTO clubs (club_id, name, domestic_competition_id) VALUES
(1, 'Real Madrid', 'ES1'),
(2, 'FC Barcelona', 'ES1'),
(3, 'Atletico Madrid', 'ES1'),
(4, 'Manchester City', 'GB1'),
(5, 'Liverpool', 'GB1'),
(6, 'Arsenal', 'GB1'),
(7, 'Juventus', 'IT1'),
(8, 'Inter de Milan', 'IT1'),
(9, 'Bayern Munich', 'L1'),
(10, 'Borussia Dortmund', 'L1'),
(11, 'Paris Saint-Germain', 'FR1'),
(12, 'AS Monaco', 'FR1');

INSERT INTO players (player_id, name, position, height_in_cm, date_of_birth, market_value_in_eur, current_club_id) VALUES
(1000, 'Diego Garcia', 'Defender', 173, '1997-11-24', 15200000, 1),
(1001, 'Hugo Nilsson', 'Attack', 182, '1996-02-07', 39900000, 1),
(1002, 'Jonas Pereira', 'Attack', 196, '2004-07-08', 3500000, 1),
(1003, 'Hugo Rossi', 'Attack', 189, '1998-12-14', 19300000, 1),
(1004, 'Miguel Rodriguez', 'Midfield', 190, '1997-07-04', 33500000, 1),
(1005, 'Rafael Bernard', 'Defender', 175, '1996-12-15', 12800000, 1),
(1006, 'Andres Costa', 'Defender', 172, '2001-10-07', 21000000, 2),
(1007, 'Luis Schmidt', 'Defender', 174, '1997-04-28', 4000000, 2),
(1008, 'Luca Rossi', 'Goalkeeper', 185, '2001-06-07', 5000000, 2),
(1009, 'Youssef Lopez', 'Midfield', 178, '2004-12-08', 12500000, 2),
(1010, 'Erik Andersson', 'Defender', 188, '2004-04-22', 27800000, 2),
(1011, 'Javier Martinez', 'Defender', 181, '2002-05-03', 14200000, 3),
(1012, 'Tiago Ferreira', 'Defender', 184, '2006-08-05', 17500000, 3),
(1013, 'Mateo Schmidt', 'Defender', 193, '2005-07-19', 25300000, 3),
(1014, 'Marco Schmidt', 'Midfield', 178, '1996-02-05', 16200000, 3),
(1015, 'Kevin Pereira', 'Attack', 197, '2002-07-20', 29500000, 4),
(1016, 'Jonas Rossi', 'Attack', 189, '2004-05-25', 26200000, 4),
(1017, 'Diego Bianchi', 'Goalkeeper', 184, '1998-08-01', 5900000, 4),
(1018, 'Jonas Silva', 'Attack', 180, '2006-09-20', 40400000, 4),
(1019, 'Mateo Bernard', 'Midfield', 188, '2004-09-01', 13900000, 4),
(1020, 'Lars Garcia', 'Attack', 183, '2000-04-02', 63400000, 4),
(1021, 'Andres Lopez', 'Goalkeeper', 176, '1997-09-25', 3800000, 5),
(1022, 'Mateo Traore', 'Midfield', 180, '2002-04-18', 19500000, 5),
(1023, 'Youssef Bianchi', 'Goalkeeper', 196, '2006-11-12', 17700000, 5),
(1024, 'Gabriel Diallo', 'Goalkeeper', 182, '2001-01-19', 10500000, 5),
(1025, 'Hugo Schmidt', 'Attack', 171, '1997-12-21', 38800000, 5),
(1026, 'Javier Lopez', 'Attack', 199, '1999-05-22', 34400000, 5),
(1027, 'Antoine Rodriguez', 'Goalkeeper', 194, '1999-08-26', 6600000, 6),
(1028, 'Pablo Fernandez', 'Attack', 171, '2002-08-28', 20900000, 6),
(1029, 'Amadou Fernandez', 'Attack', 174, '2002-12-11', 15800000, 6),
(1030, 'Javier Muller', 'Midfield', 183, '1998-05-15', 14900000, 6),
(1031, 'Erik Costa', 'Attack', 168, '1996-11-18', 27800000, 7),
(1032, 'Andres Schmidt', 'Midfield', 192, '2002-01-06', 9400000, 7),
(1033, 'Carlos Andersson', 'Defender', 199, '2003-05-14', 20700000, 7),
(1034, 'Mateo Muller', 'Defender', 188, '2004-01-24', 15600000, 7),
(1035, 'Luis Ferreira', 'Goalkeeper', 171, '2004-09-06', 9600000, 8),
(1036, 'Jonas Lopez', 'Midfield', 183, '1999-07-04', 26500000, 8),
(1037, 'Hugo Pereira', 'Attack', 188, '2005-02-14', 32800000, 8),
(1038, 'Tiago Rossi', 'Midfield', 187, '2000-07-05', 16500000, 8),
(1039, 'Thomas Lopez', 'Attack', 174, '2003-10-19', 16300000, 9),
(1040, 'Andres Costa', 'Midfield', 191, '2001-02-08', 15000000, 9),
(1041, 'Alejandro Silva', 'Goalkeeper', 168, '2004-12-10', 7900000, 9),
(1042, 'Amadou Costa', 'Defender', 174, '1998-05-04', 18800000, 9),
(1043, 'Ibrahim Costa', 'Midfield', 181, '2000-05-20', 19400000, 9),
(1044, 'Thomas Muller', 'Defender', 195, '1996-02-21', 8200000, 10),
(1045, 'Bruno Rossi', 'Attack', 176, '1996-06-25', 29500000, 10),
(1046, 'Kwame Rossi', 'Midfield', 175, '2002-09-01', 21100000, 10),
(1047, 'Andres Rodriguez', 'Attack', 177, '2001-10-18', 7200000, 10),
(1048, 'Kevin Rodriguez', 'Attack', 183, '1996-06-07', 16200000, 10),
(1049, 'Amadou Fernandez', 'Defender', 177, '2004-07-20', 33000000, 10),
(1050, 'Rafael Silva', 'Midfield', 183, '2001-07-26', 24200000, 11),
(1051, 'Miguel Silva', 'Attack', 198, '2002-01-28', 27300000, 11),
(1052, 'Javier Muller', 'Goalkeeper', 180, '1999-04-01', 2800000, 11),
(1053, 'Luca Dubois', 'Defender', 200, '1997-05-12', 28500000, 11),
(1054, 'Amadou Costa', 'Defender', 184, '2000-03-19', 19100000, 12),
(1055, 'Luis Fernandez', 'Goalkeeper', 188, '2001-12-26', 7100000, 12),
(1056, 'Kevin Pereira', 'Attack', 195, '2000-01-23', 12300000, 12),
(1057, 'Carlos Diallo', 'Midfield', 189, '2001-07-03', 33400000, 12),
(1058, 'Leo Dubois', 'Attack', 188, '2000-11-14', 27100000, 12);
