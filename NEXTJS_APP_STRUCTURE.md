# 🏗️ Next.js Application Structure

## 📁 Complete Project Structure
```
london-dog-friendly/
├── 📊 DATA (Current)
│   ├── scrape_bringfido_production.py
│   ├── gd_place_*.csv
│   └── extract_current_data.py
│
├── 🌐 WEB APPLICATION (To Create)
│   ├── app/
│   │   ├── layout.tsx                 # Root layout
│   │   ├── page.tsx                   # Homepage with map
│   │   ├── venues/
│   │   │   ├── page.tsx              # Venues list
│   │   │   └── [id]/page.tsx         # Individual venue
│   │   ├── search/page.tsx           # Advanced search
│   │   ├── categories/
│   │   │   └── [category]/page.tsx   # Category pages
│   │   └── api/
│   │       ├── venues/
│   │       │   ├── route.ts          # GET all venues
│   │       │   └── [id]/route.ts     # GET single venue
│   │       ├── search/route.ts       # Search API
│   │       └── categories/route.ts   # Categories API
│   │
│   ├── components/
│   │   ├── Map/
│   │   │   ├── InteractiveMap.tsx    # Main map component
│   │   │   ├── VenueMarker.tsx       # Map markers
│   │   │   └── MapCluster.tsx        # Marker clustering
│   │   ├── Venue/
│   │   │   ├── VenueCard.tsx         # Venue display card
│   │   │   ├── VenueDetails.tsx      # Full venue details
│   │   │   └── VenueList.tsx         # List of venues
│   │   ├── Search/
│   │   │   ├── SearchBox.tsx         # Text search
│   │   │   ├── FilterPanel.tsx       # Category filters
│   │   │   └── SortOptions.tsx       # Sort controls
│   │   └── ui/
│   │       ├── Button.tsx            # Reusable button
│   │       ├── Card.tsx              # Card component
│   │       └── Input.tsx             # Form inputs
│   │
│   ├── lib/
│   │   ├── database.ts               # Database connection
│   │   ├── csv-import.ts            # Import CSV data
│   │   └── types.ts                 # TypeScript types
│   │
│   ├── styles/
│   │   └── globals.css              # Global styles + Tailwind
│   │
│   └── public/
│       ├── images/                  # Venue images
│       └── icons/                   # Category icons
│
├── 📄 CONFIGURATION
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── .env.example
│
└── 📚 DOCUMENTATION
    ├── README.md
    ├── DEPLOY_TO_PRODUCTION.md
    └── CONTRIBUTING.md
```

## 🎨 Key Components to Build

### 1. Homepage (app/page.tsx)
```tsx
export default function HomePage() {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="bg-blue-600 text-white py-12">
        <h1>🐕 London Dog-Friendly Directory</h1>
        <p>Discover 800+ dog-friendly venues across London</p>
        <SearchBox />
      </section>
      
      {/* Interactive Map */}
      <section className="h-96">
        <InteractiveMap venues={featuredVenues} />
      </section>
      
      {/* Quick Categories */}
      <section className="py-8">
        <CategoryGrid />
      </section>
    </div>
  )
}
```

### 2. Interactive Map Component
```tsx
'use client'
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'

export default function InteractiveMap({ venues }) {
  return (
    <MapContainer center={[51.5074, -0.1278]} zoom={11}>
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      {venues.map(venue => (
        <VenueMarker key={venue.id} venue={venue} />
      ))}
    </MapContainer>
  )
}
```

### 3. API Routes (app/api/venues/route.ts)
```tsx
import { NextRequest } from 'next/server'
import { getVenues } from '@/lib/database'

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url)
  const category = searchParams.get('category')
  const search = searchParams.get('search')
  
  const venues = await getVenues({ category, search })
  
  return Response.json(venues)
}
```

### 4. Database Schema (Vercel Postgres)
```sql
CREATE TABLE venues (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  category VARCHAR(50),
  street VARCHAR(255),
  city VARCHAR(100),
  postcode VARCHAR(20),
  latitude DECIMAL(10, 8),
  longitude DECIMAL(11, 8),
  phone VARCHAR(50),
  email VARCHAR(255),
  website VARCHAR(500),
  rating DECIMAL(3, 2),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_venues_category ON venues(category);
CREATE INDEX idx_venues_location ON venues(latitude, longitude);
```

## 🔧 Essential Dependencies

### Core Framework
```json
{
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.0.0",
    "react-dom": "^18.0.0",
    "typescript": "^5.0.0"
  }
}
```

### UI & Styling
```json
{
  "dependencies": {
    "tailwindcss": "^3.3.0",
    "@headlessui/react": "^1.7.0",
    "@heroicons/react": "^2.0.0",
    "clsx": "^2.0.0"
  }
}
```

### Maps & Data
```json
{
  "dependencies": {
    "react-leaflet": "^4.2.0",
    "leaflet": "^1.9.0",
    "@vercel/postgres": "^0.5.0",
    "csv-parse": "^5.5.0"
  }
}
```

## 🎯 Development Workflow

### 1. Create Next.js App
```bash
npx create-next-app@latest london-dog-friendly --typescript --tailwind --app --src-dir=false
cd london-dog-friendly
```

### 2. Install Additional Dependencies
```bash
npm install react-leaflet leaflet @vercel/postgres csv-parse @headlessui/react @heroicons/react
npm install -D @types/leaflet
```

### 3. Set Up Database
```bash
# In Vercel dashboard or using Vercel CLI
vercel env add DATABASE_URL
```

### 4. Import Your CSV Data
```bash
# Run data import script
npm run import-data
```

### 5. Deploy to Vercel
```bash
vercel --prod
```

## 🌟 Key Features Implementation

### Search Functionality
- **Text Search**: Full-text search across venue names and descriptions
- **Category Filter**: Filter by restaurants, hotels, attractions, services
- **Location Filter**: Search by postcode or area
- **Advanced Filters**: Rating, opening hours, amenities

### Map Integration
- **Leaflet Maps**: Free, customizable mapping solution
- **Custom Markers**: Different icons for different venue categories
- **Marker Clustering**: Group nearby venues for better performance
- **Info Popups**: Quick venue details on marker click

### Performance Optimization
- **Static Generation**: Pre-render venue pages for SEO
- **Image Optimization**: Next.js automatic image optimization
- **Code Splitting**: Load components as needed
- **Caching**: API response caching for better performance

## 📱 Mobile Features
- **Responsive Design**: Mobile-first approach
- **Touch-Friendly**: Large touch targets for mobile users
- **Progressive Web App**: Installable on mobile devices
- **Offline Support**: Cache venue data for offline browsing

---

**Ready to build?** The architecture is designed for scalability, performance, and excellent user experience!