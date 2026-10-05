"""
Job-seeker focused Jev question schema.

Goal: Cut through job application noise. Surface only what matters:
  - Emails that need YOUR reply
  - Shortlisting / interview invites
  - Silently skip auto-acks (Applied/Thanks/Welcome) and platform notifications
"""

JOB_ACKNOWLEDGEMENT_SENDERS = [
    "indeed", "linkedin", "naukri", "glassdoor", "talent500",
    "shazamme", "lever.co", "myworkday", "workday", "greenhouse",
    "ashby", "teamtailor", "smartrecruiters", "icims"
]


def get_questions_schema():
    return {

        # --- CORE: What matters most ---

        "needs_response": {
            "type": "noul",
            "instructions": "Does this email require a direct, manual email reply from the user to a real human? Do NOT flag automated buttons, LinkedIn connection requests, marketing 'Register Now' links, or 'Confirm subscription' links.",
            "criteria": {
                "true": "A real human (like a recruiter or colleague) is explicitly waiting for an email reply, an interview time, or a document attachment.",
                "false": "It is an automated email, a platform notification (LinkedIn), a newsletter, or just asking to click a generic 'Register' or 'Confirm' button."
            }
        },

        "is_shortlisted": {
            "type": "noul",
            "instructions": "Does this email indicate the recipient has been selected, shortlisted, passed a screening stage, or invited for an interview or assessment?",
            "criteria": {
                "true": "The email says the recipient is selected, shortlisted, moved forward, invited for interview, or has passed a stage.",
                "false": "The email does not indicate selection or advancement in a hiring process."
            }
        },

        "is_acknowledgement": {
            "type": "noul",
            "instructions": "Is this email an automatic acknowledgement sent by a hiring system confirming it received an application? Examples: 'Thank you for applying', 'We have received your application', 'Your application has been submitted'.",
            "criteria": {
                "true": "This is an automatic system confirmation that the application was received. No action is needed.",
                "false": "This is not just a submission confirmation email."
            }
        },

        "is_platform_notification": {
            "type": "noul",
            "instructions": "Is this an automated notification from a job platform, professional network, or recruitment tool (LinkedIn, Indeed, Naukri, Glassdoor, Talent500, etc.) that is informational only, such as a job alert, profile view, connection request, or recommendation?",
            "criteria": {
                "true": "Automated platform notification: job alert, profile view, connection, digest, recommendation — does not require a reply.",
                "false": "Not a routine platform notification."
            }
        },

        "is_rejection": {
            "type": "noul",
            "instructions": "Is this email a rejection notice, informing the recipient they were not selected for a role or that the position has been filled?",
            "criteria": {
                "true": "The email explicitly or implicitly says the recipient was not selected, the role is filled, or they are no longer being considered.",
                "false": "This email is not a rejection."
            }
        },

        "has_important_info": {
            "type": "noul",
            "instructions": "Does this email contain specific, actionable information the recipient needs to know — such as a salary, joining date, location, schedule, deadline, link to a test/assessment, or next steps?",
            "criteria": {
                "true": "The email contains specific information (dates, salary, links, location, next steps) the recipient should know.",
                "false": "The email does not contain specific important information."
            }
        },

        "is_verification_code": {
            "type": "noul",
            "instructions": "Is this email just a verification code, OTP (one-time password), or login link?",
            "criteria": {
                "true": "The email is a verification code, OTP, 2FA, or login link.",
                "false": "The email is not a verification code."
            }
        },

        "is_financial": {
            "type": "noul",
            "instructions": "Is this email a genuine bank alert (OTP, payment made, money received, bill generated)? Do NOT count credit card offers, loan advertisements, or insurance promotions.",
            "criteria": {
                "true": "Genuine transaction, payment, bill, or OTP.",
                "false": "Not a genuine transaction alert (e.g. promotional offer, loan advert)."
            }
        },

        "is_spam_or_promo": {
            "type": "noul",
            "instructions": "Is this email purely promotional, newsletter, or unsolicited marketing content with no relevance to a job search?",
            "criteria": {
                "true": "Marketing email, promotional offer, newsletter, or spam with no job-search relevance.",
                "false": "Not purely promotional content."
            }
        }
    }


def format_state(email_data):
    body = email_data.get("body_text") or email_data.get("snippet", "")
    return (
        f"From: {email_data.get('sender', '')}\n"
        f"To: {email_data.get('recipients', '')}\n"
        f"Date: {email_data.get('date', '')}\n"
        f"Subject: {email_data.get('subject', '')}\n\n"
        f"Body:\n{body}"
    )
