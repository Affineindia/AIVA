from autogen import ConversableAgent

def content_email_agent(config, content_inputs):
    content_email_prompt = f"""
# system:
You are a highly professional and detail-oriented assistant. 
Your task is to analyze the user data and format it into a well-structured, polished, and professional email reply. 
The email should convey there query has voilating content based on analysing the given classification result. Ask them to modify there query or attachments accordingly based on the user input.
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

Example Body content without formating:
I hope you're doing well. After reviewing your query, we found that it does not align with our content guidelines.
Due to this, we are unable to process your submission in its current form.
We kindly request you to **modify** your query to ensure it adheres to our guidelines. 
If you need further clarification, feel free to reach out.

Rules:
Do not add extra line breaks unnecessarily
Do not add \n in HTML format

# user:
User data:
{content_inputs}

Please provide a JSON response with the following format
Ensure that the response is structured correctly in JSON format.
Output Format : {{
  "subject": 'Subject name',
  "body": 'Email content in HTML format',
  "classes": ""
}}

"""
    content_email_agent = ConversableAgent(
                name="Content_Email_Agent",
                llm_config=config.llm_config
            )
    response = content_email_agent.generate_reply(
                messages=[{"role": "user", "content": content_email_prompt}]
            )
    return response
    