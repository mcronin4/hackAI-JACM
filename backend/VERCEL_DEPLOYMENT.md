# Vercel Deployment Guide

This backend is configured to run on Vercel's serverless platform.

## Files Added for Vercel Compatibility

1. **`vercel.json`** - Vercel configuration file
2. **`api/index.py`** - Vercel-compatible entry point
3. **`.vercelignore`** - Files to exclude from deployment

## Environment Variables Required

Set these environment variables in your Vercel dashboard:

```
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_MODEL_NAME=gemini-2.5-flash
GOOGLE_TEMPERATURE=0.1
SUPABASE_URL=your_supabase_url_here
SUPABASE_ANON_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key_here
DEEPGRAM_API_KEY=your_deepgram_api_key_here
```

## Vercel-Specific Modifications

### YouTube Service
- Modified to use `/tmp` directory instead of local `downloads/` folder
- Files are automatically cleaned up after processing
- Audio files are processed in memory when possible

### Entry Point
- Created `api/index.py` as the main entry point for Vercel
- Properly configured CORS and path handling

## Deployment Steps

1. **Install Vercel CLI** (if not already installed):
   ```bash
   npm i -g vercel
   ```

2. **Deploy from the backend directory**:
   ```bash
   cd backend
   vercel
   ```

3. **Set environment variables**:
   ```bash
   vercel env add GOOGLE_API_KEY
   vercel env add SUPABASE_URL
   # ... add all other env vars
   ```

4. **Deploy production**:
   ```bash
   vercel --prod
   ```

## Important Notes

- **Function timeout**: Set to 300 seconds (5 minutes) for YouTube processing
- **File storage**: Only `/tmp` directory is writable
- **Memory limits**: Vercel has memory constraints for serverless functions
- **Cold starts**: First request may be slower due to cold start

## Testing the Deployment

After deployment, test these endpoints:

- `GET /` - Health check
- `GET /api/v1/health` - Service health
- `POST /api/v1/generate-posts` - Main pipeline
- `GET /docs` - API documentation

## Troubleshooting

1. **Import errors**: Ensure all dependencies are in `requirements.txt`
2. **Timeout errors**: Consider breaking down large operations
3. **Memory errors**: Large files may exceed Vercel's memory limits
4. **File not found errors**: Ensure you're using `/tmp` for temporary files

## Performance Considerations

- YouTube processing may be slower on Vercel due to cold starts
- Consider using faster models for better response times
- Large files may hit memory/time limits 