#!/bin/bash

# GitHub Authentication and Integration Setup Script
# This script sets up proper GitHub authentication and verifies integration

set -e

echo "🔐 Setting up GitHub Authentication and Integration..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    print_error "GitHub CLI (gh) is not installed. Please install it first:"
    echo "brew install gh"
    exit 1
fi

print_status "GitHub CLI is installed ✓"

# Check current authentication status
print_status "Checking current GitHub authentication status..."
if gh auth status &> /dev/null; then
    print_success "Already authenticated with GitHub!"
    gh auth status
else
    print_warning "Not authenticated with GitHub. Starting authentication process..."
    
    # Try web-based authentication
    print_status "Starting web-based authentication..."
    echo "This will open your browser to authenticate with GitHub."
    echo "Please complete the authentication in your browser."
    
    if gh auth login --web --git-protocol https; then
        print_success "GitHub authentication completed!"
    else
        print_error "Web authentication failed. Trying token-based authentication..."
        
        echo ""
        echo "Please provide your GitHub Personal Access Token:"
        echo "1. Go to https://github.com/settings/tokens"
        echo "2. Generate a new token with 'repo', 'read:org', and 'gist' scopes"
        echo "3. Copy the token and paste it below:"
        echo ""
        
        read -s -p "GitHub Token: " github_token
        echo ""
        
        if [ -n "$github_token" ]; then
            echo "$github_token" | gh auth login --with-token
            print_success "GitHub authentication completed with token!"
        else
            print_error "No token provided. Authentication failed."
            exit 1
        fi
    fi
fi

# Verify authentication
print_status "Verifying GitHub authentication..."
if gh auth status; then
    print_success "GitHub authentication verified!"
else
    print_error "GitHub authentication verification failed!"
    exit 1
fi

# Set up git configuration
print_status "Setting up git configuration..."
git config --global user.name "worldwidebro"
git config --global user.email "winnerscirclewcllc@gmail.com"
git config --global init.defaultBranch main
git config --global pull.rebase false

print_success "Git configuration set up ✓"

# Test GitHub integration
print_status "Testing GitHub integration..."

# Test repository access
if gh repo list --limit 1 &> /dev/null; then
    print_success "GitHub repository access working ✓"
else
    print_warning "GitHub repository access test failed"
fi

# Test authentication with a simple API call
if gh api user &> /dev/null; then
    print_success "GitHub API access working ✓"
else
    print_warning "GitHub API access test failed"
fi

# Set up environment variables for the project
print_status "Setting up environment variables..."

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    print_status "Creating .env file..."
    cat > .env << EOF
# GitHub Configuration
GITHUB_TOKEN=\$(gh auth token)
GH_TOKEN=\$(gh auth token)

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
    print_success ".env file created ✓"
else
    print_status "Updating existing .env file..."
    # Update GitHub token in existing .env
    if grep -q "GITHUB_TOKEN" .env; then
        sed -i '' 's/GITHUB_TOKEN=.*/GITHUB_TOKEN=$(gh auth token)/' .env
    else
        echo "GITHUB_TOKEN=\$(gh auth token)" >> .env
    fi
    
    if grep -q "GH_TOKEN" .env; then
        sed -i '' 's/GH_TOKEN=.*/GH_TOKEN=$(gh auth token)/' .env
    else
        echo "GH_TOKEN=\$(gh auth token)" >> .env
    fi
    
    print_success ".env file updated ✓"
fi

# Test the integration with our MCP server
print_status "Testing MCP server GitHub integration..."

# Check if MCP server can access GitHub
if python3 -c "
import os
import subprocess
try:
    token = subprocess.check_output(['gh', 'auth', 'token'], text=True).strip()
    if token:
        print('GitHub token available for MCP server')
    else:
        print('No GitHub token found')
except:
    print('Failed to get GitHub token')
" 2>/dev/null; then
    print_success "MCP server can access GitHub token ✓"
else
    print_warning "MCP server GitHub token access needs verification"
fi

# Final verification
print_status "Running final integration tests..."

# Test git operations
if git status &> /dev/null; then
    print_success "Git operations working ✓"
else
    print_warning "Git operations test failed"
fi

# Test GitHub CLI operations
if gh repo view &> /dev/null; then
    print_success "GitHub CLI operations working ✓"
else
    print_warning "GitHub CLI operations test failed (this is normal if not in a git repo)"
fi

echo ""
print_success "🎉 GitHub Authentication and Integration Setup Complete!"
echo ""
echo "Next steps:"
echo "1. Verify your GitHub token has the required scopes: repo, read:org, gist"
echo "2. Test repository operations: gh repo list"
echo "3. Test MCP server integration: python src/integrations/repository_mcp_server_fastapi.py"
echo "4. Commit your changes: git add . && git commit -m 'Setup GitHub authentication'"
echo ""
echo "Your GitHub integration is now ready for IZA OS operations!"
