$trickyEmails = @(
    @{
        name = "1. Spam disguised as support"
        subject = "URGENT: Your account needs verification"
        body = "Click here to verify your account and claim your free prize! Limited time offer expires soon. Unsubscribe from our newsletter."
    },
    @{
        name = "2. Mixed language - Hindi/English billing"
        subject = "Payment ka issue hai"
        body = "Mera payment nahi ho raha hai. Credit card se deduct ho gaya lekin invoice nahi mila. Please help karo urgent."
    },
    @{
        name = "3. Angry complaint disguised as question"
        subject = "How long do I have to wait?"
        body = "This is absolutely ridiculous! I've been waiting for 2 weeks with no response. Your support is terrible. I demand a refund immediately and want to speak to a manager."
    },
    @{
        name = "4. Technical + Access request combined"
        subject = "Cannot login to admin panel"
        body = "I'm getting 403 Forbidden error when trying to access the admin dashboard. Can you check if my account has proper permissions? Also the page loads very slowly."
    },
    @{
        name = "5. Feature request disguised as bug"
        subject = "Export button not working"
        body = "There's no CSV export button on the reports page. This is blocking our workflow. When will this be available?"
    },
    @{
        name = "6. Pure Hindi - technical issue"
        subject = "ऐप क्रैश हो रहा है"
        body = "जब मैं डैशबोर्ड खोलता हूं तो ऐप क्रैश हो जाता है। Error 500 दिख रहा है। कृपया मदद करें।"
    },
    @{
        name = "7. Hinglish - access request"
        subject = "Team member add karna hai"
        body = "Naye employee John ke liye account chahiye. Email hai john@company.com. Admin access dena please."
    },
    @{
        name = "8. Vague inquiry - should trigger LLM"
        subject = "Question about system"
        body = "Hi, I have some concerns about how things are working. Can you help me understand the process better?"
    },
    @{
        name = "9. Hardware + billing combined"
        subject = "Server down and charged double"
        body = "Production server has been down for 3 hours and we're losing money. Plus we got charged twice this month. Need immediate assistance on both issues."
    },
    @{
        name = "10. Legitimate promotional (not spam)"
        subject = "New feature announcement"
        body = "Hello team, we wanted to inform you about our new dashboard features available in your account. Check out the improvements we've made based on your feedback."
    },
    # Add your custom test cases below:
    @{
        name = "11. Your custom test"
        subject = "Test subject here"
        body = "Test body here"
    }
)

Write-Host "`n" -NoNewline
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  TESTING 10 TRICKY EMAIL SCENARIOS" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "`n"

$stats = @{
    spam_filtered = 0
    lightweight_used = 0
    llm_used = 0
    total = $trickyEmails.Count
}

foreach ($email in $trickyEmails) {
    Write-Host "`n"
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
    Write-Host $email.name -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
    Write-Host "Subject: $($email.subject)" -ForegroundColor White
    Write-Host "Body: $($email.body.Substring(0, [Math]::Min(80, $email.body.Length)))..." -ForegroundColor Gray
    Write-Host ""
    
    $body = @{
        subject = $email.subject
        body = $email.body
        sender = "test@example.com"
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/api/emails/process" -Method POST -Body $body -ContentType "application/json"
        
        $method = $response.classification.method_used
        if ($response.classification.is_spam) {
            $stats.spam_filtered++
            Write-Host "🚫 SPAM DETECTED" -ForegroundColor Red
        } elseif ($method -eq "lightweight_classifier") {
            $stats.lightweight_used++
            Write-Host "⚡ Lightweight Classifier (High Confidence)" -ForegroundColor Green
        } elseif ($method -eq "lightweight_classifier_review") {
            Write-Host "⚠️  Lightweight Classifier (Low Confidence - Review Needed)" -ForegroundColor Yellow
        } elseif ($method -like "*llm*") {
            $stats.llm_used++
            Write-Host "🤖 LLM Fallback" -ForegroundColor Magenta
        }
        
        Write-Host "  Category: $($response.classification.category)" -ForegroundColor White
        Write-Host "  Confidence: $([Math]::Round($response.classification.confidence * 100, 1))%" -ForegroundColor White
        Write-Host "  Language: $($response.classification.language_detected -join ', ')" -ForegroundColor Gray
        Write-Host "  Time: $($response.processing_time_ms)ms" -ForegroundColor Gray
        
        if ($response.classification.reasoning) {
            Write-Host "  Reasoning: $($response.classification.reasoning)" -ForegroundColor Gray
        }
        
    } catch {
        Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`n"
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  STATISTICS" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Total Emails: $($stats.total)" -ForegroundColor White
Write-Host "Spam Filtered: $($stats.spam_filtered) ($([Math]::Round($stats.spam_filtered/$stats.total*100, 1))%)" -ForegroundColor Red
Write-Host "Lightweight Classifier: $($stats.lightweight_used) ($([Math]::Round($stats.lightweight_used/$stats.total*100, 1))%)" -ForegroundColor Green
Write-Host "LLM Fallback: $($stats.llm_used) ($([Math]::Round($stats.llm_used/$stats.total*100, 1))%)" -ForegroundColor Magenta
Write-Host ""
Write-Host "✅ LLM Usage: $([Math]::Round($stats.llm_used/$stats.total*100, 1))% (Target: <20%)" -ForegroundColor $(if ($stats.llm_used/$stats.total -lt 0.2) { "Green" } else { "Yellow" })
Write-Host "`n"
