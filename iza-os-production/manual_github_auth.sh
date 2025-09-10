#!/bin/bash

# Manual GitHub Authentication Setup
# This script helps you set up GitHub authentication using a personal access token

echo "🔐 GitHub Authentication Setup"
echo "=============================="
echo ""
echo "Since web-based authentication isn't working, let's use a Personal Access Token."
echo ""
echo "STEP 1: Create a GitHub Personal Access Token"
echo "1. Go to: https://github.com/settings/tokens"
echo "2. Click 'Generate new token' → 'Generate new token (classic)'"
echo "3. Give it a name like 'IZA OS Development'"
echo "4. Set expiration (recommend 90 days or no expiration)"
echo "5. Select these scopes:"
echo "   ✓ repo (Full control of private repositories)"
echo "   ✓ read:org (Read org and team membership)"
echo "   ✓ gist (Create gists)"
echo "6. Click 'Generate token'"
echo "7. COPY the token (you won't see it again!)"
echo ""
echo "STEP 2: Enter your token below"
echo ""

read -s -p "Paste your GitHub Personal Access Token: " github_token
echo ""

if [ -z "$github_token" ]; then
    echo "❌ No token provided. Exiting."
    exit 1
fi

echo ""
echo "🔧 Setting up authentication..."

# Test the token first
echo "Testing token..."
if echo "$github_token" | gh auth login --with-token; then
    echo "✅ GitHub authentication successful!"
    
    # Verify authentication
    echo "Verifying authentication..."
    if gh auth status; then
        echo "✅ Authentication verified!"
        
        # Set up git configuration
        echo "Setting up git configuration..."
        git config --global user.name "worldwidebro"
        git config --global user.email "winnerscirclewcllc@gmail.com"
        git config --global init.defaultBranch main
        git config --global pull.rebase false
        
        echo "✅ Git configuration set up!"
        
        # Test GitHub operations
        echo "Testing GitHub operations..."
        if gh api user &> /dev/null; then
            echo "✅ GitHub API access working!"
        else
            echo "⚠️  GitHub API access test failed"
        fi
        
        # Create/update .env file
        echo "Setting up environment variables..."
        if [ ! -f .env ]; then
            cat > .env << EOF
# GitHub Configuration
GITHUB_TOKEN=$github_token
GH_TOKEN=$github_token

# Git Configuration
GIT_USER_NAME="worldwidebro"
GIT_USER_EMAIL="winnerscirclewcllc@gmail.com"

# Project Configuration
PROJECT_NAME="IZA OS Production"
PROJECT_VERSION="1.0.0"

# API Keys (add your actual keys here)
# OPENAI_API_KEY=your_openai_key_here
# ANTHROPIC_API_KEY=your_anthropic_key_here
# STRIPE_SECRET_KEY=your_stripe_key_here
EOF
            echo "✅ .env file created!"
        else
            # Update existing .env
            if grep -q "GITHUB_TOKEN" .env; then
                sed -i '' "s/GITHUB_TOKEN=.*/GITHUB_TOKEN=$github_token/" .env
            else
                echo "GITHUB_TOKEN=$github_token" >> .env
            fi
            
            if grep -q "GH_TOKEN" .env; then
                sed -i '' "s/GH_TOKEN=.*/GH_TOKEN=$github_token/" .env
            else
                echo "GH_TOKEN=$github_token" >> .env
            fi
            
            echo "✅ .env file updated!"
        fi
        
        echo ""
        echo "🎉 GitHub Authentication Setup Complete!"
        echo ""
        echo "Next steps:"
        echo "1. Test repository access: gh repo list"
        echo "2. Test MCP server: python src/integrations/repository_mcp_server_fastapi.py"
        echo "3. Commit changes: git add . && git commit -m 'Setup GitHub authentication'"
        echo ""
        
    else
        echo "❌ Authentication verification failed!"
        exit 1
    fi
else
    echo "❌ GitHub authentication failed!"
    echo "Please check your token and try again."
    exit 1
fi
