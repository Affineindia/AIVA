from azure.ai.contentsafety.models import AnalyzeImageOptions, ImageData
import pandas as pd

def execute_content_analysis_image(image_data, config):
    request = AnalyzeImageOptions(image=ImageData(content=image_data))
    response = config.safety_client.analyze_image(request)
    response_db = pd.DataFrame(response.categories_analysis)
    if any(response_db['severity']>0):
        check=True
    else:
        check=False
    return check, response_db