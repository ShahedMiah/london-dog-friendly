# 🐕 London Dog-Friendly Directory Web App

A Next.js application that allows users to export comprehensive dog-friendly venue data from London via a simple web interface.

## ✨ Features

- **One-Click Export**: Click "Start Data Export" to scrape 800+ venues
- **Real-time Progress**: Live updates showing scraping progress
- **Automatic Download**: CSV file automatically generated and downloadable
- **Comprehensive Data**: Restaurants, hotels, attractions, and services
- **Professional UI**: Clean, responsive design built with Tailwind CSS

## 🚀 Quick Start

### Development
```bash
npm run dev
```
Visit: http://localhost:3000

### Production Build
```bash
npm run build
npm start
```

## 📊 Data Export Process

1. **Click Export**: User clicks "Start Data Export" button
2. **Live Scraping**: App scrapes BringFido.com in real-time
3. **Progress Updates**: Shows current status, venues processed, etc.
4. **CSV Generation**: Creates downloadable CSV file with all data
5. **Download**: User can download the complete dataset

## 🎯 Vercel Deployment

### Option 1: Connect to GitHub (Recommended)
1. Push this code to your GitHub repository
2. In Vercel dashboard, import the GitHub repository
3. Vercel will automatically detect Next.js and deploy

### Option 2: Deploy from Local
```bash
npx vercel --prod
```

## 🔧 Environment Variables (Optional)

No environment variables required for basic functionality.

## 📁 File Structure

```
nextjs-app/
├── app/
│   ├── api/export/route.ts    # Scraping API endpoint
│   ├── globals.css            # Tailwind styles
│   ├── layout.tsx             # Root layout
│   └── page.tsx               # Main export interface
├── public/                    # Static files & generated CSVs
├── package.json               # Dependencies
└── next.config.js             # Next.js configuration
```

## 🎨 Tech Stack

- **Framework**: Next.js 14 with App Router
- **Styling**: Tailwind CSS
- **Scraping**: Playwright (Chromium)
- **Data Export**: CSV Writer
- **TypeScript**: Full type safety
- **Deployment**: Vercel

## 🔍 What Gets Exported

The CSV includes:
- **Business Info**: Name, description, category
- **Contact Details**: Phone, email, website
- **Location**: Full address, GPS coordinates
- **Source Data**: Venue ID, original BringFido URL

## ⚡ Performance Notes

- **Scraping Time**: 4-6 hours for complete dataset
- **Progress Updates**: Real-time streaming updates
- **Browser**: Runs headless Chromium for efficiency
- **Rate Limiting**: Respectful delays between requests

## 🚀 Deployment to Vercel

This app is ready for immediate Vercel deployment:

1. **Push to GitHub** (if not already done)
2. **Import to Vercel** from your GitHub repo
3. **Deploy** - No additional configuration needed!

The app will automatically handle the scraping and file generation in Vercel's serverless environment.

---

**Ready to deploy?** Just push to GitHub and import to Vercel! 🚀