# Deploy Poros Portal to Vercel

## Quick Deploy (Easiest Method)

### Option 1: Deploy via Vercel Dashboard (Recommended)

1. **Go to Vercel**: https://vercel.com
2. **Sign in** with your GitHub account
3. **Click "Add New..."** → **"Project"**
4. **Import your repository**:
   - Select `poros-protocol` repository
   - Set **Root Directory** to: `portal`
5. **Configure Environment Variables**:
   ```
   NEXT_PUBLIC_BACKEND_URL=https://poros-protocol-production.up.railway.app
   NEXT_PUBLIC_APP_NAME=Poros Protocol
   NEXT_PUBLIC_APP_VERSION=2.0
   ```
6. **Click "Deploy"**
7. **Done!** Your site will be live at `https://your-project.vercel.app`

### Option 2: Deploy via Vercel CLI

```bash
# Install Vercel CLI (if not already installed)
npm install -g vercel

# Login to Vercel
cd c:/Users/aiden/poros-protocol/portal
vercel login

# Deploy to production
vercel --prod

# Follow the prompts:
# - Set up and deploy? Y
# - Which scope? (select your account)
# - Link to existing project? N
# - Project name? poros-portal
# - Directory? ./
# - Override settings? N
```

## Manual Steps (If Needed)

### 1. Build Test (Optional - test before deploying)

```bash
cd c:/Users/aiden/poros-protocol/portal
npm run build
npm start
```

Visit http://localhost:3000 to test the production build.

### 2. Configure Vercel Project

If deploying via dashboard, make sure to set:

**Framework Preset**: Next.js
**Root Directory**: `portal`
**Build Command**: `npm run build`
**Output Directory**: `.next`
**Install Command**: `npm install`

### 3. Environment Variables (Vercel Dashboard)

Go to your project → Settings → Environment Variables:

| Name | Value |
|------|-------|
| `NEXT_PUBLIC_BACKEND_URL` | `https://poros-protocol-production.up.railway.app` |
| `NEXT_PUBLIC_APP_NAME` | `Poros Protocol` |
| `NEXT_PUBLIC_APP_VERSION` | `2.0` |

## Post-Deployment

### Custom Domain (Optional)

1. Go to project Settings → Domains
2. Add your custom domain (e.g., `poros.com`)
3. Follow DNS configuration instructions

### Testing

After deployment, test:

1. **Landing Page**: `https://your-url.vercel.app`
2. **Register**: Create a new account
3. **Dashboard**: Should redirect to `/user/dashboard`
4. **Marketplace**: Browse agents
5. **Console**: Try chatting with an agent
6. **Profile**: Check your profile page

## Troubleshooting

### Issue: 404 on User Dashboard

**Fix**: This was a Next.js cache issue. Vercel will rebuild fresh and should work.

If issues persist:
1. Delete `.next` folder locally
2. Run `npm run build` to test
3. Push to GitHub
4. Redeploy on Vercel

### Issue: Environment Variables Not Working

**Fix**: Make sure you added them in Vercel Dashboard under Settings → Environment Variables, then redeploy.

### Issue: Build Fails

Check the build logs in Vercel dashboard. Common fixes:
- Make sure all dependencies are in `package.json`
- Check TypeScript errors
- Verify all imports are correct

## Current Status

✅ **Backend**: https://poros-protocol-production.up.railway.app (Railway)
✅ **Weather Agent**: https://positive-expression-production-8aa0.up.railway.app
🔄 **Frontend**: Ready to deploy to Vercel

## Next Steps After Deployment

1. Update README.md with your Vercel URL
2. Test all features end-to-end
3. Share the link!
4. (Optional) Add custom domain

---

**Need Help?**

Check Vercel docs: https://vercel.com/docs/deployments/overview
