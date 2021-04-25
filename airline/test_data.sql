INSERT INTO Airline
VALUES ("China Eastern Airlines"), ("China Southern Airlines"),
        ("Air China"), ("Sichuan Airlines");

INSERT INTO Airport
VALUES ("JFK", "NYC"), ("PVG", "Shanghai"), ("PEK", "Beijing"),
       ("SHA", "Shanghai"), ("PKX", "Beijing"),("CSX", "Changsha"),
       ("CTU", "Chengdu"), ("CKG", "Chongqing"), ("FOC", "Fuzhou"), ("CAN", "Guangzhou");

INSERT INTO airplane
VALUES ("China Eastern Airlines", "A330-200", 247), ("China Eastern Airlines", "A330-300", 277);

INSERT INTO Flight
VALUES ("China Eastern Airlines", "MU0001", "PVG", "2021-05-01 08:00:00", "PEK", "2021-05-01 10:00:00", 10000, "Upcoming", "A330-300"),
        ("China Eastern Airlines", "MU0002", "PVG", "2021-05-01 09:00:00", "PKX", "2021-05-01 11:00:00", 3000, "Upcoming", "A330-200"),
        ("China Eastern Airlines", "MU0003", "SHA", "2021-05-01 10:00:00", "PEK", "2021-05-01 12:00:00", 3000, "Upcoming", "A330-200"),
        ("China Eastern Airlines", "MU0004", "SHA", "2021-05-01 11:00:00", "PKX", "2021-05-01 13:00:00", 3000, "Upcoming", "A330-200"),
        ("China Eastern Airlines", "MU0005", "PEK", "2021-05-01 12:00:00", "PVG", "2021-05-01 14:00:00", 3000, "Upcoming", "A330-300"),
        ("China Eastern Airlines", "MU0006", "PEK", "2021-05-01 13:00:00", "SHA", "2021-05-01 15:00:00", 3000, "Upcoming", "A330-200"),
        ("China Eastern Airlines", "MU0007", "PKX", "2021-05-01 14:00:00", "PVG", "2021-05-01 16:00:00", 3000, "Upcoming", "A330-200"),
        ("China Eastern Airlines", "MU0008", "PKX", "2021-05-01 15:00:00", "SHA", "2021-05-01 17:00:00", 3000, "Upcoming", "A330-300");
