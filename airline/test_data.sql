INSERT INTO Airline
VALUES ("China Eastern Airlines"), ("China Southern Airlines"),
        ("Air China"), ("Sichuan Airlines");

INSERT INTO Airport
VALUES ("JFK", "NYC"), ("PVG", "Shanghai"), ("PEK", "Beijing"),
        ("SHA", "Shanghai"), ("PKX", "Beijing");

INSERT INTO airplane
VALUES ("China Eastern Airlines", 330, 259), ("China Eastern Airlines", 320, 259);

INSERT INTO Flight
VALUES ("China Eastern Airlines", "1", "PVG", "2021-05-01 08:00:00", "PEK", "2021-05-01 10:00:00", 10000, "Upcoming", 330),
        ("China Eastern Airlines", "2", "PVG", "2021-05-01 09:00:00", "PKX", "2021-05-01 11:00:00", 3000, "Upcoming", 320),
        ("China Eastern Airlines", "3", "SHA", "2021-05-01 10:00:00", "PEK", "2021-05-01 12:00:00", 3000, "Upcoming", 320),
        ("China Eastern Airlines", "4", "SHA", "2021-05-01 11:00:00", "PKX", "2021-05-01 13:00:00", 3000, "Upcoming", 320),
        ("China Eastern Airlines", "5", "PEK", "2021-05-01 12:00:00", "PVG", "2021-05-01 14:00:00", 3000, "Upcoming", 330),
        ("China Eastern Airlines", "6", "PEK", "2021-05-01 13:00:00", "SHA", "2021-05-01 15:00:00", 3000, "Upcoming", 320),
        ("China Eastern Airlines", "7", "PKX", "2021-05-01 14:00:00", "PVG", "2021-05-01 16:00:00", 3000, "Upcoming", 320),
        ("China Eastern Airlines", "8", "PKX", "2021-05-01 15:00:00", "SHA", "2021-05-01 17:00:00", 3000, "Upcoming", 320);
