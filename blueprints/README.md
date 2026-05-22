# Blueprint Overview (Creative Blog & YouTube Automation)

> **Location:** `blueprints/`

## 📂 Structure
```
blueprints/
├─ creative/
│   ├─ blog/
│   │   ├─ README.md                # Quick‑start guide for the blog workflow (already exists)
│   │   ├─ TEMPLATE.md              # Skeleton markdown for a new post
│   │   └─ publish_blog.sh          # Full automation script (draft → Medium → archive)
│   └─ youtube/
│       └─ README.md                # Video production blueprint & agent‑skill list
└─ roadmap.md                       # Project roadmap (existing)
```

## 🎯 Goal
Provide an **agent‑first**, repeatable pipeline that:
1. Generates a blog post skeleton.
2. Lets you edit, publish to Medium, and archive the source.
3. Optionally records a short video, uploads it to YouTube, and links it back to the post.
4. Exposes the whole process via clear **metadata** (`META.md`) so downstream AI agents can discover and cite both the article and video.

## 🛠️ How to Use
### 1️⃣ Install prerequisites (once)
```bash
# macOS – Homebrew is assumed installed
brew install jq ffmpeg obs   # optional OBS for video capture
pip install --user google-api-python-client oauth2client  # for YouTube API script
```
### 2️⃣ Set Medium credentials (once per machine)
```bash
export MEDIUM_TOKEN="<your‑medium‑api‑token>"
export MEDIUM_USER_ID="<your‑medium‑user‑id>"
```
### 3️⃣ Run the blog automation
```bash
cd /Users/jessburnett/www/governance/blueprints
./creative/blog/publish_blog.sh \
    "Your Post Title" \
    "slug‑optional" \
    "tag1,tag2,tag3" \
    "path/to/cover.png"
```
The script will:
- Create `creative/blog/drafts/<date>-<slug>/index.md` from `TEMPLATE.md`.
- Insert the `<!-- agent-context … -->` comment.
- Open the file in VS Code for you to finish TL;DR, code, etc.
- Publish to Medium via the API.
- Write `META.md` with URL, tags, cover, and date.
- Move the finished folder to `creative/blog/published/`.

### 4️⃣ (Optional) Record a YouTube video
Follow the instructions in `creative/youtube/README.md`:
1. Record the screen while you run the script.
2. Trim/caption with `ffmpeg`.
3. Upload using the provided Python snippet or manually.
4. Add `video_url: https://youtu.be/…` to the post’s `META.md`.

## 🤖 Agent‑Friendly Signals
- **HTML comment** at the top of every post: `<!-- agent-context: <comma‑separated‑tags> -->`.
- **META.md** holds structured data (URL, tags, cover, video URL) for easy parsing.
- The YouTube README also lists the **agent skills** (screen‑capture, audio cleanup, video editing, metadata generation, YouTube API) so downstream bots can understand what is required to reproduce the video.

## 📚 Maintenance
- Update `publish_blog.sh` when Medium API changes.
- Add new tags or modify the `agent-context` comment whenever the content focus shifts.
- Keep the `youtube/README.md` up‑to‑date with any new tooling (e.g., a different recorder).

---
*All steps are designed to be run from the repository root, version‑controlled, and safe for automated agents to invoke.*
