-- 03_records.sql

-- Set search path to use our auth schema
SET search_path TO auth;

-- ------- Insert roles -------
INSERT INTO auth.role (role_name) VALUES
('ADMIN'),
('USER'),
('SUPPORT'),
('MEMBER'),
('GUEST')
ON CONFLICT (role_name) DO NOTHING;

-- ------- Insert users -------
INSERT INTO auth.user (first_name, last_name, phone, email) VALUES
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
ON CONFLICT (email) DO NOTHING;

-- ------- Insert user roles -------
INSERT INTO auth.user_roles (user_id, role_id) VALUES

((SELECT id FROM auth.user WHERE email='test.admin@example.com'),
 (SELECT id FROM auth.role WHERE role_name='ADMIN')),

((SELECT id FROM auth.user WHERE email='alice.smith@example.com'),
 (SELECT id FROM auth.role WHERE role_name='USER')),

((SELECT id FROM auth.user WHERE email='bob.johnson@example.com'),
 (SELECT id FROM auth.role WHERE role_name='ADMIN')),

((SELECT id FROM auth.user WHERE email='bob.johnson@example.com'),
 (SELECT id FROM auth.role WHERE role_name='USER')),

((SELECT id FROM auth.user WHERE email='charlie.brown@example.com'),
 (SELECT id FROM auth.role WHERE role_name='MEMBER')),

((SELECT id FROM auth.user WHERE email='support.user@example.com'),
 (SELECT id FROM auth.role WHERE role_name='SUPPORT')),

((SELECT id FROM auth.user WHERE email='guest.user@example.com'),
 (SELECT id FROM auth.role WHERE role_name='GUEST'))

ON CONFLICT DO NOTHING;

-- Soft-deleted role assignment
INSERT INTO auth.user_roles (user_id, role_id, deleted_at) VALUES
(
 (SELECT id FROM auth.user WHERE email='role.removed@example.com'),
 (SELECT id FROM auth.role WHERE role_name='USER'),
 CURRENT_TIMESTAMP - INTERVAL '30 days'
)
ON CONFLICT DO NOTHING;

-- Soft-deleted role assignment, Reassign role
INSERT INTO auth.user_roles (user_id, role_id, deleted_at) VALUES
(
 (SELECT id FROM auth.user WHERE email='role.reassigned@example.com'),
 (SELECT id FROM auth.role WHERE role_name='USER'),
 CURRENT_TIMESTAMP - INTERVAL '30 days'
)
ON CONFLICT DO NOTHING;

INSERT INTO auth.user_roles (user_id, role_id) VALUES
(
 (SELECT id FROM auth.user WHERE email='role.reassigned@example.com'),
 (SELECT id FROM auth.role WHERE role_name='USER')
)
ON CONFLICT DO NOTHING;

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

-- Soft Deleted Credential
INSERT INTO auth.login_credential
(
    user_id,
    username,
    password_hash,
    salt,
    deleted_at
)
VALUES
(
 (SELECT id FROM auth.user WHERE email='deleted.user@example.com'), 'deleted_user',
 'password_hash_deleted','salt_deleted',
  CURRENT_TIMESTAMP - INTERVAL '60 days'
)
ON CONFLICT DO NOTHING;

-- ------- Insert Refresh Tokens -------
-- Active Token
INSERT INTO auth.refresh_token (user_id,token_hash,expires_at) VALUES
( (SELECT id FROM auth.user WHERE email='active.user@example.com'), 
  'ACTIVE_TOKEN_HASH', 
  CURRENT_TIMESTAMP + INTERVAL '30 days'
);

-- Expired Token
INSERT INTO auth.refresh_token (user_id,token_hash,expires_at) VALUES
( (SELECT id FROM auth.user WHERE email='expired.user@example.com'),
  'EXPIRED_TOKEN_HASH', 
  CURRENT_TIMESTAMP - INTERVAL '1 day'
);

 -- Revoken Token
INSERT INTO auth.refresh_token (user_id,token_hash,expires_at,revoked_at) VALUES
( (SELECT id FROM auth.user WHERE email='revoked.user@example.com'),
  'REVOKED_TOKEN_HASH',
  CURRENT_TIMESTAMP + INTERVAL '30 days',
  CURRENT_TIMESTAMP - INTERVAL '5 days'
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

        -- Token A (old token, now revoked)
        INSERT INTO auth.refresh_token
        (
            user_id,
            token_hash,
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
            token_hash,
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

    END $$;

COMMIT;