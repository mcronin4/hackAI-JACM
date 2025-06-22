-- Complete Database Setup for hackAI-JACM with X OAuth Integration

-- =====================================================
-- CREATE TABLES
-- =====================================================

-- User information table with X OAuth fields
CREATE TABLE IF NOT EXISTS public.user_info (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT,
    username TEXT,
    full_name TEXT,
    avatar_url TEXT,
    x_oauth_token TEXT,
    x_oauth_secret TEXT,
    x_user_id TEXT,
    x_handle TEXT,
    x_screen_name TEXT,
    x_profile_image_url TEXT,
    linkedin_handle TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Longform content table
CREATE TABLE IF NOT EXISTS public.longform_content (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Generated posts table
CREATE TABLE IF NOT EXISTS public.generated_posts (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    longform_id BIGINT REFERENCES public.longform_content(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    platform TEXT NOT NULL,
    was_posted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Existing context posts table
CREATE TABLE IF NOT EXISTS public.existing_context_posts (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    post_content TEXT,
    platform TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- LinkedIn tokens table
CREATE TABLE IF NOT EXISTS public.linkedin_tokens (
    linkedin_user_id TEXT PRIMARY KEY,
    access_token TEXT NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- ENABLE ROW LEVEL SECURITY
-- =====================================================

ALTER TABLE public.user_info ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.longform_content ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.generated_posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.existing_context_posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.linkedin_tokens ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- RLS POLICIES
-- =====================================================

-- User info policies
CREATE POLICY "Users can view their own user info" ON public.user_info
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own user info" ON public.user_info
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own user info" ON public.user_info
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own user info" ON public.user_info
    FOR DELETE USING (auth.uid() = user_id);

-- Longform content policies
CREATE POLICY "Users can view their own longform content" ON public.longform_content
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own longform content" ON public.longform_content
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own longform content" ON public.longform_content
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own longform content" ON public.longform_content
    FOR DELETE USING (auth.uid() = user_id);

-- Generated posts policies
CREATE POLICY "Users can view their own generated posts" ON public.generated_posts
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own generated posts" ON public.generated_posts
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own generated posts" ON public.generated_posts
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own generated posts" ON public.generated_posts
    FOR DELETE USING (auth.uid() = user_id);

-- Existing context posts policies
CREATE POLICY "Users can view their own existing context posts" ON public.existing_context_posts
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own existing context posts" ON public.existing_context_posts
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own existing context posts" ON public.existing_context_posts
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own existing context posts" ON public.existing_context_posts
    FOR DELETE USING (auth.uid() = user_id);

-- LinkedIn tokens policies
CREATE POLICY "Users can view their own LinkedIn tokens" ON public.linkedin_tokens
    FOR SELECT USING (auth.uid()::text = linkedin_user_id);

CREATE POLICY "Users can insert their own LinkedIn tokens" ON public.linkedin_tokens
    FOR INSERT WITH CHECK (auth.uid()::text = linkedin_user_id);

CREATE POLICY "Users can update their own LinkedIn tokens" ON public.linkedin_tokens
    FOR UPDATE USING (auth.uid()::text = linkedin_user_id);

CREATE POLICY "Users can delete their own LinkedIn tokens" ON public.linkedin_tokens
    FOR DELETE USING (auth.uid()::text = linkedin_user_id);

-- =====================================================
-- FUNCTIONS AND TRIGGERS
-- =====================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for updated_at on user_info
CREATE TRIGGER update_user_info_updated_at
    BEFORE UPDATE ON public.user_info
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Indexes for user_info
CREATE INDEX IF NOT EXISTS idx_user_info_user_id ON public.user_info(user_id);
CREATE INDEX IF NOT EXISTS idx_user_info_x_handle ON public.user_info(x_handle);
CREATE INDEX IF NOT EXISTS idx_user_info_email ON public.user_info(email);

-- Indexes for longform_content
CREATE INDEX IF NOT EXISTS idx_longform_content_user_id ON public.longform_content(user_id);
CREATE INDEX IF NOT EXISTS idx_longform_content_created_at ON public.longform_content(created_at);

-- Indexes for generated_posts
CREATE INDEX IF NOT EXISTS idx_generated_posts_user_id ON public.generated_posts(user_id);
CREATE INDEX IF NOT EXISTS idx_generated_posts_longform_id ON public.generated_posts(longform_id);
CREATE INDEX IF NOT EXISTS idx_generated_posts_platform ON public.generated_posts(platform);
CREATE INDEX IF NOT EXISTS idx_generated_posts_was_posted ON public.generated_posts(was_posted);

-- Indexes for existing_context_posts
CREATE INDEX IF NOT EXISTS idx_existing_context_posts_user_id ON public.existing_context_posts(user_id);
CREATE INDEX IF NOT EXISTS idx_existing_context_posts_platform ON public.existing_context_posts(platform);

-- Indexes for linkedin_tokens
CREATE INDEX IF NOT EXISTS idx_linkedin_tokens_user_id ON public.linkedin_tokens(linkedin_user_id);
CREATE INDEX IF NOT EXISTS idx_linkedin_tokens_expires_at ON public.linkedin_tokens(expires_at);

-- =====================================================
-- COMMENTS FOR DOCUMENTATION
-- =====================================================

COMMENT ON TABLE public.user_info IS 'Stores user profile information and OAuth tokens';
COMMENT ON TABLE public.longform_content IS 'Stores long-form content that will be used to generate posts';
COMMENT ON TABLE public.generated_posts IS 'Stores AI-generated posts from longform content';
COMMENT ON TABLE public.existing_context_posts IS 'Stores existing posts for context';
COMMENT ON TABLE public.linkedin_tokens IS 'Stores LinkedIn OAuth tokens';

COMMENT ON COLUMN public.user_info.x_oauth_token IS 'X (Twitter) OAuth access token';
COMMENT ON COLUMN public.user_info.x_oauth_secret IS 'X (Twitter) OAuth access token secret';
COMMENT ON COLUMN public.user_info.x_user_id IS 'X (Twitter) user ID';
COMMENT ON COLUMN public.user_info.x_handle IS 'X (Twitter) handle/username';
COMMENT ON COLUMN public.user_info.x_screen_name IS 'X (Twitter) screen name';
COMMENT ON COLUMN public.user_info.x_profile_image_url IS 'X (Twitter) profile image URL';

-- =====================================================
-- SAMPLE DATA (OPTIONAL - FOR TESTING)
-- =====================================================

-- Uncomment the following lines if you want to add sample data for testing
/*
INSERT INTO public.user_info (user_id, email, username, full_name, x_handle) 
VALUES (
    '00000000-0000-0000-0000-000000000000',
    'test@example.com',
    'testuser',
    'Test User',
    'testuser'
) ON CONFLICT (user_id) DO NOTHING;
*/ 