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



DELIMITER //

CREATE PROCEDURE GetTopAgentTicket()
BEGIN
	CREATE OR REPLACE VIEW top_agents_ticket AS (
	    SELECT email, COUNT(ticket_id) AS num_of_ticket
        FROM booking_agent NATURAL JOIN purchases NATURAL JOIN ticket NATURAL JOIN flight
        WHERE purchase_date >= \'%s\'
        GROUP BY email
    );

END //

DELIMITER ;