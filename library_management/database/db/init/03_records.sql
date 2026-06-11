
-- Set search path to use our auth schema
SET search_path TO auth;

-- Insert roles
INSERT INTO auth.role (role_name) VALUES
('ADMIN'),
('USER'),
('SUPPORT'),
('MEMBER'),
('GUEST')
ON CONFLICT (role_name) DO NOTHING;

-- Insert users
INSERT INTO auth.user (first_name, last_name, phone, email) VALUES
('test_admin', 'test_admin', '1234177890', 'test.admin@example.com'),
('Alice', 'Smith', '1234567890', 'alice.smith@example.com'),
('Bob', 'Johnson', '2345678901', 'bob.johnson@example.com'),
('Charlie', 'Brown', '3456789012', 'charlie.brown@example.com')
ON CONFLICT (email) DO NOTHING;

-- Insert user roles
INSERT INTO auth.user_roles (user_id, role_id) VALUES
((SELECT id FROM auth.user WHERE email = 'test.admin@example.com'), (SELECT id FROM auth.role WHERE role_name = 'ADMIN')),
((SELECT id FROM auth.user WHERE email = 'alice.smith@example.com'), (SELECT id FROM auth.role WHERE role_name = 'ADMIN')),
((SELECT id FROM auth.user WHERE email = 'bob.johnson@example.com'), (SELECT id FROM auth.role WHERE role_name = 'ADMIN')),
((SELECT id FROM auth.user WHERE email = 'bob.johnson@example.com'), (SELECT id FROM auth.role WHERE role_name = 'USER')),
((SELECT id FROM auth.user WHERE email = 'charlie.brown@example.com'), (SELECT id FROM auth.role WHERE role_name = 'USER'))
ON CONFLICT (user_id, role_id) DO NOTHING;

-- Insert login credentials
INSERT INTO auth.login_credential (user_id, username, password_hash, salt) VALUES
-- securepassword123 with salt_0
((SELECT id FROM auth.user WHERE email = 'test.admin@example.com'), 'test_admin', 'pbkdf2_sha256$600000$salt_0$KXdEZ1WUBafW70AIgpQYmPSeawTGZ4mCz1zBD0x4J7k=', 'salt_0'),
-- securepassword123 with salt_1
((SELECT id FROM auth.user WHERE email = 'alice.smith@example.com'), 'alice_smith', 'pbkdf2_sha256$600000$salt_1$ZggqnCMhp5KNoI3f8KrM90PhAmB0aSGiABNnWOIyehA=', 'salt_1'),
-- securepassword123 with salt_2
((SELECT id FROM auth.user WHERE email = 'bob.johnson@example.com'), 'bob_johnson', 'pbkdf2_sha256$600000$salt_2$r7A/VE66u9HGoAqOCEwZRYfRauSkwAHcNdGGQ7xg+TA=', 'salt_2'),
-- securepassword123 with salt_3
((SELECT id FROM auth.user WHERE email = 'charlie.brown@example.com'), 'charlie_brown', 'pbkdf2_sha256$600000$salt_3$/R0op7yHH0RPYo0pWKnj9D3+rBu5XE7neCYMrhJ7yBU=', 'salt_3')
ON CONFLICT DO NOTHING;