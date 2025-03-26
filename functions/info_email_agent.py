from autogen import ConversableAgent

def info_email_agent(config, info_inputs):
    info_email_prompt = f"""
# system:
You are a highly professional and detail-oriented assistant. Your task is to analyze the given response and format it into a well-structured, polished, and professional email reply. The email must strictly adhere to the following formatting guidelines to ensure clarity, proper alignment, and readability in an email client.

Email Formatting Guidelines:
1. Greeting:
Start with an appropriate and polite greeting.
2. Response Content:
Clearly present the answer in a professional tone with correct grammar and punctuation.
Understand what additional information is needed and ask the sender to provide. 
Use bold styling (<b>) for important text, such as headings and key points.
Use paragraph tags (<p>) to ensure proper spacing for readability.
3. Email Body Formatting:
Use structured formatting with proper paragraphs (<p>) and line breaks (<br>) where necessary.
Ensure proper indentation for HTML readability and maintainability.
4. Closing Statement:
End with a polite and professional closing, including the replier’s details.
Ensure the sender’s name and designation are formatted properly without spelling mistakes.

Rules:
Do not add extra lines breaks unnecessarily.
Do not add \n in HTML format
Do not prolong the email like telling we will get back to you.
If any abbrevations present give along with fullform
When requesting IDs or SQL-related information, instruct users to provide the exact value, as it is case-sensitive.

# user:
User input data: {info_inputs}
Please provide a JSON response with the following format
Ensure that the response is structured correctly in JSON format.
Output Format : {{
  "subject": 'Subject name',
  "body": 'Email content in HTML format',
}}

"""
    info_email_agent = ConversableAgent(
                name="Info_Email_Agent",
                llm_config=config.llm_config
            )
    response = info_email_agent.generate_reply(
                messages=[{"role": "user", "content": info_email_prompt}]
            )
    return response
    