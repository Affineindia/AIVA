import streamlit as st
# Set page layout
import ast
from functions.get_final_answer_new import get_final_answer
from functions.utils import clean_json
import time
from setting.configurations import Config
from PIL import Image
import base64
from io import BytesIO
import json

config = Config()

# st.set_page_config(page_title="AIRIS - Affine Information Retrieval & Image Synthesis", layout="wide")
st.set_page_config(page_title="AIVA - Affine Intelligent Virtual Assistant", layout="wide")

# Custom Header
st.markdown("""
    <div style='text-align: center;'>
        <h2 style='font-size: 40px; font-family: Courier New, monospace;'>
            <img src="https://acis.affineanalytics.co.in/assets/images/logo_small.png" width="70" height="60">
            <span style='background: linear-gradient(45deg, #ed4965, #c05aaf); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
                AIVA - Affine Intelligent Virtual Assistant
            </span>
        </h2>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# User Input
default_email_body = "Which products will be delivered this month and what are their return policy?"
default_domain_keywords = "ratings, food products, image-related, recommendation, analyse, image analysis, Orders, inventory, invoices, distributors, payments, products, purchases, product features, Transactions, shipping, delivery, supply chain, inventory, policies, support, refund, pricing, anything related to business"
default_replier_details = "replier name : AIVA (Affine Intelligent Virtual Assistant), Position : Your Intelligent Affine Support Agent"
default_email_id = ""
default_support_id = "akasapu.hemanthika@affine.ai"
email_body = st.text_input("📩 Enter your email text:", placeholder="Ask about orders, refunds, ...")
email_id = st.text_input("📧 Enter your email id. If not registered contact akasapu.hemanthika@affine.ai", placeholder="Enter your registered email id", value=default_email_id)
uploaded_files = st.file_uploader(
    "Upload images", type=["png", "jpg", "jpeg"], accept_multiple_files=True
)

def delete_blob(image_name):
    blob_client = config.blob_service_client.get_blob_client(container=config.BLOB_UPLOAD_CONTAINER_NAME, blob=image_name)
    blob_client.delete_blob()

def encode_image_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")  # Save the image as PNG
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str

def upload_to_blob(image_data, count):
    image = Image.open(image_data)
    byte_stream = BytesIO()
    image.save(byte_stream, format=image.format)
    byte_stream.seek(0)
    blob_name = f"upload_image_{count}.{image.format}"
    # blob_name = image_data.name
    blob_client = config.blob_service_client.get_blob_client(container=config.BLOB_UPLOAD_CONTAINER_NAME, blob=blob_name)
    blob_client.upload_blob(byte_stream, overwrite=True)
    return blob_name

if st.button("🚀 Get Answer") and email_body:
    with st.spinner("🔍 Fetching insights..."):
        start_time = time.time()
        image_base64_list = []
        for uploaded_file in uploaded_files:
            image = Image.open(uploaded_file)
            st.image(
                image, caption="Uploaded Image", width=500
            )  # Set the width to 300 pixels

            image_base64 = encode_image_to_base64(image)
            image_base64_list.append(
                image_base64
            )

        inputs = {
                "email_body": email_body,
                "email_id": email_id,
                "attachments": image_base64_list,
                "domain": default_domain_keywords,
                "replier_details": default_replier_details,
                "support_email": default_support_id
            }
        final_output = get_final_answer(inputs)

        # for image in attachments:
        #     delete_blob(image)

        # Layout Columns
        col1, col2 = st.columns([3, 2])

        # Final Answer Section
        with col1:
            # Display email
            with st.expander("📩 Final Mail", expanded=False):
                mail = final_output.get('final_email').get("body")
                sub = final_output.get('final_email').get("subject")
                st.markdown(sub, unsafe_allow_html=True)
                st.markdown(mail, unsafe_allow_html=True)

        # Thought Process as Expandable Section with AI Icon
        with col2:
            st.markdown(f"**🔧 Total time:** {int(time.time()-start_time)} sec")
        