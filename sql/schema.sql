-- =====================================================
-- Forge Database Starter Schema
-- Version: 0.1
-- =====================================================

CREATE DATABASE IF NOT EXISTS forge_database;
USE forge_database;

-- =====================================================
-- ERAS
-- =====================================================

CREATE TABLE eras (
    era_id INT AUTO_INCREMENT PRIMARY KEY,
    era_name VARCHAR(100) NOT NULL UNIQUE,
    era_order INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- BUILDINGS
-- =====================================================

CREATE TABLE buildings (
    building_id INT AUTO_INCREMENT PRIMARY KEY,
    building_name VARCHAR(255) NOT NULL,
    building_type ENUM(
        'Residential',
        'Production',
        'Goods',
        'Military',
        'Cultural',
        'Decoration',
        'Road',
        'Great Building',
        'Special'
    ) NOT NULL,
    era_id INT,
    width INT NOT NULL,
    depth INT NOT NULL,
    population INT DEFAULT 0,
    happiness INT DEFAULT 0,
    FOREIGN KEY (era_id)
        REFERENCES eras(era_id)
);

-- =====================================================
-- UNITS
-- =====================================================

CREATE TABLE units (
    unit_id INT AUTO_INCREMENT PRIMARY KEY,
    unit_name VARCHAR(255) NOT NULL,
    era_id INT NOT NULL,
    unit_class VARCHAR(100),
    attack_value INT,
    defense_value INT,
    movement INT,
    range_value INT,
    FOREIGN KEY (era_id)
        REFERENCES eras(era_id)
);

-- =====================================================
-- QUESTS
-- =====================================================

CREATE TABLE quests (
    quest_id INT AUTO_INCREMENT PRIMARY KEY,
    quest_name VARCHAR(255) NOT NULL,
    era_id INT,
    quest_type VARCHAR(100),
    description TEXT,
    FOREIGN KEY (era_id)
        REFERENCES eras(era_id)
);

-- =====================================================
-- REWARDS
-- =====================================================

CREATE TABLE rewards (
    reward_id INT AUTO_INCREMENT PRIMARY KEY,
    reward_name VARCHAR(255) NOT NULL,
    reward_type VARCHAR(100),
    quantity INT DEFAULT 1
);

-- =====================================================
-- QUEST REWARDS
-- =====================================================

CREATE TABLE quest_rewards (
    quest_id INT,
    reward_id INT,
    PRIMARY KEY (quest_id, reward_id),
    FOREIGN KEY (quest_id)
        REFERENCES quests(quest_id)
        ON DELETE CASCADE,
    FOREIGN KEY (reward_id)
        REFERENCES rewards(reward_id)
        ON DELETE CASCADE
);

-- =====================================================
-- BATTLE RESULTS
-- =====================================================

CREATE TABLE battle_results (
    battle_id INT AUTO_INCREMENT PRIMARY KEY,
    battle_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    attacking_unit_id INT,
    defending_unit_id INT,
    winner_unit_id INT,
    rounds_fought INT,
    FOREIGN KEY (attacking_unit_id)
        REFERENCES units(unit_id),
    FOREIGN KEY (defending_unit_id)
        REFERENCES units(unit_id),
    FOREIGN KEY (winner_unit_id)
        REFERENCES units(unit_id)
);
