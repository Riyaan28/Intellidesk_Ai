"""
Intelligent Resolution Template Generator
Generates calm, polite, consistent responses based on ticket category and tone
"""

from typing import Dict

# Category-specific resolution templates
RESOLUTION_TEMPLATES = {
    "Technical Support": """Dear {name},

Thank you for reaching out to us regarding the technical issue you're experiencing.

I understand this has been frustrating for you, and I appreciate your patience. Our team has reviewed your case, and here's what we can do to help:

{resolution_steps}

Please try these steps and let me know if the issue persists. I'm here to help ensure everything works smoothly for you.

If you need any additional assistance, feel free to reach out anytime.

Best regards,
Support Team""",

    "Access Request": """Dear {name},

Thank you for contacting us regarding your access request.

I completely understand the urgency of getting access to the system. Here's what I've done to help:

{resolution_steps}

Your access should now be active. Please try logging in and let me know if you face any difficulties.

We're here to help if you need anything else!

Best regards,
Support Team""",

    "Billing/Invoice": """Dear {name},

Thank you for reaching out about your billing inquiry.

I appreciate you bringing this to our attention. I've carefully reviewed your account and here's the update:

{resolution_steps}

If you have any questions about these charges or need further clarification, please don't hesitate to ask. We're committed to ensuring transparency in all our billing matters.

Thank you for your patience and understanding.

Best regards,
Support Team""",

    "Feature Request": """Dear {name},

Thank you for taking the time to share your feature suggestion with us!

We really appreciate customers like you who help us improve our product. Your feedback is valuable to our development team.

{resolution_steps}

We'll keep you updated on the progress of this request. Your input helps us build better solutions for everyone.

Thank you for being a valued customer!

Best regards,
Support Team""",

    "Hardware/Infrastructure": """Dear {name},

Thank you for reporting this infrastructure issue.

I understand how important system reliability is for your operations. Here's what we've done to address your concern:

{resolution_steps}

We're monitoring the situation closely to ensure everything remains stable. If you notice any further issues, please let us know immediately.

Thank you for your patience and for helping us maintain a better system.

Best regards,
Support Team""",

    "How-To/Documentation": """Dear {name},

Thank you for reaching out with your question!

I'm happy to help you understand how to {topic}. Here's a step-by-step guide:

{resolution_steps}

I hope this clarifies things for you! If you need any further explanation or have additional questions, please feel free to ask.

We're here to make sure you get the most out of our platform.

Best regards,
Support Team""",

    "Data Request": """Dear {name},

Thank you for your data request.

We take data privacy and transparency very seriously. Here's what I've prepared for you:

{resolution_steps}

If you need any additional data or have questions about what we've provided, please let me know. We're committed to your privacy and data rights.

Best regards,
Support Team""",

    "Complaint/Escalation": """Dear {name},

Thank you for bringing your concerns to our attention.

I sincerely apologize for any inconvenience or frustration this situation has caused you. Your feedback is extremely important to us, and I want to make things right.

Here's what I'm doing to resolve this:

{resolution_steps}

I truly appreciate your patience and the opportunity to address your concerns. If there's anything else I can do to improve your experience, please don't hesitate to let me know.

Thank you for giving us the chance to make this better.

Best regards,
Support Team""",

    "General Inquiry": """Dear {name},

Thank you for contacting us!

I appreciate you reaching out with your question. Here's the information you requested:

{resolution_steps}

If you need any further clarification or have additional questions, please feel free to ask. We're always happy to help!

Best regards,
Support Team""",
}


def detect_angry_tone(email_body: str) -> bool:
    """
    Detect if email has angry/frustrated tone
    """
    angry_keywords = [
        'angry', 'furious', 'frustrated', 'disappointed', 'unacceptable',
        'terrible', 'horrible', 'worst', 'disgusted', 'fed up',
        'ridiculous', 'pathetic', 'useless', 'waste', 'incompetent',
        'stupid', 'idiotic', 'sick of', 'tired of', 'enough',
        'cancel', 'refund', 'lawsuit', 'lawyer', 'complaint',
        '!!!', 'URGENT', 'IMMEDIATELY', 'ASAP'
    ]
    
    email_lower = email_body.lower()
    
    # Check for angry keywords
    for keyword in angry_keywords:
        if keyword in email_lower:
            return True
    
    # Check for excessive caps (more than 30% of words in caps)
    words = email_body.split()
    caps_count = sum(1 for word in words if word.isupper() and len(word) > 2)
    if len(words) > 0 and caps_count / len(words) > 0.3:
        return True
    
    return False


def generate_resolution_template(
    category: str,
    sender_name: str,
    email_body: str,
    subject: str = "",
    custom_steps: str = None
) -> str:
    """
    Generate intelligent resolution template based on category and tone
    
    Args:
        category: Ticket category
        sender_name: Name of sender (extracted from email)
        email_body: Original email body
        subject: Email subject
        custom_steps: Custom resolution steps (optional)
    
    Returns:
        Formatted resolution email text
    """
    # Extract first name from email
    name = sender_name.split('@')[0].split('.')[0].capitalize()
    
    # Detect if email has angry tone
    is_angry = detect_angry_tone(email_body)
    
    # Get template for category
    template = RESOLUTION_TEMPLATES.get(
        category,
        RESOLUTION_TEMPLATES["General Inquiry"]
    )
    
    # If email is angry/frustrated, add extra empathy
    if is_angry:
        # Make template more empathetic and apologetic
        if "Complaint/Escalation" not in category:
            template = template.replace(
                "Thank you for",
                "Thank you so much for"
            ).replace(
                "I understand",
                "I completely understand your frustration, and I sincerely apologize for"
            )
    
    # Prepare resolution steps
    if custom_steps:
        resolution_steps = custom_steps
    else:
        # Default resolution steps based on category
        resolution_steps = _get_default_steps(category, subject, email_body)
    
    # Extract topic for How-To category
    topic = subject.lower().replace('re:', '').strip() if subject else "use this feature"
    
    # Format template
    formatted_template = template.format(
        name=name,
        resolution_steps=resolution_steps,
        topic=topic
    )
    
    return formatted_template


def _get_default_steps(category: str, subject: str, body: str) -> str:
    """
    Generate default resolution steps based on category
    """
    default_steps = {
        "Technical Support": """1. I've reviewed your technical issue
2. Our team has identified the root cause
3. We've applied a fix/workaround that should resolve the problem
4. Please try again and confirm if the issue persists

If you continue to experience issues, I'm here to help further.""",

        "Access Request": """1. I've reviewed your access request
2. Your account permissions have been updated
3. You should now have access to the requested resources
4. Please log out and log back in to refresh your session

Let me know if you need access to anything else.""",

        "Billing/Invoice": """1. I've thoroughly reviewed your billing statement
2. The charges are for [service/product details]
3. Everything appears to be in order with your account
4. I've sent a detailed invoice breakdown to your email

Please review and let me know if you have any questions.""",

        "Feature Request": """1. I've logged your feature request in our system
2. Our product team will review it in the next planning cycle
3. We'll consider it based on customer demand and technical feasibility
4. You'll receive updates on its status via email

Thank you for helping us improve!""",

        "Hardware/Infrastructure": """1. I've investigated the infrastructure issue
2. Our team has resolved the underlying problem
3. All systems are now operating normally
4. We've implemented additional monitoring to prevent recurrence

Please let me know if you notice any further issues.""",

        "How-To/Documentation": """1. [Step-by-step instructions for your query]
2. You can also refer to our documentation at [link]
3. Video tutorials are available at [link]
4. Feel free to reach out if you need clarification on any step

I'm here to help you succeed!""",

        "Data Request": """1. I've compiled the data you requested
2. Please find the attached/linked information
3. All data has been prepared according to privacy regulations
4. Let me know if you need any additional information

Your data privacy is our priority.""",

        "Complaint/Escalation": """1. I've escalated your case to our senior team
2. We're conducting a thorough investigation
3. We're taking immediate steps to prevent this from happening again
4. I'll personally follow up with you on the resolution progress

Your satisfaction is our top priority.""",

        "General Inquiry": """I've reviewed your inquiry and here's the information:

[Relevant information based on your question]

I hope this answers your question completely."""
    }
    
    return default_steps.get(category, "I've reviewed your request and will provide you with a detailed response shortly.")
