# Self-Hosted Trophy Service Setup

## Step 1: Fork the Repository
Go to https://github.com/ryo-ma/github-profile-trophy and fork it to your account.

## Step 2: Get Your GitHub PAT
1. Go to https://github.com/settings/tokens
2. Create a new Personal Access Token (classic) with `public_repo` scope
3. Copy the token (you'll need it in Step 3)

## Step 3: Deploy to Vercel
### Option A: Via Vercel UI (Easiest)
1. Go to https://vercel.com/new
2. Import the forked `github-profile-trophy` repository
3. Add environment variables:
   - `GITHUB_TOKEN`: paste your PAT from Step 2
4. Deploy

### Option B: Via Vercel CLI
```bash
npm i -g vercel
cd your-forked-repo
vercel env add GITHUB_TOKEN  # paste your PAT
vercel --prod
```

## Step 4: Update README.md
Replace this line in your README:
```html
<img src="https://github-profile-trophy.vercel.app/?username=Pariseashishbannu&theme=tokyonight&no-frame=true&no-bg=true&row=1&column=6&margin-w=10" />
```

With your Vercel deployment URL:
```html
<img src="https://your-vercel-deployment-name.vercel.app/?username=Pariseashishbannu&theme=tokyonight&no-frame=true&no-bg=true&row=1&column=6&margin-w=10" />
```

Replace `your-vercel-deployment-name` with your actual Vercel project name.

## Step 5: Test
Visit your new URL in a browser to verify it works.

---

**Why this works:**
- Your own Vercel instance won't hit rate limits from shared traffic
- You control the GitHub token, so authentication won't fail
- Themes render reliably
- You can customize the service if needed

---

**Troubleshooting:**
- If you see "API rate limit exceeded", make sure the `GITHUB_TOKEN` env var is set in Vercel
- If trophies don't show, check that your GitHub account has public repos/followers
- Test the URL directly: `https://your-url.vercel.app/?username=Pariseashishbannu`
