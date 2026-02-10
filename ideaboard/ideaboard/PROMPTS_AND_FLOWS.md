# Prompts and Key Flows

## Prompt Summary (High-Level)
- Create a new idea board app with realtime collaboration.
- Choose a stack and scaffold the project.
- Implement realtime collaboration and persistence.
- Configure Supabase and deploy to Vercel.
- Fix hydration issues, copy-to-clipboard, and join/add feedback.
- Document database schema and setup steps.
- Push to GitHub and deploy.

## Key User Flows

### Board Access
1) App loads and generates or restores a board code.
2) User shares the board code with collaborators.
3) Collaborator opens the app and joins using the code.

### Realtime Collaboration
1) Client loads ideas for the board from Supabase.
2) Client subscribes to realtime changes on the `ideas` table.
3) Add/update/delete operations broadcast to all connected clients.

### Idea Lifecycle
- Add: user enters title + optional details → insert to Supabase.
- Move: user clicks left/right → update column in Supabase.
- Edit: user changes title/details → update Supabase row.
- Delete: user removes idea → delete row in Supabase.

### Deployment
1) Push code to GitHub.
2) Import repo in Vercel.
3) Add env vars for Supabase.
4) Deploy and share URL.

## Key Files
- src/app/page.tsx: UI + client logic + realtime subscriptions.
- src/lib/supabaseClient.ts: Supabase client init + config guard.
- src/app/layout.tsx: app metadata and base layout.
- src/app/globals.css: global styles.
- README.md: setup + database schema.
