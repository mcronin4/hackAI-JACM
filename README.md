# 🦎 Chameleon - AI-Powered Content Adaptation Platform 
### Built in only 24 hours

> **🏆 Winner: Best AI Retrieval Project**  
> *Awarded 4 x $100 BestBuy gift cards for demonstrating the best implementation of contextual AI retrieval*
> https://devpost.com/software/chameleon-qpz6ru?_gl=1*1oio9uu*_gcl_au*MTI4ODI5ODAzNy4xNzUwNzE0MzY4*_ga*ODAyMzA1NDAxLjE3NTA3MTQzNjg.*_ga_0YHJK3Y10M*czE3NTA3MTQzNjgkbzEkZzEkdDE3NTA3MTY1NTMkajYwJGwwJGgw

## 🎯 Project Overview

Chameleon is a full-stack AI application that helps content creators automatically adapt their long-form content into platform-optimized social media posts. Built for the hackAI-JACM hackathon, this project demonstrates advanced AI retrieval and content generation capabilities.

### 🚀 What We Built

**Contextual AI Retrieval & Content Adaptation**: Our platform takes long-form content (articles, transcripts, videos) and intelligently extracts key topics, analyzes emotional context, and generates platform-specific social media posts optimized for X (Twitter) and LinkedIn.

### 🏆 Why We Won Best AI Retrieval Project

Our solution showcases sophisticated contextual AI retrieval by:
- **Intelligent Topic Extraction**: Using AI to identify and extract relevant topics from content
- **Emotional Context Analysis**: Understanding the emotional tone and sentiment of content
- **Platform-Specific Adaptation**: Generating content tailored to each platform's unique characteristics
- **Real-time Processing**: Streaming API for immediate feedback and content generation
- **Multi-format Support**: Processing text, YouTube videos, and transcripts

## 🛠️ Tech Stack

### Frontend
- **Next.js 15** with TypeScript
- **Tailwind CSS** for styling
- **Zustand** for state management
- **Supabase** for authentication and database
- **Lucide React** for icons

### Backend
- **FastAPI** with Python
- **Google Gemini AI** for content generation
- **LangGraph** for workflow orchestration
- **Supabase** for database operations
- **YouTube Transcript API** for video processing

### Database
- **Supabase** (PostgreSQL) with Row Level Security
- **Real-time subscriptions** for live updates

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ 
- Python 3.8+
- Supabase account
- Google AI Studio account (for Gemini API)

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/hackAI-JACM.git
cd hackAI-JACM
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp env.example .env
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment file
cp env.example .env.local
```

### 4. Environment Configuration

#### Backend (.env)
```env
# Google API Configuration
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_MODEL_NAME=gemini-2.5-flash
GOOGLE_TEMPERATURE=0.1

# Supabase Configuration
SUPABASE_URL=your_supabase_url_here
SUPABASE_ANON_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key_here
```

#### Frontend (.env.local)
```env
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url_here
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key_here

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 5. Database Setup

1. Create a new Supabase project
2. Run the SQL setup script in your Supabase SQL editor:

```sql
-- Copy the contents of supabase_setup.sql
-- This creates all necessary tables and RLS policies
```

### 6. Start the Application

#### Terminal 1 - Backend
```bash
cd backend
python main.py
```
Backend will be available at: http://localhost:8000

#### Terminal 2 - Frontend
```bash
cd frontend
npm run dev
```
Frontend will be available at: http://localhost:3000

## 🔑 Required API Keys

### Google AI Studio (Gemini)
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add to backend `.env` file

### Supabase
1. Create a new project at [Supabase](https://supabase.com)
2. Get your project URL and anon key from Settings > API
3. Add to both frontend and backend environment files

## 🎮 How to Use

### 1. Content Input
- **Text Mode**: Paste long-form content directly
- **YouTube Mode**: Paste YouTube URLs for automatic transcript extraction

### 2. Platform Selection
- Choose between X (Twitter) and LinkedIn
- Select multiple platforms for cross-posting

### 3. Content Generation
- Click "Start" to begin AI processing
- Watch real-time progress as topics are extracted and posts are generated

### 4. Post Management
- Click on any generated post to expand and edit
- Use the X logo button to send posts (placeholder for actual posting)
- Copy posts to clipboard for manual posting

## 🏗️ Architecture

### AI Pipeline
1. **Content Ingestion**: Text or YouTube video processing
2. **Topic Extraction**: AI identifies key themes and topics
3. **Emotional Analysis**: Sentiment and tone detection
4. **Platform Optimization**: Content adaptation for each platform
5. **Post Generation**: Final optimized posts with metadata

### Database Schema
- `user_info`: User profiles and authentication
- `longform_content`: Original content storage
- `generated_posts`: AI-generated social media posts
- `existing_context_posts`: Historical context for better generation

## 🚀 Features

### ✅ Implemented
- [x] Multi-platform content generation (X, LinkedIn)
- [x] YouTube video transcript extraction
- [x] Real-time streaming API
- [x] User authentication with Supabase
- [x] Responsive UI with smooth animations
- [x] Topic extraction and emotional analysis
- [x] Platform-specific content optimization

### 🔄 Future Enhancements
- [ ] Direct social media posting integration
- [ ] Image generation for posts
- [ ] Content scheduling
- [ ] Analytics dashboard
- [ ] Team collaboration features

## 🧪 Testing

### Backend API Testing
```bash
cd backend
python test_server.py
```

### Frontend Testing
```bash
cd frontend
npm run lint
```

## 📁 Project Structure

```
hackAI-JACM/
├── backend/
│   ├── app/
│   │   ├── agents/          # AI agents for content processing
│   │   ├── api/             # FastAPI routes
│   │   ├── services/        # Business logic
│   │   └── database/        # Database operations
│   ├── main.py              # FastAPI application entry
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── app/                 # Next.js app directory
│   ├── components/          # React components
│   ├── lib/                 # Utilities and configurations
│   └── package.json         # Node.js dependencies
└── supabase_setup.sql       # Database schema
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **hackAI-JACM** organizers for the amazing hackathon experience
- **Google AI Studio** for providing the Gemini API
- **Supabase** for the excellent backend-as-a-service platform
- **Next.js** and **FastAPI** communities for the robust frameworks

---

**Built with ❤️ during hackAI-JACM 2024** 
