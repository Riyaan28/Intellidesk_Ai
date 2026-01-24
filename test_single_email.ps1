# Quick single email tester for IntelliDesk
# Usage: Edit the $email variable and run: .\test_single_email.ps1

$email = @{
    subject = "Database connection timeout"
    body = "Our production database is throwing timeout errors. Error code 1045. Please help urgently."
    sender = "admin@company.com"
}

Write-Host "`nTesting Email..." -ForegroundColor Cyan
Write-Host "Subject: $($email.subject)"
Write-Host "Body: $($email.body.Substring(0, [Math]::Min(60, $email.body.Length)))...`n"

try {
    $result = Invoke-RestMethod -Uri "http://localhost:8000/api/emails/process" -Method POST -Body ($email | ConvertTo-Json) -ContentType "application/json"
    
    Write-Host "=== CLASSIFICATION RESULT ===" -ForegroundColor Green
    Write-Host "Category: $($result.classification.category)"
    Write-Host "Confidence: $([math]::Round($result.classification.confidence * 100, 1))%"
    Write-Host "Method: $($result.classification.method_used)"
    Write-Host "Language: $($result.classification.language_detected -join ', ')"
    Write-Host "Requires Review: $($result.classification.requires_review)"
    Write-Host "Time: $($result.classification.processing_time_ms)ms"
    Write-Host "`nReasoning: $($result.classification.reasoning)"
    Write-Host "`n=== TICKET CREATED ===" -ForegroundColor Green
    Write-Host "Ticket ID: $($result.ticket.id)"
    Write-Host "Status: $($result.ticket.status)"
    Write-Host "Priority: $($result.ticket.priority)"
    
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}
