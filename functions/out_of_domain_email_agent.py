from autogen import ConversableAgent

def out_of_domain_email_agent(config, out_of_domain_inputs):
    out_of_domain_email_prompt = f"""
# system:
You are a highly professional and detail-oriented assistant.
Your task is to generate a professional email response while strictly adhering to the given formatting guidelines.

Email Formatting Guidelines:
Greeting:
Begin with an appropriate and polite greeting.

Email Body Formatting:
Clearly inform the sender that their query is out of scope and should be restricted to the domain
Use structured formatting with proper paragraphs (<p>) and line breaks (<br>) where necessary.
Ensure correct indentation for HTML readability and maintainability.

Closing Statement:
Conclude with a polite and professional closing, including the replier’s details.
Format the sender’s name and designation correctly, ensuring no spelling mistakes.

Rules:
Do not add extra line breaks unnecessarily.
Do not use \n in the HTML format.

# user:
User input data: {out_of_domain_inputs}

Output Format:
The response must be structured correctly in JSON format as follows:
{{
  "subject": 'Subject name',
  "body": 'Email content in HTML format'
}}

"""
    out_of_domain_email_agent = ConversableAgent(
                name="Out_Of_Domain_Email_Agent",
                llm_config=config.llm_config
            )
    response = out_of_domain_email_agent.generate_reply(
                messages=[{"role": "user", "content": out_of_domain_email_prompt}]
            )
    return response
    