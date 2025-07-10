📝 Product Requirements Document (PRD) — Moodly MVP
1. Overview
Moodly is a tween-friendly emotional journaling web app powered by AI. It helps users reflect on their moods, receive journaling prompts, and track emotional growth over time. The MVP will be built using Streamlit, OpenAI API, and optionally Spotify API for mood-based music suggestions.
2. Target Audience
- Tweens (ages 10–14)
- Educators and school counselors
- Parents seeking emotional wellness tools for kids
3. Core Features
- Mood Selector: Emoji-based or color-coded mood picker
- AI Journaling Prompts: Contextual prompts based on selected mood
- Daily Journal Entry: Text input with optional voice-to-text
- Mood Tracker: Visual timeline of mood entries
- Positive Reinforcement: Uplifting messages or music suggestions
- Privacy-first Design: No personal data stored; local journaling option
4. Tech Stack
- Frontend: Streamlit (for rapid prototyping)
- Backend: FastAPI (for rate limiting, caching, and API orchestration)
- AI Integration: OpenAI GPT for prompt generation
- Optional APIs: Spotify API for mood-based playlists
5. User Flow
- User logs in or accesses anonymously
- Selects mood from a visual picker
- Receives a journaling prompt
- Writes or records their entry
- Gets a motivational message or music suggestion
- Entry is saved locally or optionally synced
6. Success Metrics
- Daily active users
- Number of journal entries per user
- Mood improvement trends over time
- Educator feedback and adoption rate
7. Ethical Considerations
- No tracking or profiling
- Age-appropriate language and tone
- Option for parental or educator oversight
- Alignment with SDG goals (mental health, education, well-being)
