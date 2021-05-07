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

CREATE PROCEDURE GetTopAgentTicket(
        IN vdate DATE
)
BEGIN
	CREATE OR REPLACE VIEW top_agents_ticket AS (
	    SELECT email, COUNT(ticket_id) AS num_of_ticket
        FROM booking_agent NATURAL JOIN purchases NATURAL JOIN ticket NATURAL JOIN flight
        WHERE purchase_date >= vdate
        GROUP BY email
    );

    SELECT *
    FROM top_agents_ticket AS t1
    WHERE 4 >= (
        SELECT COUNT(DISTINCT t2.num_of_ticket)
        FROM top_agents_ticket AS t2
        WHERE t2.num_of_ticket > t1.num_of_ticket
    );

END //

DELIMITER ;