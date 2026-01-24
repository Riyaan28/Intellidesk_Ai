# Test Thread Detection & Deduplication Feature
Write-Host "`n=========================================" -ForegroundColor Cyan
Write-Host "  TESTING THREAD DETECTION & DEDUPLICATION" -ForegroundColor Cyan
Write-Host "=========================================`n" -ForegroundColor Cyan

$baseUrl = "http://localhost:8000/api/emails/process"

# Test Case 1: Original email
Write-Host "Test 1: Original Email" -ForegroundColor Yellow
$email1 = @{
    subject = "Cannot access dashboard"
    body = "I'm unable to login to the admin dashboard. Getting 403 error."
    sender = "john@company.com"
} | ConvertTo-Json

$response1 = Invoke-RestMethod -Uri $baseUrl -Method POST -Body $email1 -ContentType "application/json"
$ticketId = $response1.ticket_id
Write-Host "  Created Ticket: $ticketId" -ForegroundColor Green
Write-Host "  Category: $($response1.classification.category)" -ForegroundColor White
Write-Host ""

Start-Sleep -Seconds 2

# Test Case 2: Reply with Re: prefix
Write-Host "Test 2: Reply with 'Re:' prefix (should dedupe)" -ForegroundColor Yellow
$email2 = @{
    subject = "Re: Cannot access dashboard"
    body = "Still having the same issue. Can you help?"
    sender = "john@company.com"
} | ConvertTo-Json

$response2 = Invoke-RestMethod -Uri $baseUrl -Method POST -Body $email2 -ContentType "application/json"
Write-Host "  Ticket ID: $($response2.ticket_id)" -ForegroundColor $(if ($response2.ticket_id -eq $ticketId) { "Green" } else { "Red" })
Write-Host "  Is Duplicate: $($response2.deduplication.is_duplicate)" -ForegroundColor $(if ($response2.deduplication.is_duplicate) { "Green" } else { "Red" })
Write-Host "  Master Ticket: $($response2.deduplication.master_ticket_id)" -ForegroundColor White
Write-Host ""

Start-Sleep -Seconds 2

# Test Case 3: Reference with ticket ID
Write-Host "Test 3: Reference with Ticket ID (should dedupe)" -ForegroundColor Yellow
$email3 = @{
    subject = "Following up on ticket #$ticketId"
    body = "Any update on my access issue?"
    sender = "john@company.com"
} | ConvertTo-Json

$response3 = Invoke-RestMethod -Uri $baseUrl -Method POST -Body $email3 -ContentType "application/json"
Write-Host "  Ticket ID: $($response3.ticket_id)" -ForegroundColor $(if ($response3.ticket_id -eq $ticketId) { "Green" } else { "Red" })
Write-Host "  Is Duplicate: $($response3.deduplication.is_duplicate)" -ForegroundColor $(if ($response3.deduplication.is_duplicate) { "Green" } else { "Red" })
Write-Host ""

Start-Sleep -Seconds 2

# Test Case 4: Same sender, similar topic within 48hrs
Write-Host "Test 4: Same sender, similar topic (should dedupe)" -ForegroundColor Yellow
$email4 = @{
    subject = "Dashboard access problem"
    body = "I still can't login to the dashboard. 403 forbidden error."
    sender = "john@company.com"
} | ConvertTo-Json

$response4 = Invoke-RestMethod -Uri $baseUrl -Method POST -Body $email4 -ContentType "application/json"
Write-Host "  Ticket ID: $($response4.ticket_id)" -ForegroundColor $(if ($response4.ticket_id -eq $ticketId) { "Green" } else { "Red" })
Write-Host "  Is Duplicate: $($response4.deduplication.is_duplicate)" -ForegroundColor $(if ($response4.deduplication.is_duplicate) { "Green" } else { "Red" })
Write-Host ""

Start-Sleep -Seconds 2

# Test Case 5: Forwarded email
Write-Host "Test 5: Forwarded email with 'Fwd:' prefix (should dedupe)" -ForegroundColor Yellow
$email5 = @{
    subject = "Fwd: Cannot access dashboard"
    body = "Forwarding this issue to you. Original message: I'm unable to login."
    sender = "john@company.com"
} | ConvertTo-Json

$response5 = Invoke-RestMethod -Uri $baseUrl -Method POST -Body $email5 -ContentType "application/json"
Write-Host "  Ticket ID: $($response5.ticket_id)" -ForegroundColor $(if ($response5.ticket_id -eq $ticketId) { "Green" } else { "Red" })
Write-Host "  Is Duplicate: $($response5.deduplication.is_duplicate)" -ForegroundColor $(if ($response5.deduplication.is_duplicate) { "Green" } else { "Red" })
Write-Host ""

Start-Sleep -Seconds 2

# Test Case 6: Different sender, different topic (should NOT dedupe)
Write-Host "Test 6: Different sender, different topic (should create new)" -ForegroundColor Yellow
$email6 = @{
    subject = "Payment issue"
    body = "My credit card was charged twice this month."
    sender = "sarah@company.com"
} | ConvertTo-Json

$response6 = Invoke-RestMethod -Uri $baseUrl -Method POST -Body $email6 -ContentType "application/json"
$newTicketId = $response6.ticket_id
Write-Host "  Ticket ID: $newTicketId" -ForegroundColor $(if ($newTicketId -ne $ticketId) { "Green" } else { "Red" })
Write-Host "  Is Duplicate: $($response6.deduplication.is_duplicate)" -ForegroundColor $(if (-not $response6.deduplication.is_duplicate) { "Green" } else { "Red" })
Write-Host ""

Start-Sleep -Seconds 2

# Test Case 7: Bracket-style ticket reference [Ticket #12345]
Write-Host "Test 7: Bracket-style reference [Ticket #$ticketId] (should dedupe)" -ForegroundColor Yellow
$email7 = @{
    subject = "[Ticket #$ticketId] - Update needed"
    body = "Please update the status of this ticket."
    sender = "john@company.com"
} | ConvertTo-Json

$response7 = Invoke-RestMethod -Uri $baseUrl -Method POST -Body $email7 -ContentType "application/json"
Write-Host "  Ticket ID: $($response7.ticket_id)" -ForegroundColor $(if ($response7.ticket_id -eq $ticketId) { "Green" } else { "Red" })
Write-Host "  Is Duplicate: $($response7.deduplication.is_duplicate)" -ForegroundColor $(if ($response7.deduplication.is_duplicate) { "Green" } else { "Red" })
Write-Host ""

Write-Host "`n=========================================" -ForegroundColor Cyan
Write-Host "  SUMMARY" -ForegroundColor Cyan
Write-Host "=========================================`n" -ForegroundColor Cyan

$dedupeCount = 0
if ($response2.deduplication.is_duplicate) { $dedupeCount++ }
if ($response3.deduplication.is_duplicate) { $dedupeCount++ }
if ($response4.deduplication.is_duplicate) { $dedupeCount++ }
if ($response5.deduplication.is_duplicate) { $dedupeCount++ }
if ($response7.deduplication.is_duplicate) { $dedupeCount++ }

Write-Host "Original Ticket Created: $ticketId" -ForegroundColor Green
Write-Host "Successfully Deduped: $dedupeCount / 5 tests" -ForegroundColor $(if ($dedupeCount -eq 5) { "Green" } else { "Yellow" })
Write-Host "New Ticket Created: $newTicketId (Expected: Different)" -ForegroundColor Green
Write-Host ""

if ($dedupeCount -eq 5) {
    Write-Host "✅ All deduplication tests passed!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Some deduplication tests failed" -ForegroundColor Yellow
}
Write-Host ""
