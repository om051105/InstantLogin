-- InstantLogin Database Schema
-- Phase 1: Core Authentication Tables

CREATE DATABASE IF NOT EXISTS instantlogin CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE instantlogin;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    user_id       INT           NOT NULL AUTO_INCREMENT,
    name          VARCHAR(128)  NOT NULL,
    email         VARCHAR(255)  NOT NULL,
    password_hash VARCHAR(255)  NOT NULL,
    account_status ENUM('active','locked','suspended','unverified') NOT NULL DEFAULT 'active',
    failed_attempts INT          NOT NULL DEFAULT 0,
    created_at    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login    DATETIME      NULL,
    PRIMARY KEY (user_id),
    UNIQUE KEY uq_users_email (email),
    INDEX idx_users_account_status (account_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Sessions table
CREATE TABLE IF NOT EXISTS sessions (
    session_id         VARCHAR(64)  NOT NULL,
    user_id            INT          NOT NULL,
    created_at         DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at         DATETIME     NOT NULL,
    status             ENUM('active','expired','logged_out') NOT NULL DEFAULT 'active',
    device             VARCHAR(255) NULL,
    browser            VARCHAR(255) NULL,
    ip_address         VARCHAR(45)  NULL,
    refresh_token_hash VARCHAR(255) NULL,
    PRIMARY KEY (session_id),
    INDEX idx_sessions_user_id (user_id),
    INDEX idx_sessions_status (status),
    CONSTRAINT fk_sessions_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Login attempts table (used by ML module in Phase 2)
CREATE TABLE IF NOT EXISTS login_attempts (
    attempt_id      INT         NOT NULL AUTO_INCREMENT,
    user_id         INT         NULL,
    timestamp       DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    success         TINYINT(1)  NOT NULL DEFAULT 0,
    error_code      ENUM('NONE','INVALID_PASSWORD','INVALID_USERNAME','ACCOUNT_LOCKED',
                         'SESSION_EXPIRED','MFA_FAILURE','NETWORK_ERROR','SERVER_ERROR',
                         'SUSPICIOUS_ACTIVITY','RATE_LIMITED') NOT NULL DEFAULT 'NONE',
    ip_address      VARCHAR(45) NULL,
    device          VARCHAR(255) NULL,
    browser         VARCHAR(255) NULL,
    response_time_ms FLOAT      NULL,
    PRIMARY KEY (attempt_id),
    INDEX idx_attempts_user_id (user_id),
    INDEX idx_attempts_timestamp (timestamp),
    INDEX idx_attempts_success (success),
    CONSTRAINT fk_attempts_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Security events table (audit trail)
CREATE TABLE IF NOT EXISTS security_events (
    event_id    INT          NOT NULL AUTO_INCREMENT,
    user_id     INT          NULL,
    event_type  ENUM('LOGIN_SUCCESS','LOGIN_FAILURE','LOGOUT','ACCOUNT_LOCKED','ACCOUNT_UNLOCKED',
                     'RATE_LIMITED','SUSPICIOUS_ACTIVITY','PASSWORD_CHANGED','SESSION_EXPIRED','REGISTRATION')
                NOT NULL,
    severity    ENUM('INFO','WARNING','HIGH','CRITICAL') NOT NULL DEFAULT 'INFO',
    timestamp   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    description TEXT         NULL,
    ip_address  VARCHAR(45)  NULL,
    PRIMARY KEY (event_id),
    INDEX idx_events_user_id (user_id),
    INDEX idx_events_type (event_type),
    INDEX idx_events_severity (severity),
    INDEX idx_events_timestamp (timestamp),
    CONSTRAINT fk_events_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Seed: Demo admin user (password: Admin@1234)
-- Hash generated with bcrypt rounds=12
INSERT IGNORE INTO users (name, email, password_hash, account_status) VALUES
(
    'Admin User',
    'admin@instantlogin.dev',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TiGgGgJf6dYUi.9/IbPXkKbFO.yO',
    'active'
);
