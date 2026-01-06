CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cognito_id VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    email_verified BOOLEAN DEFAULT false,
    avatar_url VARCHAR(255)
);

CREATE TABLE chats (
    chat_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_by UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
	title VARCHAR(255) NOT NULL,
	share_code UUID NOT NULL DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE messages (
    message_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chat_id UUID NOT NULL REFERENCES chats(chat_id) ON DELETE CASCADE,
    sent_by UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE user_chat_mappings (
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    chat_id UUID NOT NULL REFERENCES chats(chat_id) ON DELETE CASCADE,
    joined_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (user_id, chat_id)
);

CREATE OR REPLACE FUNCTION add_chat_creator_to_mapping()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO user_chat_mappings (user_id, chat_id)
    VALUES (NEW.created_by, NEW.chat_id)
    ON CONFLICT DO NOTHING;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_add_chat_creator
AFTER INSERT ON chats
FOR EACH ROW
EXECUTE FUNCTION add_chat_creator_to_mapping();

CREATE INDEX idx_messages_chat_id ON messages(chat_id);
CREATE INDEX idx_user_chat_mappings_chat_id ON user_chat_mappings(chat_id);
