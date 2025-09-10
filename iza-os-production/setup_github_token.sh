#!/bin/bash

# Simple GitHub Token Setup Script
echo "🔐 GitHub Token Setup"
echo "===================="
echo ""
echo "Please enter your GitHub Personal Access Token:"
echo "(The token will be hidden as you type)"
echo ""

read -s -p "GitHub Token: " github_token
echo ""

if [ -z "$github_token" ]; then
    echo "❌ No token provided. Exiting."
    exit 1
fi

echo ""
echo "🔧 Setting up GitHub authentication..."

# Test the token first
echo "Testing token..."
if echo "$github_token" | gh auth login --with-token; then
    echo "✅ GitHub authentication successful!"
    
    # Update .env file with the actual token
    echo "Updating .env file..."
    sed -i '' "s/GITHUB_TOKEN=\$(gh auth token 2>\/dev\/null || echo \"\")/GITHUB_TOKEN=$github_token/" .env
    sed -i '' "s/GH_TOKEN=\$(gh auth token 2>\/dev\/null || echo \"\")/GH_TOKEN=$github_token/" .env
    
    echo "✅ .env file updated with GitHub token"
    
    # Verify authentication
    echo "Verifying authentication..."
    if gh auth status; then
        echo "✅ GitHub authentication verified!"
        
        # Test GitHub operations
        echo "Testing GitHub operations..."
        if gh api user &> /dev/null; then
            echo "✅ GitHub API access working!"
        else
            echo "⚠️  GitHub API access test failed"
        fi
        
        # Test repository access
        if gh repo list --limit 1 &> /dev/null; then
            echo "✅ GitHub repository access working!"
        else
            echo "⚠️  GitHub repository access test failed"
        fi
        
        echo ""
        echo "🎉 GitHub Token Setup Complete!"
        echo ""
        echo "Next steps:"
        echo "1. Test MCP server: curl http://localhost:8000/health"
        echo "2. Test agent orchestrator: curl http://localhost:8001/health"
        echo "3. Run unified orchestrator: python UNIFIED_ORCHESTRATOR.py"
        echo ""
        
    else
        echo "❌ GitHub authentication verification failed!"
        exit 1
    fi
else
    echo "❌ GitHub authentication failed!"
    echo "Please check your token and try again."
    exit 1
fi
