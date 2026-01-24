"""
Test Script: Urgency Detection & Severity Classification
Tests the comprehensive urgency detection system with various scenarios
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ai.urgency import urgency_detector
from colorama import init, Fore, Style

init()

def print_result(title, urgency_result):
    """Pretty print urgency detection results"""
    print(f"\n{Fore.CYAN}{'='*80}")
    print(f"{title}")
    print(f"{'='*80}{Style.RESET_ALL}")
    
    severity = urgency_result['severity']
    color = {
        'P1': Fore.RED,
        'P2': Fore.YELLOW,
        'P3': Fore.BLUE,
        'P4': Fore.GREEN
    }.get(severity, Fore.WHITE)
    
    print(f"{color}Severity: {severity} - {urgency_result['severity_name']}")
    print(f"SLA: {urgency_result['sla_hours']} hours")
    print(f"Auto-Escalate: {'YES ⚠️' if urgency_result['auto_escalate'] else 'No'}{Style.RESET_ALL}")
    print(f"Reasoning: {urgency_result['reasoning']}")
    print(f"\nDetected Signals:")
    for signal in urgency_result.get('signals', []):
        print(f"  • {signal}")

def test_urgency_detection():
    """Test various email scenarios"""
    
    test_cases = [
        {
            "name": "❗ P1: ALL CAPS with Emergency",
            "subject": "URGENT!! SYSTEM DOWN!!!",
            "body": "THE ENTIRE PRODUCTION SYSTEM IS DOWN! ALL USERS ARE AFFECTED! THIS IS AN EMERGENCY!",
            "category": "Technical Support"
        },
        {
            "name": "💰 P1: Business Impact (Revenue Loss)",
            "subject": "Critical Issue - Losing Money",
            "body": "Our payment system has been down for 2 hours. We're losing money with every minute. Customers are complaining and we cannot process any orders. This is costing us thousands!",
            "category": "Technical Support"
        },
        {
            "name": "⚖️ P1: Legal Escalation",
            "subject": "Final Warning - Legal Action",
            "body": "This is unacceptable. I've contacted my lawyer and if this isn't resolved immediately, I will pursue legal action. I'm also requesting a full refund.",
            "category": "Complaint/Escalation"
        },
        {
            "name": "📈 P1: 3rd Follow-up Auto-Escalation",
            "subject": "Re: Re: Re: Still not working",
            "body": "This is the third time I'm reaching out. Nothing has been done. This is extremely frustrating.",
            "category": "Technical Support",
            "followup_count": 3
        },
        {
            "name": "🔥 P2: High Priority with Time Sensitivity",
            "subject": "Major Feature Broken - Need Fix Today",
            "body": "Our main reporting feature is not working. This is blocking our team and we need this fixed today. It's affecting multiple users.",
            "category": "Technical Support"
        },
        {
            "name": "😤 P2: Emotional Language & Frustration",
            "subject": "This is ridiculous!!!",
            "body": "I am so frustrated and disappointed. This has been broken for days and no one is helping. This is completely unacceptable!",
            "category": "Complaint/Escalation"
        },
        {
            "name": "🔔 P2: Multiple Exclamations",
            "subject": "Help!!!! Urgent!!! Important!!!",
            "body": "I need help with this important issue!!! It's been causing problems!!!",
            "category": "General Inquiry"
        },
        {
            "name": "🟦 P3: Minor Issue",
            "subject": "Small bug in report export",
            "body": "When I export reports, the date format is slightly off. Not urgent but would be nice to fix when possible.",
            "category": "Technical Support"
        },
        {
            "name": "💡 P4: Feature Request",
            "subject": "Suggestion for improvement",
            "body": "It would be nice to have a dark mode option. Not urgent, just a suggestion for a future enhancement.",
            "category": "Feature Request"
        },
        {
            "name": "🔍 Mixed Signals: Business Impact + Time Sensitive",
            "subject": "Customers waiting - need fix ASAP",
            "body": "We have customers waiting for this to be fixed. The system is not working properly and we need this resolved as soon as possible.",
            "category": "Technical Support"
        }
    ]
    
    print(f"\n{Fore.MAGENTA}{'='*80}")
    print("URGENCY & SEVERITY CLASSIFICATION TEST SUITE")
    print(f"{'='*80}{Style.RESET_ALL}\n")
    print("Testing comprehensive signal detection:")
    print("  • Tone Analysis (ALL CAPS, emotional language)")
    print("  • Business Impact (revenue, customers, production)")
    print("  • Time Sensitivity (urgent, ASAP, emergency)")
    print("  • Escalation Keywords (lawyer, refund, cancel)")
    print("  • Follow-up Tracking (auto-escalate on 3rd follow-up)")
    
    for test in test_cases:
        result = urgency_detector.detect_urgency(
            subject=test['subject'],
            body=test['body'],
            category=test['category'],
            followup_count=test.get('followup_count', 0)
        )
        print_result(test['name'], result)
    
    print(f"\n{Fore.GREEN}{'='*80}")
    print("✅ Test suite completed!")
    print(f"{'='*80}{Style.RESET_ALL}\n")

if __name__ == "__main__":
    test_urgency_detection()
