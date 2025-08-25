import { NextRequest } from 'next/server'
import { chromium } from 'playwright'
import * as fs from 'fs'
import * as path from 'path'
import { createObjectCsvWriter } from 'csv-writer'

interface VenueData {
  name: string
  address: string
  phone: string
  email: string
  website: string
  description: string
  latitude: string
  longitude: string
  category: string
  venue_id: string
  url: string
}

class BringFidoScraper {
  private baseUrl = "https://www.bringfido.ca"
  private allVenues: VenueData[] = []
  private failedUrls: string[] = []
  
  private categories = {
    'restaurants': {
      url: '/restaurant/city/london_gb/',
      category_id: '139',
      expected_count: 121
    },
    'hotels': {
      url: '/lodging/city/london_gb/',
      category_id: '193', 
      expected_count: 658
    },
    'attractions': {
      url: '/attraction/city/london_gb/',
      category_id: '229',
      expected_count: 44
    },
    'services': {
      url: '/resource/city/london_gb/',
      category_id: '77',
      expected_count: 8
    }
  }

  constructor(private progressCallback: (data: any) => void) {}

  private waitRandom(min: number = 2000, max: number = 5000): Promise<void> {
    const delay = Math.random() * (max - min) + min
    return new Promise(resolve => setTimeout(resolve, delay))
  }

  private async extractVenueLinksFromListing(page: any, categoryName: string) {
    const venueLinks: any[] = []
    let currentPage = 1
    
    this.progressCallback({
      progress: `Extracting ${categoryName} venue links...`,
      stage: `Scanning ${categoryName} listings`
    })
    
    while (true) {
      try {
        await page.waitForLoadState('networkidle', { timeout: 30000 })
        await this.waitRandom(2000, 4000)
        
        let headingLinks: any[] = []
        
        if (categoryName === 'restaurants') {
          headingLinks = await page.$$('h2 a[href*="/restaurant/"]')
        } else if (categoryName === 'hotels') {
          headingLinks = await page.$$('h2 a[href*="/lodging/"]')
        } else if (categoryName === 'attractions') {
          headingLinks = await page.$$('h2 a[href*="/attraction/"]')
        } else if (categoryName === 'services') {
          headingLinks = await page.$$('h2 a[href*="/resource/"]')
        }
        
        const linksFound: any[] = []
        
        for (const element of headingLinks) {
          try {
            const href = await element.getAttribute('href')
            const title = await element.innerText()
            
            if (href && title) {
              const fullUrl = href.startsWith('http') ? href : `${this.baseUrl}${href}`
              
              if (!linksFound.some(link => link.url === fullUrl)) {
                linksFound.push({
                  url: fullUrl,
                  title: title.trim(),
                  category: categoryName
                })
              }
            }
          } catch (e) {
            continue
          }
        }
        
        venueLinks.push(...linksFound)
        
        this.progressCallback({
          progress: `Page ${currentPage}: Found ${linksFound.length} ${categoryName} links`,
          stage: `Scanning ${categoryName} listings`
        })
        
        // Look for next page
        try {
          const nextLink = await page.$('a:has-text("See More Results")')
          
          if (nextLink && linksFound.length > 0) {
            const nextUrl = await nextLink.getAttribute('href')
            if (nextUrl) {
              const fullNextUrl = nextUrl.startsWith('http') ? nextUrl : `${this.baseUrl}${nextUrl}`
              await page.goto(fullNextUrl)
              currentPage++
              continue
            }
          }
        } catch (e) {
          // No more pages
        }
        
        break
        
      } catch (error) {
        this.progressCallback({
          progress: `Error extracting ${categoryName} links from page ${currentPage}`,
          stage: `Error in ${categoryName}`
        })
        break
      }
    }
    
    return venueLinks
  }

  private async extractVenueDetails(page: any, venueUrl: string, category: string) {
    try {
      await page.goto(venueUrl, { timeout: 30000 })
      await page.waitForLoadState('networkidle', { timeout: 20000 })
      await this.waitRandom(1000, 3000)
      
      const venueData = await page.evaluate(() => {
        const data = {
          name: '',
          address: '',
          phone: '',
          email: '',
          website: '',
          description: '',
          latitude: '',
          longitude: ''
        }
        
        // Get name from h1
        const nameEl = document.querySelector('h1')
        if (nameEl) data.name = nameEl.textContent?.trim() || ''
        
        // Get address
        const addressElements = document.querySelectorAll('button, div, span, p')
        for (let i = 0; i < addressElements.length; i++) {
          const el = addressElements[i]
          const text = el.textContent || ''
          if (text.includes('London') && (text.includes('UK') || text.includes('United Kingdom'))) {
            data.address = text.trim()
            break
          }
        }
        
        // Get phone
        const phoneEl = document.querySelector('a[href^="tel:"]')
        if (phoneEl) {
          data.phone = phoneEl.textContent?.trim() || ''
        }
        
        // Get email
        const emailEl = document.querySelector('a[href^="mailto:"]')
        if (emailEl) {
          data.email = (emailEl as HTMLAnchorElement).href.replace('mailto:', '')
        }
        
        // Get website
        const websiteLinks = document.querySelectorAll('a[href^="http"]')
        for (let j = 0; j < websiteLinks.length; j++) {
          const link = websiteLinks[j] as HTMLAnchorElement
          const href = link.href
          if (!href.includes('bringfido') && 
              !href.includes('facebook') && 
              !href.includes('twitter') && 
              !href.includes('instagram') &&
              !href.includes('booking.com') &&
              !href.includes('airbnb')) {
            data.website = href
            break
          }
        }
        
        // Get description
        const paragraphs = document.querySelectorAll('p')
        for (let k = 0; k < paragraphs.length; k++) {
          const p = paragraphs[k]
          const text = p.textContent?.trim() || ''
          if (text.length > 50 && 
              (text.toLowerCase().includes('dog') || 
               text.toLowerCase().includes('pet') ||
               text.toLowerCase().includes('restaurant') ||
               text.toLowerCase().includes('bar') ||
               text.toLowerCase().includes('food') ||
               text.toLowerCase().includes('hotel') ||
               text.toLowerCase().includes('attraction'))) {
            data.description = text
            break
          }
        }
        
        // Extract coordinates
        const scripts = document.querySelectorAll('script')
        for (let l = 0; l < scripts.length; l++) {
          const script = scripts[l]
          const content = script.textContent || ''
          
          const latMatch = content.match(/["']?latitude["']?\s*[:\=]\s*([0-9.-]+)/i)
          const lngMatch = content.match(/["']?longitude["']?\s*[:\=]\s*([0-9.-]+)/i)
          
          if (latMatch && lngMatch) {
            data.latitude = latMatch[1]
            data.longitude = lngMatch[1]
            break
          }
        }
        
        return data
      })
      
      const venueId = venueUrl.split('/').pop() || ''
      
      return {
        ...venueData,
        venue_id: venueId,
        url: venueUrl,
        category: category
      }
      
    } catch (error) {
      this.failedUrls.push(venueUrl)
      return null
    }
  }

  async scrapeAllCategories(): Promise<VenueData[]> {
    const browser = await chromium.launch({
      headless: true,
      args: ['--no-sandbox', '--disable-dev-shm-usage']
    })
    
    const page = await browser.newPage()
    page.setDefaultTimeout(45000)
    
    try {
      let totalExpected = 0
      Object.values(this.categories).forEach(cat => {
        totalExpected += cat.expected_count
      })
      
      this.progressCallback({
        totalVenues: totalExpected,
        processedVenues: 0,
        stage: 'Initializing',
        progress: 'Starting scraper...'
      })
      
      for (const [categoryName, categoryInfo] of Object.entries(this.categories)) {
        this.progressCallback({
          stage: `Processing ${categoryName}`,
          progress: `Starting ${categoryName} scraping...`
        })
        
        const categoryUrl = `${this.baseUrl}${categoryInfo.url}`
        await page.goto(categoryUrl, { timeout: 30000 })
        
        // Extract venue links
        const venueLinks = await this.extractVenueLinksFromListing(page, categoryName)
        
        if (venueLinks.length === 0) {
          this.progressCallback({
            progress: `No ${categoryName} venues found`,
            stage: `Completed ${categoryName}`
          })
          continue
        }
        
        this.progressCallback({
          progress: `Found ${venueLinks.length} ${categoryName} to process`,
          stage: `Processing ${categoryName} details`
        })
        
        // Extract details from each venue
        for (let i = 0; i < venueLinks.length; i++) {
          const venue = venueLinks[i]
          
          this.progressCallback({
            progress: `Processing ${venue.title}`,
            stage: `${categoryName} ${i + 1}/${venueLinks.length}`,
            processedVenues: this.allVenues.length + 1
          })
          
          const venueData = await this.extractVenueDetails(page, venue.url, categoryName)
          if (venueData) {
            if (!venueData.name) {
              venueData.name = venue.title
            }
            this.allVenues.push(venueData)
          }
          
          await this.waitRandom(3000, 6000)
        }
        
        this.progressCallback({
          progress: `Completed ${categoryName}: ${venueLinks.length} venues processed`,
          stage: `Finished ${categoryName}`
        })
        
        // Break between categories
        await this.waitRandom(10000, 20000)
      }
      
      return this.allVenues
      
    } finally {
      await browser.close()
    }
  }
}

export async function POST(request: NextRequest) {
  const encoder = new TextEncoder()
  
  const stream = new ReadableStream({
    start(controller) {
      const progressCallback = (data: any) => {
        const jsonData = JSON.stringify(data) + '\n'
        controller.enqueue(encoder.encode(jsonData))
      }
      
      const scraper = new BringFidoScraper(progressCallback)
      
      scraper.scrapeAllCategories()
        .then(async (venues) => {
          // Create CSV file
          const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
          const filename = `london-dog-friendly-venues-${timestamp}.csv`
          const filepath = path.join(process.cwd(), 'public', filename)
          
          // Ensure public directory exists
          const publicDir = path.join(process.cwd(), 'public')
          if (!fs.existsSync(publicDir)) {
            fs.mkdirSync(publicDir, { recursive: true })
          }
          
          const csvWriter = createObjectCsvWriter({
            path: filepath,
            header: [
              { id: 'name', title: 'Name' },
              { id: 'description', title: 'Description' },
              { id: 'category', title: 'Category' },
              { id: 'address', title: 'Address' },
              { id: 'phone', title: 'Phone' },
              { id: 'email', title: 'Email' },
              { id: 'website', title: 'Website' },
              { id: 'latitude', title: 'Latitude' },
              { id: 'longitude', title: 'Longitude' },
              { id: 'venue_id', title: 'Venue ID' },
              { id: 'url', title: 'Source URL' }
            ]
          })
          
          await csvWriter.writeRecords(venues)
          
          progressCallback({
            isRunning: false,
            progress: `Export completed! ${venues.length} venues exported.`,
            stage: 'Completed',
            processedVenues: venues.length,
            totalVenues: venues.length,
            downloadUrl: `/${filename}`
          })
          
          controller.close()
        })
        .catch((error) => {
          progressCallback({
            isRunning: false,
            error: error.message,
            stage: 'Error'
          })
          controller.close()
        })
    }
  })
  
  return new Response(stream, {
    headers: {
      'Content-Type': 'text/plain',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
    }
  })
}