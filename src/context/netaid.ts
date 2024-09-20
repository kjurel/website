import { createClient } from '@supabase/supabase-js';

const supabaseUrl = 'https://izetyjbsztttkcwwswag.supabase.co';
const supabaseKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml6ZXR5amJzenR0dGtjd3dzd2FnIiwicm9sZSI6ImFub24iLCJpYXQiOjE2Nzk1OTY2NjEsImV4cCI6MTk5NTE3MjY2MX0.UYLgLfFSlE9qX3105mKHLfkNj75qh67Mk9HQm9szRwk"!;
export const supabase = createClient(supabaseUrl, supabaseKey);
