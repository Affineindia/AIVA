def call_airis_agentic_flow(airis_agentic_flow_input):

    ############################################# INPORTS AND INITIATIONS ###########################################

    from setting.configurations import Config
    from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
    # from azure.search.documents.models import Vector
    from azure.search.documents.models import (
        QueryAnswerType,
        QueryCaptionType,
        QueryType,
        VectorizedQuery,    
    )
    from functions.utils import clean_json
    import sys
    sys.stdout.reconfigure(encoding='utf-8')

    config = Config()
    num_iterations = 3

    ################################################ PROMPT VARIABLES ##############################################

    metadata = """
        Metadata for table AIRIS_Delivery_Details:
        Column Name: Order_Id, Type: VARCHAR COLLATE "SQL_Latin1_General_CP1_CI_AS"
        Column Name: Delivery_Status, Type: VARCHAR COLLATE "SQL_Latin1_General_CP1_CI_AS"
        Column Name: Expected_Delivery_Date, Type: VARCHAR COLLATE "SQL_Latin1_General_CP1_CI_AS"


        Metadata for table AIRIS_Inventory_Details:
        Column Name: Product_Id, Type: VARCHAR COLLATE "SQL_Latin1_General_CP1_CI_AS"
        Column Name: Quantity_Left, Type: INTEGER


        Metadata for table AIRIS_Order_Details:
        Column Name: Customer_Id, Type: VARCHAR COLLATE "SQL_Latin1_General_CP1_CI_AS"
        Column Name: Order_Id, Type: VARCHAR COLLATE "SQL_Latin1_General_CP1_CI_AS"
        Column Name: Order_Date, Type: VARCHAR COLLATE "SQL_Latin1_General_CP1_CI_AS"


        Metadata for table AIRIS_Order_Summary:
        Column Name: Order_Id, Type: VARCHAR COLLATE "SQL_Latin1_General_CP1_CI_AS"
        Column Name: Product_Id, Type: VARCHAR COLLATE "SQL_Latin1_General_CP1_CI_AS"
        Column Name: Product_Quantity, Type: INTEGER


        Metadata for table AIRIS_Product_Details:
        Column Name: Product_Id, Type: VARCHAR COLLATE "SQL_Latin1_General_CP1_CI_AS"
        Column Name: Product_Name, Type: VARCHAR COLLATE "SQL_Latin1_General_CP1_CI_AS"
        Column Name: Product_Category, Type: VARCHAR COLLATE "SQL_Latin1_General_CP1_CI_AS"
        Column Name: Product_Price, Type: INTEGER


        Metadata for table AIRIS_Refund_Details:
        Column Name: Order_Id, Type: VARCHAR COLLATE "SQL_Latin1_General_CP1_CI_AS"
        Column Name: Refund_Status, Type: VARCHAR COLLATE "SQL_Latin1_General_CP1_CI_AS"
        Column Name: Refund_Amount, Type: FLOAT
        Column Name: Expected_Refund_Date, Type: VARCHAR COLLATE "SQL_Latin1_General_CP1_CI_AS"


        Metadata for table AIRIS_User_Details:
        Column Name: Email_Id, Type: VARCHAR COLLATE "SQL_Latin1_General_CP1_CI_AS"
        Column Name: User_Name, Type: VARCHAR COLLATE "SQL_Latin1_General_CP1_CI_AS"
        Column Name: Customer_Id, Type: VARCHAR COLLATE "SQL_Latin1_General_CP1_CI_AS"

        """

    search_index_data = """
    SEARCH INDEX FILEDS
"fields": [
    {
      "name": "product_name",
      "type": "Edm.String",
      "searchable": true,
      "filterable": true,
      "retrievable": true,
      "stored": true,
      "sortable": false,
      "facetable": false,
      "key": false,
      "synonymMaps": []
    },
    {
      "name": "product_category",
      "type": "Edm.String",
      "searchable": true,
      "filterable": true,
      "retrievable": true,
      "stored": true,
      "sortable": false,
      "facetable": false,
      "key": false,
      "synonymMaps": []
    },
    {
      "name": "entry_ID",
      "type": "Edm.String",
      "searchable": true,
      "filterable": true,
      "retrievable": true,
      "stored": true,
      "sortable": false,
      "facetable": false,
      "key": true,
      "synonymMaps": []
    },
    {
      "name": "product_document_content",
      "type": "Edm.String",
      "searchable": true,
      "filterable": true,
      "retrievable": true,
      "stored": true,
      "sortable": false,
      "facetable": false,
      "key": false,
      "synonymMaps": []
    },
    {
      "name": "product_document_embedding",
      "type": "Collection(Edm.Single)",
      "searchable": true,
      "filterable": false,
      "retrievable": false,
      "stored": true,
      "sortable": false,
      "facetable": false,
      "key": false,
      "dimensions": 1536,
      "vectorSearchProfile": "myHnswProfile",
      "synonymMaps": []
    },
    {
      "name": "product_image_url",
      "type": "Edm.String",
      "searchable": true,
      "filterable": true,
      "retrievable": true,
      "stored": true,
      "sortable": false,
      "facetable": false,
      "key": false,
      "synonymMaps": []
    },
    {
      "name": "product_image_embedding",
      "type": "Collection(Edm.Single)",
      "searchable": true,
      "filterable": false,
      "retrievable": false,
      "stored": true,
      "sortable": false,
      "facetable": false,
      "key": false,
      "dimensions": 1024,
      "vectorSearchProfile": "myHnswProfile",
      "synonymMaps": []
    }
  ],
"""

    ################################################ USER PROXY AGENT ##############################################

    user_proxy = UserProxyAgent(
        name="user_proxy",
        system_message="""You are the User Proxy Agent. 
        Your role is to manage the flow of information between the user and routing agent. 
        When a user provides a question, email_id and attachments (if any), pass these to the routing_agent without modification.""",
        code_execution_config={
            "work_dir": "Routing_File",
            "use_docker": False,
        },
        max_consecutive_auto_reply=num_iterations,
        llm_config=config.llm_config,
        human_input_mode="NEVER",
        is_termination_msg=lambda msg: msg["content"]
    )

    ################################################ ROUTING AGENT ##############################################

    routing_agent = AssistantAgent(
        name="routing_agent",
        system_message=f"""
You are an Expert Router Agent responsible for analyzing user queries and attachment data and determining the correct processing path.  
The goal is to design step by step process path and directions to run the process for achieving correct answer.
The system has below different agents for executing different tasks.
    - Quin_Agent (Database related) - This agent is used to answer user query related to database tables (AIRIS_Delivery_Details, AIRIS_Inventory_Details, AIRIS_Order_Details, AIRIS_Order_Summary, AIRIS_Product_Details, AIRIS_Refund_Details, AIRIS_User_Details)
    - Eryl_Agent (Documentation related) - This agent is useful for getting product information from search index by calling function 'execute_search'. Information regarding product rating, return policies, descriptions, products website images can be searched. 
    - Insight_Agent - This agent analyses complete process response and generates final answer based on instruction provided and user question
Based on the user query and analysing the SQL database metadata and Eryl searchable fields data design the process

{metadata}

{search_index_data}

Example scenerio and logic of process:

Example 1 - New refund claims -> Send attachment details to Eryl_Agent to get Product_Name -> ask Quin Agent to check customer latest delivered order and product details like all product name, quantity ordered, product price -> Send Eryl_Agent and Quin_Agent responses to Insight_Agent to give final answer that is check the matched products and calculate the refund amount eligible. Be cautious user can give multiple images for same product
Example 2 - Similar products -> pass user query and attachment details (if any) to Quin_Agent to get similar products with their details -> Insight_Agent for final response

Rules:
- By analysing the given example scenerios logically be smart to design optimal steps for new scenerios also
- You can have multiple steps in the process
- Make sure you design steps logically with less number of steps
- All information related to database can be fetched at a time using joins
- Always last agent should be Insight_Agent to format end user response
- Logically create Quin_Agent steps if applicable, so that accurate information is extracted based on user question
- Make process simple and stick to the user question. No need to always call Quin_Agent and Eryl_Agent for generic questions like "analyze the image"
- For recommendation always confirm product details by Eryl_Agent first

Output Format ( STRICTLY GIVE JSON OUTPUT)

{{
    "User_question": question,
    "Process": {{
        "Step_<number>": {{
            "name": "name of the agent",
            "instruction": "Give detailed directions to execute the step".
        }},
    }},
    "Next_step": "Step_1"
    "Next_agent": "name of Step_1"
}}

Important:
- Analyse the provided examples scenerios properly and form the process accordingly
- If new scenerio is presented optimally design the process with your understanding of different agents and there use 
- Always get correct product name from Eryl_Agent before sending to Quin_Agent
- Refund_Details table present in database only has information about existing refund orders. Question related to new claims or refund eligibility should not use the table data
- **Always last Step should be Insight_Agent to format end user response**
    """,
        max_consecutive_auto_reply=num_iterations,
        llm_config=config.llm_config,
        human_input_mode="NEVER"
    )

    ################################################ ROUTING CRITIC AGENT ##############################################

    routing_critic_agent = AssistantAgent(
        name="routing_critic_agent",
        system_message=f"""
You are an Expert Router Critic Agent responsible for checking if routing_agent response is good or not.  
Rules:
- Check if process designed by routing agent is optimal efficient and logical to answer user question
- check if process adheres to routing_agent rules
- 

Output Format ( STRICTLY GIVE JSON OUTPUT)

{{
    "User_question": question,
    "Process": {{
        "Step_<number>": {{
            "name": "name of the agent",
            "instruction": "Give detailed directions to execute the step".
        }},
    }},
    "Next_step": "Step_1"
    "Next_agent": "name of Step_1"
}}

Important:
- Analyse the provided examples scenerios properly and form the process accordingly
- If new scenerio is presented optimally design the process with your understanding of different agents and there use 
- Always get correct product name from Eryl_Agent before sending to Quin_Agent
- Refund_Details table present in database only has information about existing refund orders. Question related to new claims or refund eligibility should not use the table data

    """,
        max_consecutive_auto_reply=num_iterations,
        llm_config=config.llm_config,
        human_input_mode="NEVER"
    )

    ################################################ QUIN AGENT ##############################################

    quin_agent = AssistantAgent(
        name="Quin_Agent",
        system_message=f"""
    You are an Expert SQL query generator and executor agent Agent.
    Your task is to generate SQL query based on the user question and execute it using function calling 'execute_query' and send the output to Quin_Critic_Agent for feedback

    Analyse below database metadata for generating SQL queries:
    {metadata}

    Rules:
    - make sure you donot change column names. use same as metadata
    - Check your step data i.e name, instruction and prompt
    - Use joins for processing multiple tables
    - Give proper input to the function calling
    - Store exact output from the function
    - **Do not use TOP unnecessarily. Understand the user question and instruction properly and use only if needed**
    - Tables are under dbo schema. therefore refer tables as dbo.<table_name> in query
    - If you get feedback from Quin_Critic_Agent do modifications
    - When providing product details make sure you include product name compulsory
    - When there is time frame in the user question form the query accordingly.
    - Give all the columns which are relevant for user question

    Example of your task output:

    {{
        "query": "generated query",
        "query_output": "function output"
    }}

    strictly give JSON output

    Important:
    - Clearly understand the database schema. 
    - do not get confused with column names and tables
    - make neccessary table joins to efficiently run the query
    - **Do not use TOP unless needed**

    """,
        max_consecutive_auto_reply=num_iterations,
        llm_config=config.llm_config,
        human_input_mode="NEVER"
    )
    
    ################################################ DB TOOL AGENT ##############################################

    DB_tool = AssistantAgent(
        name="DB_tool",
        system_message="""
    You are the DB_tool Agent. Your job is to take the query Quin_Agent and use the function to extract the result.

    **Steps**:
    1. **Receive the Query**:
    2. **Execute the execute_query function**
        """,
        max_consecutive_auto_reply=3,
        llm_config=None,
        human_input_mode="NEVER"
    )

    ################################################ EXECUTE QUERY FUNCTION #######################################

    @DB_tool.register_for_execution()
    @quin_agent.register_for_llm(description="You will execute the function and get the result")
    def execute_query(query: str = None):
        try:
            import pandas as pd
            # Execute the query and fetch the result into a DataFrame
            df = pd.read_sql(query, config.engine)
            result_json = df.to_json(orient="records")
            return result_json
        except Exception as e:
            return f"An error occurred while execusting the query:{e}"
        
    ################################################ QUIN CRITIC AGENT ##############################################

    quin_critic_agent = AssistantAgent(
        name="Quin_Critic_Agent",
        system_message=f"""
    You are an Expert SQL query and response analyzer.
    Your task is to check the output of Quin_Agent and give your feedback.

    Analyse below database metadata for analyzing the output:
    {metadata}

    Rules:
    - If the query execution has error analyze that error and give clear feedback where modifications needed
    - If the query is successfully executed check the output and see if the requirement of the step is fullfilled
    - If no feedback is required give "Quin_Critic_Agent: HAPPY WITH THE ANSWER"
    - Thoroughly check if all parts of the user question is present in the query. If only partial question is executed give relevant feedback
    - If after current step there are more routing steps then give step number for next step else give END THE PROCESS
    - Never create new Steps. Stick with the routing_agent steps. If feedback is there give Current step only as Next_step
    - Always give outputs_history in response
    - Check the instruction correctly and query output. Sometimes more or less informations is provided by Quin_Agent
    - Check if all information is given like order details and product details if applicable

    Output format (Strictly follow this JSON format)

    {{
        "User_question": question,
        "Routing_data_current_Step_<current step number>": {{
                "name": "name of the agent",
                "instruction": "Give detailed directions to execute the step".
            }},
        "Current_step_outputs": {{
            "Step_<number>": {{
                "query": "generated query",
                "query_output": function output,
                "outputs_history": [list of all successfull queries outputs]
                "feedback": "Detailed feedback if all parts of the instruction or prompt are executed else Quin_Critic_Agent: HAPPY WITH THE ANSWER",
            }},
        "Routing_data_next_Step_<next step number>": {{
                "name": "name of the agent",
                "instruction": "Give detailed directions to execute the step".
            }},
        }}
        "Next_step": "Step_<current_number> if feedback/Step_<next_number> if router agent has more steps/END THE PROCESS",
        "Next_agent": " name of Step_<current_number> if feedback/name of Step_<next_number> if router agent has more steps/None"
    }}

    Output Instructions:
    - If feedbacks are there and you are re running current step donot create duplicate Step_outputs for same step number
    - Never create duplicate keys in the output dictionary like Process, Step_outputs
    - **When there is feedback no need to give detailed output only key information like feedback and function output is enought**
    - **When feedback is Quin_Critic_Agent: HAPPY WITH THE ANSWER, always give complete output**
    - Never forget Next_step and Next_agent in output
    """,
            max_consecutive_auto_reply=num_iterations,
            llm_config=config.llm_config,
            human_input_mode="NEVER"
        )

    ################################################ ERYL AGENT ##############################################

    eryl_agent = AssistantAgent(
        name="Eryl_Agent",
        system_message=f"""
    You are an Expert Search agent.
    Your task is to follow your step instruction given by routing agent and create text and pass it as argument to Search_tool as argument to execute function 'execute_search'

    Rules to create text:
    - Focus only on your Step instruction
    - Based on your Step instruction form the text for searching
    - Include needed information product details like product name, description based on your instruction 
    - Never analyze your next Step

    Example of your task output (Strictly this output):

    {{
        "text": "created text",
    }}

    Instructions:
    - **Always pass text to Search_tool as argument to execute function 'execute_search'**
    """,
        max_consecutive_auto_reply=num_iterations,
        llm_config=config.llm_config,
        human_input_mode="NEVER",
        description="pass our output to Search_tool as argument to execute function 'execute_search'"
    )

    ################################################ ERYL CRITIC AGENT ##############################################

    eryl_critic_agent = AssistantAgent(
        name="Eryl_Critic_Agent",
        system_message=f"""
    You are an Expert response analyzer.
    Your task is to check the output of Eryl_Agent and give your feedback as well as extract insight from the output based on user question.

    Rules:
    - Ensure Eryl_Agent gives proper input to function calling
    - If any error give feedback to Eryl_Agent
    - If no feedback is required give "Eryl_Critic_Agent: HAPPY WITH THE ANSWER"
    - If after current step there are more routing steps then give step number for next step else give END THE PROCESS
    - Never create new Steps. Stick with the routing_agent steps. If feedback is there give Current step only as Next_step
    - For product name information always give from search index data or database data. Intellitag product name is not the official one
    - Always include identified product_name and product_category in your insight
    
    Output format (Strictly give JSON and follow this format)

    {{
        "User_question": question,
        "Routing_data_current_Step_<current step number>": {{
                "name": "name of the agent",
                "instruction": "Give detailed directions to execute the step".
            }},
        "Current_step_outputs": {{
            "Step_<number>": {{
                "eryl_insight": your insight relevant to user question from the Eryl_Agent response,
                "feedback": "Detailed feedback if error else Eryl_Critic_Agent: HAPPY WITH THE ANSWER",
            }}
        "Routing_data_next_Step_<next step number>": {{
                "name": "name of the agent",
                "instruction": "Give detailed directions to execute the step".
            }},
        }}
        "Next_step": "Step_<current_number> if feedback/Step_<next_number> if router agent has more steps/END THE PROCESS",
        "Next_agent": " name of Step_<current_number> if feedback/name of Step_<next_number> if router agent has more steps/None"
    }}

    ## Important Instructions:
    - If feedbacks are there and you are re running current step donot create duplicate Step_outputs for same step number
    - Never create duplicate keys in the output dictionary like Process, Step_outputs
    - **When there is feedback no need to give detailed output only key information like feedback and function output is enought**
    - **When feedback is Eryl_Critic_Agent: HAPPY WITH THE ANSWER, always give complete output**
    - Never forget Next_step and Next_agent in output
    - Donot let Eryl_Agent change the Step. 
    - **Always ensure Eryl_Agent performed function calling by passing argument**
    - **Always ensure all products information is searched if not give feedback to Eryl_Agent**
    - **If any product information is missing always give feedback to Eryl_Agent**
    - **Double check the Eryl_Agent instruction and make sure all required is answered**
    """,
        max_consecutive_auto_reply=num_iterations,
        llm_config=config.llm_config,
        human_input_mode="NEVER"
    )

    ################################################ SEARCH TOOL ##############################################

    search_tool = AssistantAgent(
        name="Search_tool",
        system_message="""
    You are the Search_tool Agent. Your job is to take the text from Eryl_Agent and use the function 'execute_search' to extract the result.

    **Steps**:
    1. **Receive the text**:
    2. **Execute the execute_search function**
        """,
        max_consecutive_auto_reply=3,
        llm_config=None,
        human_input_mode="NEVER"
    )

    ################################################ EXECUTE SEARCH FUNCTION ##############################################

    import asyncio
    @search_tool.register_for_execution()
    @eryl_agent.register_for_llm(description="You will execute the function and get the result")
    def execute_search(text: str = None):
        try:
            input = text
            print(input)
            print("printing from search")
            def generate_embeddings(text, client, embedding_model_deloyment_name):
                embeddings = client.embeddings.create(input=[text], model=embedding_model_deloyment_name).data[0].embedding
                return embeddings

            text_vector_query = VectorizedQuery(vector=generate_embeddings(input, config.client, config.text_embedding_model), k_nearest_neighbors=3, fields="product_document_embedding")
            text_results = config.search_client.search(
                search_text=None,
                vector_queries=[text_vector_query],
                select=['product_name', 'product_category', 'product_document_content'],
                query_type=QueryType.SEMANTIC,
                semantic_configuration_name='my-semantic-config',
                query_caption=QueryCaptionType.EXTRACTIVE,
                query_answer=QueryAnswerType.EXTRACTIVE,
                top=2
            )

            response = [result for result in text_results]

            return response
        except Exception as e:
            return f"An error occurred while search:{e}"

     
    ################################################ INSIGHT AGENT ##############################################

    insight_agent = AssistantAgent(
        name="Insight_Agent",
        system_message=f"""
    You are an Expert insight generator agent.
    Your task is to analyze the user question and output of entire agentic process and format final output for user.

    Rules:
    - Check your step data i.e name, instruction
    - Check all steps output so far in the chat history
    - Analyze the outputs and give your final insight/answer to user question
    - Give relevant tables if Quin_Agent response is present in your output

    Format of your task output (append your output to Step_outputs (if present) else create):

    {{
        "User_question": question,
        "Final_answer": your final answer/insight by analyzing user question and chat outputs,
        "tables": if any Quin_Agent response in chat history give outputs_history,
        "feedback": Detailed feedback if error else Insight_Agent: HAPPY WITH THE ANSWER
    }}

    Output Instructions:
    - If feedbacks are there and you are re running current step donot create duplicate Step_outputs for same step number
    - Never create duplicate keys in the output dictionary like Process, Step_outputs
    - **When there is feedback no need to give detailed output only key information like feedback and function output is enought**
    - **When feedback is Insight_Agent: HAPPY WITH THE ANSWER, always give complete output**
    """,
        max_consecutive_auto_reply=num_iterations,
        llm_config=config.llm_config,
        human_input_mode="NEVER"
    )

    ################################################ STATE TRANSITION FUNCTION #################################################

    def state_transition(last_speaker, groupchat):
        messages = groupchat.messages
        last_message = messages[-1]["content"]
        last_message = clean_json(last_message)

        print(type(last_message))

        # if last_speaker not in [user_proxy, quin_agent, DB_tool, eryl_agent, search_tool]:
        #     next_step = last_message['Next_step']
        #     if next_step == "END THE PROCESS":
        #         return user_proxy
        #     try:
        #         next_agent = last_message['Process'][next_step]['name']
        #     except:
        #         pass

        try:
            next_step = last_message['Next_step']
            if next_step == "END THE PROCESS":
                if last_speaker is insight_agent:
                    return user_proxy
                else:
                    return insight_agent
        except:
            pass
        try:
            next_agent = last_message['Next_agent']
        except:
            pass

        if last_speaker is user_proxy:
            return routing_agent

        if last_speaker is routing_agent:
            # return user_proxy
            if next_agent == "Quin_Agent":
                return quin_agent
            elif next_agent == "Eryl_Agent":
                return eryl_agent
            elif next_agent == "Insight_Agent":
                return insight_agent
            
        if last_speaker is quin_agent:
            return DB_tool
    
        if last_speaker is DB_tool:
            return quin_critic_agent
        
        if last_speaker is quin_critic_agent:
            if "Quin_Critic_Agent: HAPPY WITH THE ANSWER" in str(last_message):
                if next_agent == "Quin_Agent":
                    return quin_agent
                elif next_agent == "Eryl_Agent":
                    return eryl_agent
                elif next_agent == "Insight_Agent":
                    return insight_agent
                elif next_agent == "END THE PROCESS":
                    return user_proxy
            else:
                return quin_agent
            
        if last_speaker is eryl_agent:
            return search_tool
        
        if last_speaker is search_tool:
            return eryl_critic_agent
        
        if last_speaker is eryl_critic_agent:
            if "Eryl_Critic_Agent: HAPPY WITH THE ANSWER" in str(last_message):
                if next_agent == "Quin_Agent":
                    return quin_agent
                elif next_agent == "Eryl_Agent":
                    return eryl_agent
                elif next_agent == "Insight_Agent":
                    return insight_agent
                elif next_agent == "END THE PROCESS":
                    return user_proxy
            else:
                return eryl_agent
            
        if last_speaker is insight_agent:
            if "Insight_Agent: HAPPY WITH THE ANSWER" in str(last_message):
                user_proxy
            else:
                if next_agent == "Quin_Agent":
                    return quin_agent
                elif next_agent == "Eryl_Agent":
                    return eryl_agent
                elif next_agent == "Insight_Agent":
                    return insight_agent
                elif next_agent == "END THE PROCESS":
                    return user_proxy


    ################################################ CHAT INITIALIZATION #######################################
          
    groupchat = GroupChat(agents=[user_proxy,routing_agent,quin_agent, DB_tool,quin_critic_agent,eryl_agent,search_tool, \
                                  eryl_critic_agent, insight_agent], messages=[], max_round=90, \
                                    speaker_selection_method=state_transition)
    manager = GroupChatManager(groupchat=groupchat, llm_config=config.llm_config)
    # vision_capability = VisionCapability(lmm_config=config.llm_config)
    # vision_capability.add_to_agent(manager)

    chat_history = user_proxy.initiate_chat(
        manager,
        message=airis_agentic_flow_input,
        summary_method="reflection_with_llm"
    )
    response = {} 
    response['chat_history'] = chat_history.chat_history

    for item in chat_history.chat_history:
        if item['name'] =="Insight_Agent":
            final_answer = clean_json(item.get('content', ""))
            response['final_answer'] = final_answer
            
    return response