CREATE TRIGGER agent_id_update
AFTER UPDATE ON booking_agent
FOR EACH ROW
    UPDATE purchases
    SET booking_agent_id = NEW.booking_agent_id
    WHERE booking_agent_id = OLD.booking_agent_id;
