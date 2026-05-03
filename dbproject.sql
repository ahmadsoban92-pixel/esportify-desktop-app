CREATE DATABASE ESPORTS_SYSTEM;
GO

USE ESPORTS_SYSTEM;
GO

----------------------------------------------------------------
-- TABLES & INDEXES
----------------------------------------------------------------
CREATE TABLE Users (
    u_id INT IDENTITY(1,1) PRIMARY KEY CLUSTERED,
    name VARCHAR(50) NOT NULL
        CHECK (name NOT LIKE '%[0-9]%' AND name NOT LIKE '%[^A-Za-z ]%'),
    email VARCHAR(100) UNIQUE NOT NULL,
    CHECK (
        email NOT LIKE '% %'               
        AND email LIKE '%@gmail.com'       
        AND email NOT LIKE '%@%@%'         
        AND email NOT LIKE '.%'           
        AND email NOT LIKE '@%'          
    ),
    password VARCHAR(255) NOT NULL
        CHECK (LEN(password) >= 8),
    CNIC VARCHAR(15) NOT NULL
        CHECK (CNIC LIKE '[0-9][0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9][0-9][0-9][0-9]-[0-9]'),
    role VARCHAR(20) NOT NULL 
        CHECK (role IN ('admin','player','referee'))
);

CREATE NONCLUSTERED INDEX idx_users_role ON Users(role);
CREATE NONCLUSTERED INDEX idx_users_email ON Users(email);
CREATE NONCLUSTERED INDEX idx_users_pass ON Users(password);
CREATE NONCLUSTERED INDEX idx_users_name ON Users(name);
GO

CREATE TABLE Player (
    p_id INT PRIMARY KEY CLUSTERED
        REFERENCES Users(u_id) ON DELETE CASCADE,
    p_tag VARCHAR(30) UNIQUE NOT NULL
);
CREATE NONCLUSTERED INDEX idx_p_tag ON Player(p_tag);
GO

CREATE TABLE Game (
    g_id INT IDENTITY(1,1) PRIMARY KEY CLUSTERED,
    g_name VARCHAR(50) UNIQUE NOT NULL,
    format VARCHAR(30) NOT NULL CHECK (format IN ('Knockout', 'Battle Royale'))
);
CREATE NONCLUSTERED INDEX idx_game_name ON Game(g_name);
GO

CREATE TABLE Referee (
    r_id INT PRIMARY KEY CLUSTERED
        REFERENCES Users(u_id) ON DELETE CASCADE,
    salary INT NOT NULL CHECK (salary >= 0),
    experience_in_years INT NOT NULL CHECK (experience_in_years >= 0),
    specialization_id INT NOT NULL REFERENCES Game(g_id),
    status VARCHAR(20) NOT NULL DEFAULT 'Applicant' CHECK ( status In ('Applicant','Hired'))
);
CREATE NONCLUSTERED INDEX idx_experience ON Referee(experience_in_years);
CREATE NONCLUSTERED INDEX idx_specilization ON Referee(specialization_id);
GO

CREATE TABLE Payment (
    pay_id INT IDENTITY(1,1) PRIMARY KEY CLUSTERED,
    p_id INT NOT NULL REFERENCES Player(p_id),
    amount INT NOT NULL CHECK (amount >= 0),
    date DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    proof_image VARBINARY(MAX),
    status VARCHAR(20) NOT NULL CHECK (status IN ('pending','completed','failed'))
);
CREATE NONCLUSTERED INDEX idx_payment_player ON Payment(p_id);
CREATE NONCLUSTERED INDEX idx_payment_status ON Payment(status);
CREATE NONCLUSTERED INDEX idx_payment_date ON Payment(date);
GO

CREATE TABLE Tournament (
    t_id INT IDENTITY(1,1) PRIMARY KEY CLUSTERED,
    t_name VARCHAR(60) NOT NULL,
    venue VARCHAR(60) NOT NULL,
    g_id INT NOT NULL REFERENCES Game(g_id),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    entry_fee INT NOT NULL CHECK (entry_fee >= 0),
    winner_id INT NULL REFERENCES Player(p_id),
    max_players INT NOT NULL CHECK (max_players IN (8, 16, 32)),
    status VARCHAR(20) DEFAULT 'Open' CHECK (status IN ('Open','Filled', 'Ongoing', 'Completed','Cancelled')),
    CONSTRAINT chk_dates CHECK (end_date >= start_date)
);
CREATE NONCLUSTERED INDEX idx_tournament_game ON Tournament(g_id);
CREATE NONCLUSTERED INDEX idx_tournament_winner ON Tournament(winner_id);
CREATE NONCLUSTERED INDEX idx_tournament_sdate ON Tournament(start_date);
CREATE NONCLUSTERED INDEX idx_tournament_status ON Tournament(status);
CREATE NONCLUSTERED INDEX idx_tournament_venue ON Tournament(venue);
GO

CREATE TABLE Registration (
    reg_id INT IDENTITY(1,1) PRIMARY KEY CLUSTERED,
    p_id INT NOT NULL REFERENCES Player(p_id),
    t_id INT NOT NULL REFERENCES Tournament(t_id) ON DELETE CASCADE,
    pay_id INT UNIQUE NOT NULL REFERENCES Payment(pay_id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL CHECK (status IN ('pending','approved','rejected')),
    timestamp DATETIME2 DEFAULT SYSDATETIME()
);
CREATE NONCLUSTERED INDEX idx_registration_player ON Registration(p_id);
CREATE NONCLUSTERED INDEX idx_registration_tournament ON Registration(t_id);
CREATE NONCLUSTERED INDEX idx_registration_status ON Registration(status);
CREATE NONCLUSTERED INDEX idx_registration_payment ON Registration(pay_id);
GO

CREATE TABLE Match (
    m_id INT IDENTITY(1,1) PRIMARY KEY CLUSTERED,
    t_id INT NOT NULL REFERENCES Tournament(t_id) ON DELETE CASCADE,
    r_id INT NOT NULL REFERENCES Referee(r_id),
    match_time DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    round_num INT DEFAULT 1,
    winner_id INT NULL REFERENCES Player(p_id),
    status VARCHAR(20) NOT NULL CHECK (status IN ('Scheduled', 'Ongoing', 'Completed')) DEFAULT 'Scheduled'
);
CREATE NONCLUSTERED INDEX idx_match_tournament ON Match(t_id);
CREATE NONCLUSTERED INDEX idx_match_referee ON Match(r_id);
CREATE NONCLUSTERED INDEX idx_match_time ON Match(match_time);
CREATE NONCLUSTERED INDEX idx_match_status ON Match(status);
GO

CREATE TABLE Match_Participants (
    mp_id INT IDENTITY(1,1) PRIMARY KEY CLUSTERED,
    m_id INT NOT NULL REFERENCES Match(m_id) ON DELETE CASCADE,
    p_id INT NOT NULL REFERENCES Player(p_id),
    score_value INT DEFAULT 0 CHECK (score_value >= 0), 
    placement INT DEFAULT 0 CHECK (placement >= 0),
    total_points INT DEFAULT 0, 
    is_winner BIT DEFAULT 0,
    CONSTRAINT uc_match_player UNIQUE (m_id, p_id) 
);
CREATE NONCLUSTERED INDEX idx_participants_match ON Match_Participants(m_id);
CREATE NONCLUSTERED INDEX idx_participants_player ON Match_Participants(p_id);
CREATE NONCLUSTERED INDEX idx_participants_placement ON Match_Participants(placement);
CREATE NONCLUSTERED INDEX idx_participants_points ON Match_Participants(total_points);
GO

CREATE TABLE History (
    history_id INT IDENTITY(1,1) PRIMARY KEY CLUSTERED,
    user_id INT NOT NULL REFERENCES Users(u_id),
    entity VARCHAR(30) NOT NULL CHECK (entity IN ('Payment','Registration','Match','Tournament','Referee','Player','Disputes','Game')),
    entity_id INT NOT NULL,
    action VARCHAR(200) NOT NULL,
    timestamp DATETIME2 DEFAULT SYSDATETIME()
);
CREATE NONCLUSTERED INDEX idx_history_user ON History(user_id);
CREATE NONCLUSTERED INDEX idx_history_entity ON History(entity, entity_id);
CREATE NONCLUSTERED INDEX idx_history_time ON History(timestamp);
GO

CREATE TABLE Disputes (
    dispute_id INT IDENTITY(1,1) PRIMARY KEY CLUSTERED,
    filed_by INT NOT NULL REFERENCES Player(p_id),
    against_player INT NOT NULL REFERENCES Player(p_id),
    status VARCHAR(20) NOT NULL CHECK (status IN ('pending','approved','rejected')) DEFAULT 'pending',
    referee_id INT NULL REFERENCES Referee(r_id),
    reason VARCHAR(200) NOT NULL,
    filed_at DATETIME2 DEFAULT SYSDATETIME(),
    resolved_at DATETIME2 NULL,
    CHECK (filed_by <> against_player),
    CHECK (resolved_at IS NULL OR resolved_at >= filed_at)
);
CREATE NONCLUSTERED INDEX idx_disputes_filed_by ON Disputes(filed_by);
CREATE NONCLUSTERED INDEX idx_disputes_against_player ON Disputes(against_player);
CREATE NONCLUSTERED INDEX idx_disputes_referee ON Disputes(referee_id);
CREATE NONCLUSTERED INDEX idx_disputes_filed ON Disputes(filed_at);
CREATE NONCLUSTERED INDEX idx_disputes_resolved ON Disputes(resolved_at);
GO

----------------------------------------------------------------
-- VIEWS
----------------------------------------------------------------
CREATE VIEW g_names as select g_name from Game;
GO
CREATE VIEW login_check AS SELECT email,password,role FROM Users;
GO
CREATE VIEW find_admin_id AS SELECT u_id from Users where role = 'admin';
GO
CREATE VIEW vw_RefereeLookup AS
SELECT r.r_id, u.email 
FROM Referee r 
JOIN Users u ON r.r_id = u.u_id;
GO

CREATE VIEW vw_RefereeMatches AS
SELECT 
    m.m_id, 
    t.t_name,     
    g.g_name, 
    g.format, 
    m.status, 
    m.r_id 
FROM Match m
JOIN Tournament t ON m.t_id = t.t_id
JOIN Game g ON t.g_id = g.g_id;
GO

CREATE VIEW vw_MatchPlayers AS
SELECT 
    mp.m_id, 
    p.p_tag AS Gamertag 
FROM Match_Participants mp
JOIN Player p ON mp.p_id = p.p_id;
GO

CREATE VIEW vw_RefereeHistory AS
SELECT 
    m.m_id, 
    t.t_name,
    g.g_name, 
    ISNULL(p.p_tag, 'Draw/TBD') as WinnerName,
    m.match_time AS DatePlayed,
    m.r_id
FROM Match m
JOIN Tournament t ON m.t_id = t.t_id
JOIN Game g ON t.g_id = g.g_id
LEFT JOIN Player p ON m.winner_id = p.p_id
WHERE m.status = 'Completed';
GO

CREATE VIEW vw_RefereeDisputes AS
SELECT 
    d.dispute_id, 
    p.p_tag AS ReportedName, 
    d.reason, 
    d.referee_id,
    d.status
FROM Disputes d
JOIN Player p ON d.against_player = p.p_id;
GO

CREATE VIEW vw_PlayerLookup AS
SELECT p.p_id, u.email 
FROM Player p 
JOIN Users u ON p.p_id = u.u_id;
GO

CREATE VIEW vw_AdminTournaments AS
SELECT t.t_id, t.t_name, g.g_name, g.format, t.status, t.max_players, t.start_date
FROM Tournament t
INNER JOIN Game g ON t.g_id = g.g_id;
GO

CREATE VIEW vw_AdminRefereesPending AS
SELECT r.r_id, u.name AS FullName, g.g_name AS Specialization, r.experience_in_years
FROM Referee r
INNER JOIN Users u ON r.r_id = u.u_id
INNER JOIN Game g ON r.specialization_id = g.g_id
WHERE r.status = 'Applicant';
GO

CREATE VIEW vw_AdminRefereesActive AS
SELECT r.r_id, u.name AS FullName, g.g_name AS Specialization
FROM Referee r
INNER JOIN Users u ON r.r_id = u.u_id
INNER JOIN Game g ON r.specialization_id = g.g_id
WHERE r.status = 'Hired';
GO

CREATE VIEW vw_AdminPayments AS
SELECT 
    py.pay_id, 
    u.name AS Username, 
    t.t_name AS TournamentName, 
    py.amount, 
    py.status,
    py.proof_image 
FROM Payment py
INNER JOIN Player p ON py.p_id = p.p_id
INNER JOIN Users u ON p.p_id = u.u_id
INNER JOIN Registration r ON py.pay_id = r.pay_id
INNER JOIN Tournament t ON r.t_id = t.t_id
WHERE py.status = 'pending';
GO

CREATE VIEW vw_AdminPlayers AS
SELECT p.p_id, p.p_tag AS Gamertag, u.email
FROM Player p
INNER JOIN Users u ON p.p_id = u.u_id;
GO

CREATE VIEW vw_GameDetails AS
SELECT g_id, g_name, format FROM Game;
GO

CREATE VIEW vw_OpenTournaments AS
SELECT 
    t.t_id,
    t.t_name, 
    g.g_name, 
    g.format, 
    t.entry_fee 
FROM Tournament t
INNER JOIN Game g ON t.g_id = g.g_id
WHERE t.status = 'Open';
GO

CREATE VIEW vw_MyRegistrations AS
SELECT 
    r.p_id AS PlayerID,
    t.t_id, 
    t.t_name AS Name, 
    g.g_name AS GameName, 
    r.status AS Status
FROM Registration r
INNER JOIN Tournament t ON r.t_id = t.t_id
INNER JOIN Game g ON t.g_id = g.g_id;
GO

CREATE VIEW vw_PlayerMatches AS
SELECT 
    u.u_id AS PlayerID,
    t.t_name AS Name,
    m.round_num AS Round,
    g.format AS Format,
    CASE 
        WHEN g.format = 'Battle Royale' THEN 'Lobby' 
        ELSE ISNULL((
            SELECT TOP 1 p2.p_tag 
            FROM Match_Participants mp2 
            JOIN Player p2 ON mp2.p_id = p2.p_id 
            WHERE mp2.m_id = m.m_id AND mp2.p_id != u.u_id
        ), 'TBD') 
    END AS Opponent,
    CASE 
        WHEN g.format = 'Battle Royale' THEN mp.total_points
        ELSE mp.score_value 
    END AS Score,
    CASE 
        WHEN m.status != 'Completed' THEN 'Scheduled'
        WHEN mp.is_winner = 1 THEN 'Win'
        WHEN g.format = 'Battle Royale' THEN 'Rank #' + CAST(mp.placement AS VARCHAR)
        ELSE 'Loss'
    END AS Result
FROM Match_Participants mp
JOIN Match m ON mp.m_id = m.m_id
JOIN Tournament t ON m.t_id = t.t_id
JOIN Game g ON t.g_id = g.g_id
JOIN Users u ON mp.p_id = u.u_id;
GO

CREATE VIEW vw_EditTournaments AS SELECT t_id, t_name, entry_fee FROM Tournament WHERE status = 'Open';
GO

CREATE VIEW vw_PlayerTournaments AS
SELECT 
    r.p_id,      
    t.t_id, 
    t.t_name, 
    g.g_name, 
    r.status
FROM Registration r
JOIN Tournament t ON r.t_id = t.t_id
JOIN Game g ON t.g_id = g.g_id;
GO

CREATE VIEW vw_TournamentStandings AS
SELECT 
    t.t_name,   
    p.p_tag, 
    CASE 
        WHEN g.format = 'Battle Royale' THEN SUM(mp.total_points)
        ELSE COUNT(CASE WHEN mp.is_winner = 1 THEN 1 END) 
    END AS Score
FROM Match_Participants mp
JOIN Match m ON mp.m_id = m.m_id
JOIN Tournament t ON m.t_id = t.t_id
JOIN Game g ON t.g_id = g.g_id
JOIN Player p ON mp.p_id = p.p_id
GROUP BY t.t_name, p.p_tag, g.format;
GO

CREATE VIEW vw_PlayerProfile AS
SELECT 
    p.p_id,      
    p.p_tag, 
    u.email
FROM Player p
JOIN Users u ON p.p_id = u.u_id;
GO

----------------------------------------------------------------
-- STORED PROCEDURES
----------------------------------------------------------------
CREATE PROCEDURE sp_RegisterReferee
    @Name VARCHAR(50),
    @Email VARCHAR(100),
    @Password VARCHAR(255),
    @CNIC VARCHAR(15),
    @Experience INT,
    @GameSpecializationName VARCHAR(50)
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @GameID INT;
    SELECT @GameID = g_id FROM Game WHERE g_name = @GameSpecializationName;

    IF @GameID IS NULL
    BEGIN
        SELECT 0 AS Result, 'Invalid Game Specialization' AS Message;
        RETURN;
    END
    BEGIN TRANSACTION;
    BEGIN TRY
        DECLARE @NewUserID INT;
        
        INSERT INTO Users (name, email, password, CNIC, role)
        VALUES (@Name, @Email, @Password, @CNIC, 'referee');
        SET @NewUserID = SCOPE_IDENTITY(); 

        INSERT INTO Referee (r_id, salary, experience_in_years, specialization_id, status)
        VALUES (@NewUserID, 0, @Experience, @GameID,'Applicant'); 

        COMMIT TRANSACTION;
        SELECT 1 AS Result, 'Referee Registered Successfully' AS Message;
    
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
        SELECT 0 AS Result, ERROR_MESSAGE() AS Message;
    END CATCH
END
GO

CREATE PROCEDURE sp_RegisterPlayer
    @username VARCHAR(50),
    @Gamertag VARCHAR(50),
    @Email VARCHAR(100),
    @Password VARCHAR(255),
    @CNIC VARCHAR(15)
AS
BEGIN
    SET NOCOUNT ON;

    BEGIN TRANSACTION;
    BEGIN TRY
        DECLARE @NewUserID INT;
        
        INSERT INTO Users (name, email, password, CNIC, role)
        VALUES (@username, @Email, @Password, @CNIC, 'player');
        
        SET @NewUserID = SCOPE_IDENTITY(); 

        INSERT INTO Player (p_id, p_tag)
        VALUES (@NewUserID,@Gamertag); 

        COMMIT TRANSACTION;
        SELECT 1 AS Result, 'Account Created Successfully!' AS Message;
    
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
        SELECT 0 AS Result, ERROR_MESSAGE() AS Message;
    END CATCH
END
GO

CREATE PROCEDURE sp_RefereeStatus
    @Email NVARCHAR(100)
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @Status NVARCHAR(50);
    SELECT @Status = status FROM Referee WHERE r_id IN (SELECT u_id from Users where email = @Email);

    IF @Status = 'Applicant'
    BEGIN
        SELECT  0 AS result,'Referee Application Approval Pending' AS Message;
        RETURN;
    END
    SELECT 1 AS result,'success' AS Message;
    RETURN;
END
GO

CREATE PROCEDURE sp_ResetPassword
    @Email NVARCHAR(100),
    @NewPassword NVARCHAR(255)
AS
BEGIN
    SET NOCOUNT ON;
    
    BEGIN TRANSACTION;
    BEGIN TRY
        UPDATE login_check 
        SET password = @NewPassword 
        WHERE email = @Email;

        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END
GO

CREATE PROCEDURE sp_SubmitDispute
    @FiledBy INT,
    @ReportedGamertag VARCHAR(30),
    @Reason VARCHAR(200)
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @AgainstID INT;

    SELECT @AgainstID = p_id FROM Player WHERE p_tag = @ReportedGamertag;

    IF @AgainstID IS NULL
    BEGIN
        SELECT 0 AS Result, 'Player not found.' AS Message;
        RETURN;
    END

    IF @AgainstID = @FiledBy
    BEGIN
        SELECT 0 AS Result, 'Cannot report yourself.' AS Message;
        RETURN;
    END

    INSERT INTO Disputes (filed_by, against_player, reason, status, referee_id)
    VALUES (@FiledBy, @AgainstID, @Reason, 'pending', NULL);

    SELECT 1 AS Result, 'Dispute filed successfully.' AS Message;
END
GO

CREATE PROCEDURE sp_UpdatePlayerStats
    @MatchID INT,
    @Gamertag VARCHAR(30),
    @Kills INT,
    @Rank INT,
    @TotalPoints INT
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @PlayerID INT;
    SELECT @PlayerID = p_id FROM Player WHERE p_tag = @Gamertag;

    IF @PlayerID IS NOT NULL
    BEGIN
        UPDATE Match_Participants
        SET score_value = @Kills,
            placement = @Rank,
            total_points = @TotalPoints
        WHERE m_id = @MatchID AND p_id = @PlayerID;
    END
END
GO

CREATE PROCEDURE sp_FinalizeMatch
    @MatchID INT
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRANSACTION;

    DECLARE @TournamentID INT;
    DECLARE @Format VARCHAR(30);
    DECLARE @WinnerID INT;
    DECLARE @RoundNum INT;

    SELECT 
        @TournamentID = m.t_id,
        @Format = g.format,
        @RoundNum = m.round_num
    FROM Match m
    JOIN Tournament t ON m.t_id = t.t_id
    JOIN Game g ON t.g_id = g.g_id
    WHERE m.m_id = @MatchID;

    IF @Format = 'Battle Royale'
    BEGIN
        SELECT TOP 1 @WinnerID = p_id 
        FROM Match_Participants 
        WHERE m_id = @MatchID 
        ORDER BY placement ASC, total_points DESC;
    END
    ELSE
    BEGIN
        SELECT @WinnerID = winner_id FROM Match WHERE m_id = @MatchID;
    END

    UPDATE Match 
    SET status = 'Completed', 
        winner_id = @WinnerID,
        match_time = SYSDATETIME()
    WHERE m_id = @MatchID;

    DECLARE @IsLastMatch BIT = 0;

    IF @Format = 'Battle Royale'
    BEGIN
        SET @IsLastMatch = 1;
    END
    ELSE
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM Match WHERE t_id = @TournamentID AND winner_id IS NULL)
        BEGIN
            SET @IsLastMatch = 1;
        END
    END

    IF @IsLastMatch = 1 AND @WinnerID IS NOT NULL
    BEGIN
        UPDATE Tournament 
        SET status = 'Completed', 
            winner_id = @WinnerID 
        WHERE t_id = @TournamentID;
    END

    COMMIT TRANSACTION;
END
GO

CREATE PROCEDURE sp_ResolveDispute
    @DisputeID INT,
    @Action VARCHAR(20),     
    @RefereeID INT            
AS
BEGIN
    SET NOCOUNT ON;

    UPDATE Disputes
    SET status = @Action, 
        referee_id = @RefereeID,  
        resolved_at = SYSDATETIME()
    WHERE dispute_id = @DisputeID;
END
GO

CREATE PROCEDURE sp_CreateTournament
    @Name VARCHAR(60),
    @GameName VARCHAR(50),
    @Format VARCHAR(30),
    @EntryFee INT,
    @MaxPlayers INT,
    @StartDate DATE,
    @EndDate DATE,
    @Venue VARCHAR(60)
AS
BEGIN
    SET NOCOUNT ON;

    IF NOT EXISTS (SELECT 1 FROM Referee WHERE status = 'Hired')
    BEGIN
        THROW 51000, 'Cannot create tournament. No hired referees are available in the system.', 1;
    END

    DECLARE @GameID INT;
    SELECT @GameID = g_id FROM Game WHERE g_name = @GameName;

    IF @GameID IS NULL
    BEGIN
        THROW 51000, 'Game not found.', 1;
    END

    INSERT INTO Tournament (t_name, venue, g_id, start_date, end_date, entry_fee, max_players, status)
    VALUES (@Name, @Venue, @GameID, @StartDate, @EndDate, @EntryFee, @MaxPlayers, 'Open');
END
GO

CREATE PROCEDURE sp_AddGame
    @GameName VARCHAR(50),
    @Format VARCHAR(30)
AS
BEGIN
    SET NOCOUNT ON;
    
    IF EXISTS (SELECT 1 FROM Game WHERE g_name = @GameName)
    BEGIN
        SELECT 0 AS Result, 'Game already exists.' AS Message;
        RETURN;
    END

    INSERT INTO Game (g_name, format) VALUES (@GameName, @Format);
    
    SELECT 1 AS Result, 'Game added successfully.' AS Message;
END
GO

CREATE PROCEDURE sp_DeleteGame
    @GameID INT
AS
BEGIN
    SET NOCOUNT ON;
    DELETE FROM Game WHERE g_id = @GameID;
END
GO

CREATE PROCEDURE sp_CancelTournament
    @TournamentID INT
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE Tournament SET status = 'Cancelled' WHERE t_id = @TournamentID;
END
GO

CREATE PROCEDURE sp_ApproveReferee
    @RefereeID INT,
    @Salary DECIMAL(10, 2)
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE Referee 
    SET status = 'Hired', 
        salary = @Salary 
    WHERE r_id = @RefereeID;
END
GO

CREATE PROCEDURE sp_DeleteReferee
    @RefereeID INT
AS
BEGIN
    SET NOCOUNT ON;
    DELETE FROM Users WHERE u_id = @RefereeID; 
END
GO

CREATE PROCEDURE sp_BanPlayer
    @PlayerID INT
AS
BEGIN
    SET NOCOUNT ON;
    DELETE FROM Users WHERE u_id = @PlayerID;
END
GO

CREATE PROCEDURE sp_ApprovePayment
    @PaymentID INT
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRANSACTION;
    BEGIN TRY
        UPDATE Payment SET status = 'completed' WHERE pay_id = @PaymentID;
        
        UPDATE Registration SET status = 'approved' WHERE pay_id = @PaymentID;
        
        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END
GO

CREATE PROCEDURE sp_RejectPayment
    @PaymentID INT
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRANSACTION;
    BEGIN TRY
        UPDATE Payment SET status = 'failed' WHERE pay_id = @PaymentID;
        UPDATE Registration SET status = 'rejected' WHERE pay_id = @PaymentID;
        
        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END
GO

CREATE PROCEDURE sp_RegisterPaid
    @PlayerID INT,
    @TournamentID INT,
    @Amount INT,
    @ProofImage VARBINARY(MAX) 
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRANSACTION;
    
    DECLARE @NewPayID INT;

    INSERT INTO Payment (p_id, amount, status, proof_image)
    VALUES (@PlayerID, @Amount, 'pending', @ProofImage);

    SET @NewPayID = SCOPE_IDENTITY();

    INSERT INTO Registration (p_id, t_id, pay_id, status)
    VALUES (@PlayerID, @TournamentID, @NewPayID, 'pending');

    COMMIT TRANSACTION;
END
GO

CREATE PROCEDURE sp_HandleTournamentState
    @TournamentID INT
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @CurrentCount INT;
    DECLARE @MaxPlayers INT;
    DECLARE @CurrentStatus VARCHAR(20);
    DECLARE @StartDate DATE;
    DECLARE @Today DATE = CAST(SYSDATETIME() AS DATE);

    SELECT 
        @MaxPlayers = max_players,
        @CurrentStatus = status,
        @StartDate = start_date
    FROM Tournament
    WHERE t_id = @TournamentID;

    SELECT @CurrentCount = COUNT(*)
    FROM Registration
    WHERE t_id = @TournamentID
      AND status = 'approved';
      
    IF @CurrentCount >= @MaxPlayers
       AND @CurrentStatus = 'Open'
       AND @Today <= @StartDate
    BEGIN
        UPDATE Tournament
        SET status = 'Filled'
        WHERE t_id = @TournamentID;
        EXEC sp_StartReadyTournaments;

        RETURN;
    END
RETURN;
END
GO

CREATE PROCEDURE sp_StartReadyTournaments
AS
BEGIN
    SET NOCOUNT ON;
    EXEC sp_AutoCancelExpiredTournaments;
   
    DECLARE @WorkTable TABLE (
        RowID INT IDENTITY(1,1), 
        t_id INT,
        format VARCHAR(30)
    );

    INSERT INTO @WorkTable (t_id, format)
    SELECT t.t_id, g.format
    FROM Tournament t
    JOIN Game g ON t.g_id = g.g_id
    WHERE t.status = 'Filled' 
      AND t.start_date <= CAST(SYSDATETIME() AS DATE);

    DECLARE @i INT = 1;
    DECLARE @Count INT = (SELECT COUNT(*) FROM @WorkTable);
    DECLARE @CurrentTID INT;
    DECLARE @CurrentFormat VARCHAR(30);

    WHILE @i <= @Count
    BEGIN
        SELECT @CurrentTID = t_id, @CurrentFormat = format
        FROM @WorkTable
        WHERE RowID = @i;

        UPDATE Tournament 
        SET status = 'Ongoing' 
        WHERE t_id = @CurrentTID;

        IF @CurrentFormat = 'Knockout' 
        BEGIN
            EXEC sp_GenerateRound1 @CurrentTID;
        END
        ELSE IF @CurrentFormat = 'Battle Royale'
        BEGIN
            EXEC sp_GenerateBattleRoyaleMatch @CurrentTID;
        END

        SET @i = @i + 1;
    END
END
GO

CREATE PROCEDURE sp_GenerateBattleRoyaleMatch
    @TournamentID INT
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRANSACTION;

    DECLARE @DefaultRef INT = (SELECT TOP 1 r_id FROM Referee ORDER BY NEWID()); 

    INSERT INTO Match (t_id, r_id, status, round_num, match_time)
    VALUES (@TournamentID, @DefaultRef, 'Scheduled', 1, SYSDATETIME());

    DECLARE @MatchID INT = SCOPE_IDENTITY();

    INSERT INTO Match_Participants (m_id, p_id, score_value, placement, total_points)
    SELECT @MatchID, p_id, 0, 0, 0
    FROM Registration 
    WHERE t_id = @TournamentID AND status = 'approved';

    COMMIT TRANSACTION;
END
GO

CREATE PROCEDURE sp_GenerateRound1
    @TournamentID INT
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @Players TABLE (RowID INT IDENTITY(1,1), p_id INT);
    
    INSERT INTO @Players (p_id)
    SELECT p_id 
    FROM Registration 
    WHERE t_id = @TournamentID AND status = 'approved' 
    ORDER BY NEWID();

    DECLARE @Count INT = (SELECT COUNT(*) FROM @Players);
    DECLARE @DefaultRef INT = (SELECT TOP 1 r_id FROM Referee ORDER BY NEWID()); 

    DECLARE @i INT = 1;
    
    WHILE @i < @Count
    BEGIN
        DECLARE @P1 INT = (SELECT p_id FROM @Players WHERE RowID = @i);
        DECLARE @P2 INT = (SELECT p_id FROM @Players WHERE RowID = @i + 1);
        
        INSERT INTO Match (t_id, r_id, round_num, status)
        VALUES (@TournamentID, @DefaultRef, 1, 'Scheduled');
        
        DECLARE @NewMatchID INT = SCOPE_IDENTITY();

        INSERT INTO Match_Participants (m_id, p_id) VALUES (@NewMatchID, @P1);
        INSERT INTO Match_Participants (m_id, p_id) VALUES (@NewMatchID, @P2);

        SET @i = @i + 2;
    END
END
GO

CREATE PROCEDURE sp_GenerateNextRound
    @TournamentID INT,
    @CurrentRound INT
AS
BEGIN
    SET NOCOUNT ON;

    IF EXISTS (SELECT 1 FROM Match WHERE t_id = @TournamentID AND round_num = @CurrentRound + 1)
    BEGIN
        RETURN;
    END
    
    IF EXISTS (SELECT 1 FROM Tournament WHERE t_id = @TournamentID AND status = 'Completed')
    BEGIN
        RETURN;
    END

    DECLARE @WinnerCount INT;

    IF EXISTS (
        SELECT 1 
        FROM Match
        WHERE t_id = @TournamentID
          AND round_num = @CurrentRound
          AND winner_id IS NULL
    )
    BEGIN
        RETURN;
    END

    DECLARE @Winners TABLE (
        RowNum INT IDENTITY(1,1),
        p_id INT
    );

    INSERT INTO @Winners (p_id)
    SELECT winner_id
    FROM Match
    WHERE t_id = @TournamentID AND round_num = @CurrentRound
    ORDER BY m_id ASC;

    SELECT @WinnerCount = COUNT(*) FROM @Winners;

    IF @WinnerCount = 1
    BEGIN
        DECLARE @Champion INT = (SELECT p_id FROM @Winners);
        UPDATE Tournament
        SET winner_id = @Champion,
            status = 'Completed'
        WHERE t_id = @TournamentID;

        RETURN;
    END

    DECLARE @i INT = 1;
    DECLARE @DefaultRef INT = (SELECT TOP 1 r_id FROM Referee); 

    WHILE @i < @WinnerCount
    BEGIN
        DECLARE @P1 INT = (SELECT p_id FROM @Winners WHERE RowNum = @i);
        DECLARE @P2 INT = (SELECT p_id FROM @Winners WHERE RowNum = @i + 1);

        INSERT INTO Match (t_id, r_id, round_num, status)
        VALUES (@TournamentID, @DefaultRef, @CurrentRound + 1, 'Scheduled');

        DECLARE @NewMatchID INT = SCOPE_IDENTITY();

        INSERT INTO Match_Participants (m_id, p_id) VALUES (@NewMatchID, @P1);
        INSERT INTO Match_Participants (m_id, p_id) VALUES (@NewMatchID, @P2);

        SET @i = @i + 2;
    END
END
GO

CREATE PROCEDURE sp_AutoCancelExpiredTournaments
AS
BEGIN
    SET NOCOUNT ON;

    UPDATE Tournament
    SET status = 'Cancelled'
    WHERE t_id IN (
        SELECT t.t_id
        FROM Tournament t
        LEFT JOIN Registration r ON t.t_id = r.t_id AND r.status ='approved'
        WHERE 
            t.status = 'Open'              
            AND t.start_date < CAST(GETDATE() AS DATE)     
        GROUP BY t.t_id, t.max_players
        HAVING COUNT(r.reg_id) < t.max_players
    );
END
GO

----------------------------------------------------------------
-- TRIGGERS
----------------------------------------------------------------
CREATE TRIGGER trg_AutoDeclareMatchWinner
ON Match_Participants
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @MatchID INT;
    SELECT DISTINCT @MatchID = m_id FROM inserted;

    IF (SELECT COUNT(*) FROM Match_Participants WHERE m_id = @MatchID AND score_value IS NOT NULL) = (SELECT COUNT(*) FROM Match_Participants WHERE m_id = @MatchID)
    BEGIN
        DECLARE @WinnerID INT;
        
        SELECT TOP 1 @WinnerID = p_id 
        FROM Match_Participants 
        WHERE m_id = @MatchID 
        ORDER BY score_value DESC; 

        UPDATE Match 
        SET winner_id = @WinnerID, status = 'Completed' 
        WHERE m_id = @MatchID;
        
        UPDATE Match_Participants SET is_winner = 1 WHERE m_id = @MatchID AND p_id = @WinnerID;
    END
END
GO

CREATE TRIGGER trg_AutoStartTournament
ON Registration
AFTER INSERT, UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @TournamentID INT;

    SELECT @TournamentID = t_id FROM inserted;

    EXEC sp_HandleTournamentState @TournamentID;
END
GO

CREATE TRIGGER trg_GenerateNextRound
ON Match
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @TournamentID INT;
    DECLARE @CurrentRound INT;

    SELECT @TournamentID = t_id, @CurrentRound = round_num
    FROM inserted;

    EXEC sp_GenerateNextRound @TournamentID, @CurrentRound;
END
GO

CREATE TRIGGER trg_Referee_History_Insert
ON Referee
FOR INSERT
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @admin_id INT;

    SELECT  @admin_id = u_id
    FROM find_admin_id

    INSERT INTO History (user_id, entity, entity_id, action)
    SELECT @admin_id, 'Referee', i.r_id, 'New Referee Application Submitted'
    FROM inserted i
END;
GO

CREATE TRIGGER trg_Referee_History_update
ON Referee
FOR  UPDATE
AS
BEGIN 
    set nocount on;
    DECLARE @admin_id INT;

    SELECT  @admin_id = u_id FROM find_admin_id
    INSERT INTO History (user_id, entity, entity_id, action)
    SELECT @admin_id, 'Referee', i.r_id, 'Referee Status updated to: ' + i.status
    FROM inserted i
    INNER JOIN deleted d ON i.r_id = d.r_id
    WHERE i.status <> d.status;
END
GO

CREATE TRIGGER trg_Payment_History_Insert
ON Payment
FOR INSERT 
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO History (user_id, entity, entity_id, action)
    SELECT i.p_id, 'Payment', i.pay_id, 'Payment Initiated'
    FROM inserted i;
END;
GO

CREATE TRIGGER trg_Payment_History_Update
ON Payment
FOR UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    INSERT INTO History (user_id, entity, entity_id, action)
    SELECT i.p_id, 'Payment', i.pay_id, 'Payment Status updated to: ' + i.status
    FROM inserted i
    INNER JOIN deleted d ON i.pay_id = d.pay_id
    WHERE i.status <> d.status;
END;
GO

CREATE TRIGGER trg_Registration_History_Insert
ON Registration
FOR INSERT
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO History (user_id, entity, entity_id, action)
    SELECT i.p_id, 'Registration', i.reg_id, 'Registered for Tournament ID ' + CAST(i.t_id AS VARCHAR)
    FROM inserted i;
END;
GO

CREATE TRIGGER trg_Registration_History_Update
ON Registration
FOR UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO History (user_id, entity, entity_id, action)
    SELECT i.p_id, 'Registration', i.reg_id, 'Registration Status changed to: ' + i.status
    FROM inserted i
    INNER JOIN deleted d ON i.reg_id = d.reg_id
    WHERE i.status <> d.status;
END;
GO

CREATE TRIGGER trg_Registration_History_Delete
ON Registration
FOR DELETE
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO History (user_id, entity, entity_id, action)
    SELECT d.p_id, 'Registration', d.reg_id, 'Registration Deleted/Cancelled'
    FROM deleted d;
END;
GO

CREATE TRIGGER trg_Disputes_History_Insert
ON Disputes
FOR INSERT
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO History (user_id, entity, entity_id, action)
    SELECT i.filed_by, 'Disputes', i.dispute_id, 'Filed dispute against Player ID: ' + CAST(i.against_player AS VARCHAR)
    FROM inserted i;
END;
GO

CREATE TRIGGER trg_Disputes_History_Update
ON Disputes
FOR UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO History (user_id, entity, entity_id, action)
    SELECT i.referee_id, 'Disputes', i.dispute_id, 'Dispute Record Status Updated to:' + i.status
    FROM inserted i
    INNER JOIN deleted d ON i.dispute_id = d.dispute_id
    WHERE i.status <> d.status;
END;
GO

CREATE TRIGGER trg_Tournament_History_Insert
ON Tournament
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @admin_id INT
     SELECT  @admin_id = u_id
    FROM find_admin_id
    INSERT INTO History (user_id, entity, entity_id, action)
    SELECT @admin_id, 'Tournament', i.t_id, 'Tournament Created: ' + i.t_name
    FROM inserted i;
END;
GO

CREATE TRIGGER trg_Tournament_History_Update
ON Tournament
for UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @admin_id INT
     SELECT  @admin_id = u_id
    FROM find_admin_id
    INSERT INTO History (user_id, entity, entity_id, action)
    SELECT @admin_id, 'Tournament', i.t_id, 'Tournament Status updated to: ' + i.status
    FROM inserted i
    INNER JOIN deleted d ON i.t_id = d.t_id
    WHERE i.status <> d.status;
END;
GO

CREATE TRIGGER trg_Tournament_History_Delete
ON Tournament
for DELETE
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @admin_id INT
     SELECT  @admin_id = u_id
    FROM find_admin_id
    INSERT INTO History (user_id, entity, entity_id, action)
    SELECT @admin_id, 'Tournament', d.t_id, 'Tournament Deleted: ' + d.t_name
    FROM deleted d;
END;
GO

CREATE TRIGGER trg_Game_History_Insert
ON Game
for INSERT
AS
BEGIN
    SET NOCOUNT ON;
    declare @admin_id INT
     SELECT  @admin_id = u_id
    FROM find_admin_id
    INSERT INTO History (user_id, entity, entity_id, action)
    SELECT @admin_id, 'Game', i.g_id, 'New Game Added: ' + i.g_name
    FROM inserted i;
END;
GO

CREATE TRIGGER trg_Game_History_Delete
ON Game
for DELETE
AS
BEGIN
    SET NOCOUNT ON;
    declare @admin_id INT
    SELECT  @admin_id = u_id
    FROM find_admin_id
    INSERT INTO History (user_id, entity, entity_id, action)
    SELECT @admin_id, 'Game', d.g_id, 'Game Deleted: ' + d.g_name
    FROM deleted d;
END;
GO

CREATE TRIGGER trg_Player_History_Insert
ON Player
for INSERT
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO History (user_id, entity, entity_id, action)
    SELECT i.p_id, 'Player', i.p_id, 'New Player Registered: ' + i.p_tag
    FROM inserted i;
END;
GO

CREATE TRIGGER trg_Player_History_Delete
ON Player
FOR DELETE
AS
BEGIN
    SET NOCOUNT ON;
    declare @admin_id INT
    SELECT  @admin_id = u_id
    FROM find_admin_id
    INSERT INTO History (user_id, entity, entity_id, action)
    SELECT @admin_id, 'Player', d.p_id, 'Player Profile Deleted'
    FROM deleted d;
END;
GO