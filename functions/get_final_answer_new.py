from functions.execute_content_analysis import execute_content_analysis
from functions.execute_content_analysis_image import execute_content_analysis_image
from functions.call_airis_agentic_flow_new import call_airis_agentic_flow
from functions.utils import clean_json
from functions.content_email_agent import content_email_agent
from functions.question_extraction_agent import question_extraction_agent
from functions.info_email_agent import info_email_agent
from functions.out_of_domain_email_agent import out_of_domain_email_agent
from functions.query_mail_agent import query_email_agent
from functions.user_email_agent import user_email_agent
from functions.intellitag_agent import intellitag_agent
from functions.user_check import user_check
from setting.configurations import Config

def get_final_answer(inputs):

    ############################### RESPONSE ############################################

    response = {
        "final_email": "",
    }

    ############################### CONFIG ##############################################

    config = Config()

    ############################################ USER CHECK #########################################################

    user_check_flag = user_check(config, inputs['email_id'])

    if user_check_flag==False:
        user_email_inputs = {
            "User name": inputs['email_id'],
            "Replier details": inputs['replier_details'],
            "Support email": inputs['support_email']
        }
        user_email_agent_response = user_email_agent(config, user_email_inputs)
        user_email_agent_response = clean_json(user_email_agent_response)

        response['final_email'] = user_email_agent_response

        print('\n-------- USER MAIL ---------------')
        print(user_email_agent_response)

        return response

    ################################ CHECK CONTENT ########################################

    content_check, content_response = execute_content_analysis(inputs['email_body'], config)
    print('\n-------- CONTENT CHECK RESPONSE ---------------')
    print(content_response)

    if content_check:
        content_input = {
            'user_name': inputs['email_id'],
            'replier_details': inputs['replier_details'],
            'data_source': 'query'
        }
        content_email_response = content_email_agent(config, content_input)
        content_email_response = clean_json(content_email_response)

        response['content_response'] = content_response
        response['final_email'] = content_email_response

        print('\n-------- CONTENT EMAIL ---------------')
        print(content_email_response)
        
        return response
    
    ################################ CHECK CONTENT IMAGE ########################################

    print('\n-------- CONTENT IMAGE CHECK RESPONSE ---------------')
    for image in inputs['attachments']:
        content_check, content_response = execute_content_analysis_image(image, config)
        print(content_response)

        if content_check:
            content_input = {
                'user_name': inputs['email_id'],
                'replier_details': inputs['replier_details'],
                'data_source': 'attachments'
            }
            content_email_response = content_email_agent(config, content_input)
            content_email_response = clean_json(content_email_response)

            response['content_response'] = content_response
            response['final_email'] = content_email_response

            print('\n-------- CONTENT EMAIL ---------------')
            print(content_email_response)
            
            return response
    
    ############################################ EXTRACT QUESTION ################################################

    question_extraction_input = {
        "Email_content": inputs['email_body'],
        "Domain": inputs['domain']
    }
    print('\n-------- EXTRACT QUESTION INPUT ---------------')
    print(question_extraction_input)

    question_extraction_response = question_extraction_agent(config, question_extraction_input)
    question_extraction_response = clean_json(question_extraction_response)

    response['extract_question'] = question_extraction_response

    print('\n-------- EXTRACT QUESTION RESPONSE ---------------')
    print(question_extraction_response)

    ############################################ UNIFIED VIEW ######################################################

    if question_extraction_response['tag']=='question':
        
        ############################################ INTELITAG ######################################################

        if len(inputs['attachments'])>0:
            intellitag_response = intellitag_agent(config, inputs['attachments'])
        else:
            intellitag_response = []

        unified_view_input = {
            "question": question_extraction_response['question'],
            "email_id": inputs['email_id'],
            "attachments": intellitag_response
        }
        unified_response = call_airis_agentic_flow(f"""{unified_view_input}""")

        ############################################ QUERY EMAIL #########################################################
        
        final_answer = unified_response.get("final_answer")
        query_inputs = {
            "User name": inputs['email_id'],
            "Replier details": inputs['replier_details']
        }
        query_inputs['User answer to format'] = final_answer
        query_email_response = query_email_agent(config, query_inputs)
        query_email_response = clean_json(query_email_response)

        print('\n-------- QUERY EMAIL ---------------')
        print(query_email_response)

        response['unified_response'] = unified_response
        response['final_email'] = query_email_response

        return response

    ############################################ INFO EMAIL #########################################################

    elif question_extraction_response['tag']=='info':
        info_inputs = {
            "User name": inputs['email_id'],
            "answer to be formatted": question_extraction_response['question'],
            "Replier details": inputs['replier_details']
        }
        info_agent_response = info_email_agent(config, info_inputs)
        info_agent_response = clean_json(info_agent_response)

        response['final_email'] = info_agent_response

        print('\n-------- INFO MAIL ---------------')
        print(info_agent_response)

        return response

    ############################################ OUT OF DOMAIN ######################################################

    else:
        out_of_domain_inputs = {
            "User name": inputs['email_id'],
            "Domain": inputs['domain'],
            "Replier details": inputs['replier_details']
        }
        out_of_domain_agent_response = out_of_domain_email_agent(config, out_of_domain_inputs)
        out_of_domain_agent_response = clean_json(out_of_domain_agent_response)

        response['final_email'] = out_of_domain_agent_response

        print('\n-------- OUT OF DOMAIN MAIL ---------------')
        print(out_of_domain_agent_response)

        return response

    
    