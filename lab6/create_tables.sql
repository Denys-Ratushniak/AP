CREATE TABLE user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(128),
    firstName VARCHAR(32),
    lastName VARCHAR(32),
    email VARCHAR(128),
    password VARCHAR(128),
    phone VARCHAR(32),
    birthDate DATE,
    userStatus ENUM('0', '1') DEFAULT '1'
);

CREATE TABLE classroom (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(128),
    classroomStatus ENUM('available', 'pending', 'unavailable') DEFAULT 'available',
    capacity INT
);

CREATE TABLE order_table (
    id INT AUTO_INCREMENT PRIMARY KEY,
    classroomId INT,
    userId INT,
    start_time DATETIME,
    end_time DATETIME,
    status ENUM('placed','approved','denied') DEFAULT 'placed',
    FOREIGN KEY(classroomId) REFERENCES classroom(id),
    FOREIGN KEY(userId) REFERENCES user(id)
);



-- mysql -u root -p ap
-- source F:\bohdan\3_sem\PP\AP\lab6\create_tables.sql

