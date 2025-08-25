import { NextRequest } from 'next/server'
import { chromium } from 'playwright'

export async function GET(request: NextRequest) {
  try {
    // Test browser launch
    const browser = await chromium.launch({
      headless: true,
      args: [
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--disable-web-security',
        '--disable-features=VizDisplayCompositor'
      ]
    })
    
    const page = await browser.newPage()
    
    // Test navigation to a simple page
    await page.goto('https://example.com', { timeout: 10000 })
    const title = await page.title()
    
    await browser.close()
    
    return Response.json({
      success: true,
      message: 'Browser test successful',
      title: title,
      timestamp: new Date().toISOString()
    })
    
  } catch (error) {
    return Response.json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
      timestamp: new Date().toISOString()
    }, { status: 500 })
  }
}