def intellitag_agent(config, intellitag_input):
    def analyze_images(image_base64_list):
        # Create a prompt with the list of images
        prompt = """Analyze the provided images meticulously and extract detailed information based on the following categories:
        Extract all text from the image, ensuring no details are missed. Pay special attention to any certifications, health claims, brand names, and nutritional information. 
        Carefully include text from all sections, including the top, center, bottom, and sides of the packaging. 
        Review the image thoroughly to capture any additional small text or logos that 
        might be important, such as certifications or endorsements (e.g., American Heart Association, Gluten Free).
        Provide the extracted text in a clear, organized format
        """

        # Construct messages with the images
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": [{"type": "text", "text": f"{prompt}"}]
                + [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{img}",
                            "detail": "high",
                        },
                    }
                    for img in image_base64_list
                ],
            },
        ]

        response = config.client.chat.completions.create(
            model="gpt-4o-08-06",
            messages=messages,
            max_tokens=4000,
            n=1,
            temperature=0,
            seed=43,
        )

        return response.choices[0].message.content


    # Function to structure and correct combined information
    def structure_combined_info(combined_info):
        prompt = f"""Given the extracted information from multiple images:

        {combined_info}

        Please structure the information neatly under the following headings:
        1. Product Information
    Attributes:
    - Product Name
    - Product Type (e.g., Snack, Beverage, Cereal)
    - Brand Name
    - Tagline
    - Key Features (e.g., made with real banannas, Kids approved, grab and go, nutritional drink,Toasted Whole Grains Oats,No Extra Added sugar)
    - Flavor (e.g., Fruity, Citrus, Spicy, Savory, Sweet, Nutty, Herbal, Exotic,Tomato and Basil)
    - Weight/Volume
    - Certifications (e.g., Non-GMO Project Verified, Vegan, USDA Organic, Non-GMO Project Verified, American Heart Association Certified)
    - Packaging Type (e.g., Box, Bottle, Bag)
    - Batch Number
    - Shelf Life (e.g., Best before 6 months, Consume within 7 days of opening, Best if used within 3 days after opening, Use within 1 month after opening)
    - Storage Instructions
    - Additional Information -
    - Barcode/UPC Code
    - Manufactured For (e.g., Manufactured For Munk Pack, Inc , Manufactured For Nature's Path Foods, Produced exclusively for
    - Product Message

    2. Nutritional Information
    Attributes:
    - Serving Size
    - Calories per Serving
    - Total Fat (g)
    - Saturated Fat (g)
    - Trans Fat (g)
    - Cholesterol (mg)
    - Sodium (mg)
    - Total Carbohydrate (g)
    - Dietary Fiber (g)
    - Sugars (g)
    - Protein (g)
    - Vitamins and Minerals (e.g., Vitamin A, Vitamin C, Calcium, Iron)
    - Nutrition Guidance
    3. Ingredients
    Attributes:
    - Ingredient List (in order of quantity)
    - Allergen Information (e.g., Contains Nuts, Dairy)
    - Preservatives (if any)
    - Artificial Flavors/Colors (if any)
    - Organic/Non-Organic Labels
    - GMO Status (e.g., Non-GMO, Non GMO Verified, May contain genetically modified ingredients, GMO free)
    4. Dietary Information
    Attributes:
    - Gluten Status
    - Vegetarian Status
    - Sugar Status
    - Lactose Status
    - Glycemic Impact (e.g., Low Glycemic Index, Glucose Controlled, High Glucose Response)
    5. **Implicit Product Profile**
        Based on the information provided, infer the following attributes:
        - Occasion (e.g., Holiday, Party, Daily Use, Easter, Super Bowl, Thanksgiving, Oktoberfest)
        - Season (e.g., Summer, Winter, All Seasons)
        - Consumer Type (e.g., Adults, Children, Athletes, Health-Conscious)
        - Meal Type (e.g., Breakfast, Lunch, Dinner, Snacks)
        - Consumption Time (e.g., Pre-Workout, Post-Workout, Anytime)
        - Dietary Needs (e.g., Low-Sodium, High-Protein, Low-Carb)
        - Health Goals (e.g., Weight Loss, Muscle Gain, Energy Boost)
        - Convenience Level (e.g., Ready-to-Eat, Requires Minimal Preparation)
        - Packaging Size (e.g., Single Serving, Family Pack)
        Analyze the provided information to infer the relevant attributes for Dietary Preferences.

    6.  Additional Information
        Additionally, if there is any other information or points that have not been defined in the above attributes, please create a new attribute for it and place it under the category that suits it best. Ensure that no text or information is missed.

    For any heading information is not available then donot give it. The answer should be clear and to the point, ensuring everything is captured accurately. Ensure there is no Duplication, and the data is well-organized. Provide the output in a clear and structured format.END  """

        response = config.client.chat.completions.create(
            model="gpt-4o-08-06",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=4000,
            n=1,
            temperature=0,
            seed=43,
        )

        return response.choices[0].message.content
    
    combined_info = analyze_images(intellitag_input)
    structured_output = structure_combined_info(combined_info)

    return structured_output