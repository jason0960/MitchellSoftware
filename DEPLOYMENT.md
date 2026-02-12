# Deployment Guide

This portfolio website is ready to be deployed on any static hosting platform. Here are the most popular options:

## Option 1: GitHub Pages (Recommended - Free)

1. Go to your repository on GitHub: https://github.com/jason0960/MitchellSoftware
2. Click on **Settings** → **Pages**
3. Under "Build and deployment":
   - Source: Deploy from a branch
   - Branch: Select `copilot/create-portfolio-website` (or merge to `main` and use `main`)
   - Folder: `/ (root)`
4. Click **Save**
5. Wait a few minutes, then visit: `https://jason0960.github.io/MitchellSoftware/`

## Option 2: Netlify (Free)

1. Sign up at https://netlify.com
2. Click "Add new site" → "Import an existing project"
3. Connect your GitHub account and select this repository
4. Configure settings:
   - Branch: `copilot/create-portfolio-website`
   - Build command: (leave empty)
   - Publish directory: `/`
5. Click "Deploy site"
6. Your site will be live at a netlify.app subdomain (can customize)

## Option 3: Vercel (Free)

1. Sign up at https://vercel.com
2. Click "Add New..." → "Project"
3. Import your GitHub repository
4. Configure settings:
   - Framework Preset: Other
   - Root Directory: `./`
   - Build Command: (leave empty)
   - Output Directory: (leave empty)
5. Click "Deploy"
6. Your site will be live at a vercel.app subdomain (can customize)

## Option 4: Custom Domain

If you have your own domain:

1. Deploy using any of the above methods
2. Configure custom domain in the platform's settings
3. Update your domain's DNS records (platform will provide instructions)

## Testing Locally

To test the website locally before deployment:

```bash
# Using Python (Python 3)
python3 -m http.server 8000

# Using Node.js
npx http-server

# Using PHP
php -S localhost:8000
```

Then open http://localhost:8000 in your browser.

## Customization

Before deploying, you may want to customize:

1. **Contact Information** in `index.html`:
   - Email address
   - LinkedIn URL
   - GitHub username

2. **Projects** in `index.html`:
   - Replace placeholder projects with your actual work
   - Update project links and descriptions

3. **About Section**:
   - Customize statistics (years of experience, projects completed)
   - Update the bio text

4. **Skills**:
   - Add or remove skills based on your expertise
   - Reorder categories if needed

5. **Colors** in `styles.css`:
   - Modify CSS custom properties in `:root` section
   - Change gradient colors for hero section

## Performance Optimization

The website is already optimized, but for even better performance:

1. Minify CSS and JavaScript (optional for such a small site)
2. Add CDN for Font Awesome (already implemented)
3. Enable caching headers on your hosting platform
4. Consider adding a service worker for offline support

## SEO Tips

1. Update meta description in `index.html`
2. Add Open Graph tags for social media sharing
3. Create a sitemap.xml
4. Submit your site to Google Search Console
5. Add Google Analytics if you want to track visitors

## Support

If you encounter any issues, feel free to:
- Open an issue on GitHub
- Check the platform's documentation
- Review browser console for any JavaScript errors
