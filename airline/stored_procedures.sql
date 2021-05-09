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
CREATE PROCEDURE GetTopAgentsTicket()
BEGIN
	SELECT *
    FROM top_agents_ticket AS t1
    WHERE 4 >= (
        SELECT COUNT(DISTINCT t2.num_of_ticket)
        FROM top_agents_ticket AS t2
        WHERE t2.num_of_ticket > t1.num_of_ticket
    )
    ORDER BY t1.num_of_ticket DESC;
END //
DELIMITER ;


DELIMITER //
CREATE PROCEDURE GetTopAgentsCommission()
BEGIN
    SELECT *
    FROM top_agents_commission AS t1
    WHERE 4 >= (
        SELECT COUNT(DISTINCT t2.amount_of_commission)
        FROM top_agents_commission AS t2
        WHERE t2.amount_of_commission > t1.amount_of_commission
    )
    ORDER BY t1.amount_of_commission DESC;
END //
DELIMITER ;


DELIMITER //
CREATE PROCEDURE GetTopDestination()
BEGIN
    SELECT *
    FROM top_destinations AS t1
    WHERE 2 >= (
        SELECT COUNT(DISTINCT t2.num_of_purchase)
        FROM top_destinations AS t2
        WHERE t2.num_of_purchase > t1.num_of_purchase
    )
    ORDER BY t1.num_of_purchase DESC;
END //
DELIMITER ;


