from azure.ai.contentsafety.models import AnalyzeTextOptions
import pandas as pd

def execute_content_analysis(email_body, config):
    request = AnalyzeTextOptions(text=email_body)
    response = config.safety_client.analyze_text(request)
    response_db = pd.DataFrame(response.categories_analysis)
    if any(response_db['severity']>0):
        check=True
    else:
        check=False
    return check, response_db