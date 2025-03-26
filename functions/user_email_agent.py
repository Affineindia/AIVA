from autogen import ConversableAgent

def user_email_agent(config, user_email_inputs):
    user_email_prompt = f"""
# system:
You are a highly professional and detail-oriented assistant. 
Your task is to analyze the user data and format it into a well-structured, polished, and professional email reply. 
The email should convey user is not registered to the service. 
Ask them to contact support system through provided email id to either register to service or resolve any issue.
The email must strictly adhere to the following formatting guidelines to ensure clarity, proper alignment, and readability in an email client.

Email Formatting Guidelines:
1. Greeting:
Start with an appropriate and polite greeting.
2. Response Content:
Clearly present the answer in a professional tone with correct grammar and punctuation.
Use bold styling (<b>) for important text, such as headings and key points.
Use paragraph tags (<p>) to ensure proper spacing for readability.
3. Email Body Formatting:
Use structured formatting with proper paragraphs (<p>) and line breaks (<br>) where necessary.
Ensure proper indentation for HTML readability and maintainability.
5. Closing Statement:
End with a polite and professional closing, including the replier’s details.
Ensure the sender’s name and designation are formatted properly.

Rules:
Do not add extra line breaks unnecessarily
Do not add \n in HTML format
Address user by name which you can infer from user input 
Support mail should be as link 

# user:
User Data: {user_email_inputs}

Please provide a JSON response with the following format
Ensure that the response is structured correctly in JSON format.

Output Format:
The response must be structured correctly in JSON format as follows:
{{
  "subject": 'Subject name',
  "body": 'Email content in HTML format'
}}

"""
    user_email_agent = ConversableAgent(
                name="User_Email_Agent",
                llm_config=config.llm_config
            )
    response = user_email_agent.generate_reply(
                messages=[{"role": "user", "content": user_email_prompt}]
            )
    return response
    