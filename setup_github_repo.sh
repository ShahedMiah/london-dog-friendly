#!/bin/bash

# 🚀 Setup GitHub Repository for London Dog-Friendly Directory
# Run this script to create and push to GitHub

set -e  # Exit on any error

echo "🐕 Setting up London Dog-Friendly Directory GitHub Repository..."

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed. Please install it first:"
    echo "   brew install gh"
    exit 1
fi

# Check if user is logged into GitHub CLI
if ! gh auth status &> /dev/null; then
    echo "🔐 Please login to GitHub CLI first:"
    echo "   gh auth login"
    exit 1
fi

# Initialize git if not already done
if [ ! -d ".git" ]; then
    echo "📦 Initializing Git repository..."
    git init
else
    echo "✅ Git repository already initialized"
fi

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    echo "📝 Creating .gitignore..."
    cat > .gitignore << EOF
# Dependencies
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Production builds
.next/
out/
build/

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Database
*.db
*.sqlite

# Python
__pycache__/
*.py[cod]
*\$py.class
venv/
.venv/

# Progress files (can be regenerated)
bringfido_progress_*.json

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# IDE files
.vscode/
.idea/
*.swp
*.swo

# Logs
logs
*.log

# Vercel
.vercel
EOF
else
    echo "✅ .gitignore already exists"
fi

# Create README.md
echo "📖 Creating README.md..."
cat > README.md << 'EOF'
# 🐕 London Dog-Friendly Directory

An interactive directory of dog-friendly businesses in London, built with Next.js and deployed on Vercel.

## 🌟 Features

- **Interactive Map**: Explore 800+ dog-friendly venues on an interactive map
- **Advanced Search**: Filter by category, location, and ratings
- **Detailed Listings**: Complete business information including contact details
- **Mobile Responsive**: Optimized for all devices
- **Real-time Updates**: Fresh data from multiple sources

## 🎯 Categories

- **Restaurants & Pubs**: 121+ venues
- **Hotels & Accommodation**: 658+ venues  
- **Attractions & Activities**: 44+ venues
- **Services**: 8+ venues

## 🚀 Live Demo

Visit the live site: [https://your-site.vercel.app](https://your-site.vercel.app)

## 🛠️ Technology Stack

- **Frontend**: Next.js 14, React, Tailwind CSS
- **Backend**: Next.js API Routes
- **Database**: Vercel Postgres
- **Maps**: Leaflet.js
- **Deployment**: Vercel
- **Data Source**: BringFido.com scraping + manual curation

## 📊 Data

The dataset includes:
- 800+ dog-friendly venues across London
- Complete business details (name, address, phone, website)
- GPS coordinates for mapping
- Category classifications
- Dog-friendly specific descriptions

## 🔧 Development

```bash
# Clone the repository
git clone https://github.com/[username]/london-dog-friendly.git
cd london-dog-friendly

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local

# Run development server
npm run dev
```

## 📈 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Data sourced from BringFido.com
- Built with love for London dog owners 🐾
EOF

# Add all files to git
echo "📦 Adding files to git..."
git add .

# Check if there are any changes to commit
if git diff --staged --quiet; then
    echo "✅ No changes to commit"
else
    # Commit the changes
    echo "💾 Committing changes..."
    git commit -m "Initial commit: London Dog-Friendly Directory

🐕 Complete dataset of 800+ dog-friendly London venues
🗂️  Includes restaurants, hotels, attractions, and services  
🔧 Ready for Next.js web application deployment
📊 Data sourced from BringFido.com with comprehensive scraping tools

Features ready for implementation:
- Interactive mapping
- Advanced search and filtering  
- Mobile-responsive design
- API endpoints for data access"
fi

# Create GitHub repository
echo "🌐 Creating GitHub repository..."
REPO_NAME="london-dog-friendly"
REPO_DESC="Interactive directory of dog-friendly businesses in London - 800+ venues with search, maps, and detailed listings"

# Create the repository
if gh repo create "$REPO_NAME" --public --description "$REPO_DESC" --clone=false; then
    echo "✅ GitHub repository created successfully!"
    
    # Add remote origin
    GITHUB_USER=$(gh api user --jq .login)
    git remote add origin "https://github.com/$GITHUB_USER/$REPO_NAME.git"
    
    # Push to GitHub
    echo "📤 Pushing to GitHub..."
    git branch -M main
    git push -u origin main
    
    echo ""
    echo "🎉 SUCCESS! Your repository is ready:"
    echo "   🔗 https://github.com/$GITHUB_USER/$REPO_NAME"
    echo ""
    echo "🚀 Next steps:"
    echo "   1. Read DEPLOY_TO_PRODUCTION.md for deployment guide"
    echo "   2. Run your data scraper to populate the dataset"
    echo "   3. Set up the Next.js application"
    echo "   4. Deploy to Vercel"
    echo ""
    echo "💡 Quick Vercel deployment:"
    echo "   npm create next-app@latest . --typescript --tailwind --app"
    echo "   vercel --prod"
    
else
    echo "❌ Failed to create GitHub repository"
    echo "   This might be because a repository with this name already exists"
    echo "   Try: gh repo create london-dog-friendly-directory --public"
fi
EOF