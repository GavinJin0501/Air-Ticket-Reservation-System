DELIMITER //

CREATE PROCEDURE GetAirportWithCity()
BEGIN
	SELECT airport_city, airport_name FROM `airport`;
END //

DELIMITER ;



DELIMITER //

CREATE PROCEDURE GetUniqueAirportCity()
BEGIN
	SELECT DISTINCT airport_city FROM `airport`;
END //

DELIMITER ;
