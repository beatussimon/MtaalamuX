// User types
export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  date_joined: string;
  verification_level: string | null;
}

export interface UserProfile {
  id: number;
  user: User;
  tier: UserTier;
  bio: string;
  avatar: string;
  interests: string;
  last_seen: string;
  theme: 'light' | 'dark';
  created_at: string;
  updated_at: string;
  is_basic: boolean;
  is_plus: boolean;
  is_premium: boolean;
  can_initiate_consultation: boolean;
  can_post_content: boolean;
  can_sell_items: boolean;
  display_tier: string;
}

export type UserTier = 'basic' | 'plus' | 'premium';

// Professional types
export interface Category {
  id: number;
  name: string;
  image: string | null;
  description: string;
  initials: string;
  professional_count: number;
  created_at: string;
  updated_at: string;
}

export interface Professional {
  id: number;
  user: User;
  field: Category | null;
  subfield: string;
  location: string;
  skills: string[];
  photo: string | null;
  hero_image: string | null;
  bio: string;
  is_verified: boolean;
  verification_level: 'green' | 'gold' | null;
  follower_count: number;
  average_rating: number;
  article_count: number;
  research_count: number;
  has_verification: boolean;
  display_verification: string;
  is_featured: boolean;
  allow_instant_messaging: boolean;
  linkedin_url: string | null;
  twitter_url: string | null;
  github_url: string | null;
  website_url: string | null;
  created_at: string;
  updated_at: string;
}

// Message types
export interface Conversation {
  id: number;
  participants: User[];
  subject: string;
  consultation_type: string;
  status: 'active' | 'closed' | 'completed';
  created_at: string;
  updated_at: string;
  last_message: Message | null;
  unread_count: number;
  consultation: number | null;
  consultation_status: ConsultationStatusInfo;
}

export interface Message {
  id: number;
  conversation: number;
  sender: User;
  content: string;
  file: string | null;
  file_size: number | null;
  image: string | null;
  timestamp: string;
  is_read: boolean;
  read_at: string | null;
  parent: number | null;
}

export interface ConsultationStatusInfo {
  has_consultation: boolean;
  status?: string;
  is_active?: boolean;
  is_within_time_bounds?: boolean;
  can_send_messages?: boolean;
  start_time?: string;
  end_time?: string;
}

// Article types
export interface Article {
  id: number;
  author: Professional;
  title: string;
  content: string;
  image: string | null;
  category: Category | null;
  publish_date: string;
  is_published: boolean;
  is_featured: boolean;
  views: number;
  like_count: number;
  is_liked: boolean;
  comments_count: number;
  shares: number;
  engagement_score: number;
  content_preview?: string;
  content_full?: string | null;
  access_level?: string;
  is_blurred?: boolean;
  updated_at: string;
}

// Research types
export interface Research {
  id: number;
  author: Professional;
  title: string;
  abstract: string;
  content: string;
  document: string | null;
  image: string | null;
  category: Category | null;
  tags: string[];
  publish_date: string;
  status: 'draft' | 'published' | 'archived';
  is_featured: boolean;
  views: number;
  like_count: number;
  is_liked: boolean;
  shares: number;
  engagement_score: number;
  content_preview?: string;
  content_full?: string | null;
  access_level?: string;
  is_blurred?: boolean;
  updated_at: string;
}

// Consultation types
export interface Consultation {
  id: number;
  client: User;
  expert: Professional;
  title: string;
  description: string;
  status: 'pending' | 'accepted' | 'rejected' | 'completed' | 'cancelled';
  start_time: string;
  end_time: string;
  created_at: string;
  updated_at: string;
}

export interface AvailabilitySlot {
  id: number;
  expert: number;
  start_time: string;
  end_time: string;
  is_booked: boolean;
  booked_by: number | null;
  created_at: string;
  updated_at: string;
}

// API Response types
export interface ApiResponse<T> {
  data: T;
  status: number;
  statusText: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface ApiError {
  detail?: string;
  non_field_errors?: string[];
  [key: string]: unknown;
}

// Auth types
export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  password2: string;
  first_name?: string;
  last_name?: string;
}

export interface AuthResponse {
  access: string;
  refresh: string;
  user: User;
}

export interface TokenPayload {
  token_type: string;
  exp: number;
  iat: number;
  jti: string;
  user_id: number;
  username: string;
}
