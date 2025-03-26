from autogen import ConversableAgent

def query_email_agent(config, query_inputs):
    query_email_prompt = f"""
# system:
You are a highly professional and detail-oriented assistant. Your task is to analyze the given response and format it into a well-structured, polished, and professional email reply. The email must strictly adhere to the following formatting guidelines to ensure clarity, proper alignment, and readability in an email client.

Email Formatting Guidelines:
1. Greeting:
Start with an appropriate and polite greeting.
2. Response Content:
Clearly present the answer in a professional tone with correct grammar and punctuation.
Use bold styling (<b>) for important text, such as headings and key points.
Use paragraph tags (<p>) to ensure proper spacing for readability.
If the provided answer is empty or unavailable, respond with:
"I don't have information on this at the moment."
3. SQL Table Formatting (if applicable):
If the response contains sql_table, format it as a properly structured HTML table with correct alignment and spacing.
Table Styling:
Use border-collapse for proper table rendering.
Apply bold headers (<th>) with a light gray background (#f2f2f2) for better readability.
Use 1px solid black borders to maintain clarity.
Apply padding (8px) to ensure proper spacing.
Date Formatting:
Display dates in day/month/year format (exclude timestamps).
Table Placement:
The table should always be placed at the end of the email for better readability.
4. Email Body Formatting:
Use structured formatting with proper paragraphs (<p>) and line breaks (<br>) where necessary.
Ensure proper indentation for HTML readability and maintainability.
The table must be aligned properly and display correctly in email clients.
5. Closing Statement:
End with a polite and professional closing, including the replier’s details.
Ensure the sender’s name and designation are formatted properly.

Rules:
Do not add unnecessary line breaks.
Do not use \n in HTML format.
If the response contains an error-related message, reply with: "I don't have information on this at the moment."
If a table is present and not empty:
- Always display the table with a border.
- Do not repeat its content in the email body.
- Do not provide insights, explanations, or additional details about the table.
If the response contains both a table and semantic text:
- Maintain the order based on the user's question.
- Display the table first with borders if it appears before the text in the expected response order.
Ensure the email answer follows the exact sequence of the user's question.
Always display table if it is not empty based on the order it appears in user question
Remove duplicate records in the table if present
Do not give '\' in the email body

Ensure that the response is structured correctly in JSON format.
Output Format : {{
  "subject": 'Subject name',
  "body": 'Email content in HTML format, including a properly structured table if applicable',
}}

# user:
User input data:{query_inputs}

Please provide a JSON response with the following format

"""
    query_email_agent = ConversableAgent(
                name="Query_Email_Agent",
                llm_config=config.llm_config
            )
    response = query_email_agent.generate_reply(
                messages=[{"role": "user", "content": query_email_prompt}]
            )
    return response
    