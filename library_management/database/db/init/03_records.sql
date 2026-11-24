-- 03_records.sql

-- Set search path to use our auth schema
SET search_path TO auth;

-- ------- Insert roles -------
INSERT INTO auth.role (role_name) VALUES
('ADMIN'),
('USER'),
('SUPPORT'),
('MEMBER'),
('GUEST'),
('TESTER')
ON CONFLICT (role_name) DO NOTHING;

-- ------- Insert users -------
WITH seed_users (first_name, last_name, phone, email) AS (
    VALUES
    ('Admin','Test','1000000001','test.admin@example.com'),
    ('Alice','Smith','1000000002','alice.smith@example.com'),
    ('Bob','Johnson','1000000003','bob.johnson@example.com'),
    ('Charlie','Brown','1000000004','charlie.brown@example.com'),
    ('Support','User','1000000005','support.user@example.com'),
    ('Guest','User','1000000006','guest.user@example.com'),
    ('Deleted','Credential','1000000007','deleted.user@example.com'),
    ('RoleRemoved','User','1000000008','role.removed@example.com'),
    ('RoleReassigned','User','2000000008','role.reassigned@example.com'),
    ('NoRole','User','1000000009','norole.user@example.com'),
    ('Expired','Token','1000000010','expired.user@example.com'),
    ('Active','Token','1000000011','active.user@example.com'),
    ('Revoked','Token','1000000012','revoked.user@example.com'),
    ('Rotated','Token','1000000013','rotated.user@example.com')
)
INSERT INTO auth.user (first_name, last_name, phone, email)
SELECT s.first_name, s.last_name, s.phone, s.email
FROM seed_users AS s
WHERE NOT EXISTS (
    SELECT 1 FROM auth.user AS u WHERE u.email = s.email
);

-- ------- Insert current user roles -------
-- The schema has no deleted_at column or unique user-role constraint.
WITH seed_user_roles (email, role_name) AS (
    VALUES
    ('test.admin@example.com', 'ADMIN'),
    ('alice.smith@example.com', 'USER'),
    ('bob.johnson@example.com', 'ADMIN'),
    ('bob.johnson@example.com', 'USER'),
    ('charlie.brown@example.com', 'MEMBER'),
    ('support.user@example.com', 'SUPPORT'),
    ('guest.user@example.com', 'GUEST'),
    ('role.reassigned@example.com', 'USER')
)
INSERT INTO auth.user_roles (user_id, role_id)
SELECT u.id, r.id
FROM seed_user_roles AS s
JOIN auth.user AS u ON u.email = s.email
JOIN auth.role AS r ON r.role_name = s.role_name
WHERE NOT EXISTS (
    SELECT 1
    FROM auth.user_roles AS ur
    WHERE ur.user_id = u.id AND ur.role_id = r.id
);

-- ------- Insert login credentials -------
INSERT INTO auth.login_credential (user_id, username, password_hash, salt) VALUES

-- securepassword123 with salt_0
((SELECT id FROM auth.user WHERE email = 'test.admin@example.com'), 'test_admin',
 'pbkdf2_sha256$600000$salt_0$KXdEZ1WUBafW70AIgpQYmPSeawTGZ4mCz1zBD0x4J7k=', 'salt_0'),

-- securepassword123 with salt_1
((SELECT id FROM auth.user WHERE email = 'alice.smith@example.com'), 'alice_smith',
 'pbkdf2_sha256$600000$salt_1$ZggqnCMhp5KNoI3f8KrM90PhAmB0aSGiABNnWOIyehA=', 'salt_1'),

-- securepassword123 with salt_2
((SELECT id FROM auth.user WHERE email = 'bob.johnson@example.com'), 'bob_johnson',
 'pbkdf2_sha256$600000$salt_2$r7A/VE66u9HGoAqOCEwZRYfRauSkwAHcNdGGQ7xg+TA=', 'salt_2'),

-- securepassword123 with salt_3
((SELECT id FROM auth.user WHERE email = 'charlie.brown@example.com'), 'charlie_brown',
 'pbkdf2_sha256$600000$salt_3$/R0op7yHH0RPYo0pWKnj9D3+rBu5XE7neCYMrhJ7yBU=', 'salt_3'),

((SELECT id FROM auth.user WHERE email='support.user@example.com'), 'support_user',
 'password_hash_support', 'salt_support'),

((SELECT id FROM auth.user WHERE email='guest.user@example.com'), 'guest_user',
 'password_hash_guest', 'salt_guest'),

((SELECT id FROM auth.user WHERE email='expired.user@example.com'), 'expired_user',
 'password_hash_expired', 'salt_expired'),

((SELECT id FROM auth.user WHERE email='active.user@example.com'), 'active_user',
 'password_hash_active','salt_active'),

((SELECT id FROM auth.user WHERE email='revoked.user@example.com'), 'revoked_user',
 'password_hash_revoked','salt_revoked'),

((SELECT id FROM auth.user WHERE email='rotated.user@example.com'),'rotated_user',
 'password_hash_rotated','salt_rotated')

ON CONFLICT DO NOTHING;

-- deleted.user@example.com intentionally has no login credential.
-- The schema has no deleted_at column to represent a soft-deleted credential.

-- ------- Insert Refresh Tokens -------
-- These are development fixtures, not production credentials.
INSERT INTO auth.refresh_token (user_id, token, expires_at)
SELECT u.id, 'ACTIVE_TOKEN', CURRENT_TIMESTAMP + INTERVAL '30 days'
FROM auth.user AS u
WHERE u.email = 'active.user@example.com'
    AND NOT EXISTS (
            SELECT 1 FROM auth.refresh_token AS rt WHERE rt.token = 'ACTIVE_TOKEN'
    );

INSERT INTO auth.refresh_token (user_id, token, expires_at)
SELECT u.id, 'EXPIRED_TOKEN', CURRENT_TIMESTAMP - INTERVAL '1 day'
FROM auth.user AS u
WHERE u.email = 'expired.user@example.com'
    AND NOT EXISTS (
            SELECT 1 FROM auth.refresh_token AS rt WHERE rt.token = 'EXPIRED_TOKEN'
    );

INSERT INTO auth.refresh_token (user_id, token, expires_at, revoked_at)
SELECT u.id, 'REVOKED_TOKEN', CURRENT_TIMESTAMP + INTERVAL '30 days',
             CURRENT_TIMESTAMP - INTERVAL '5 days'
FROM auth.user AS u
WHERE u.email = 'revoked.user@example.com'
    AND NOT EXISTS (
            SELECT 1 FROM auth.refresh_token AS rt WHERE rt.token = 'REVOKED_TOKEN'
    );

 -- Refresh Token Rotation Chain
BEGIN;

    DO $$
    DECLARE
        v_token_a_id BIGINT;
        v_token_b_id BIGINT;
        v_user_id BIGINT;
    BEGIN

        SELECT id
        INTO v_user_id
        FROM auth.user
        WHERE email = 'rotated.user@example.com';

        IF v_user_id IS NOT NULL AND NOT EXISTS (
            SELECT 1 FROM auth.refresh_token
            WHERE token IN ('ROTATION_TOKEN_A', 'ROTATION_TOKEN_B')
        ) THEN
            -- Token A (old token, now revoked)
            INSERT INTO auth.refresh_token
            (
                user_id,
                token,
                expires_at,
                revoked_at
            )
            VALUES
            (
                v_user_id,
                'ROTATION_TOKEN_A',
                CURRENT_TIMESTAMP + INTERVAL '30 days',
                CURRENT_TIMESTAMP - INTERVAL '10 days'
            )
            RETURNING id
            INTO v_token_a_id;

            -- Token B (new active token)
            INSERT INTO auth.refresh_token
            (
                user_id,
                token,
                expires_at
            )
            VALUES
            (
                v_user_id,
                'ROTATION_TOKEN_B',
                CURRENT_TIMESTAMP + INTERVAL '30 days'
            )
            RETURNING id
            INTO v_token_b_id;

            -- Link token chain
            UPDATE auth.refresh_token
            SET replaced_by_token_id = v_token_b_id
            WHERE id = v_token_a_id;
        END IF;

    END $$;

COMMIT;