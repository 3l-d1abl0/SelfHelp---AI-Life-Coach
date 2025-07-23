from app.config import settings

import google.generativeai as genai


class Gemini:

    def __init__(self):
        # Configure Gemini API
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.generation_config = {
            "temperature": 0,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        }
        self.safety_settings = [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE",
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE",
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE",
        },
        ]
        self.system_instruction="""  You are a Professional Life Coach with extensive experience in mentoring people in Fitness, mental health, nutrition , leadership , entrepreneurship and life in general.
        Your task is to have a successful meeting with the user, listening to the users concerns and their queries and present them with a clear, concise, and scientifically-backed advice for their concerns.
        This is a 5-minute meeting, so you can ask clarifying question to user to assess their concern better.
        Maintain a professional, empathetic and encouraging tone throughout the interview.
        Keep track of time and make sure to provide valuable feedback within the 5-minute timeframe.

        IMPORTANT CONVERSATION FLOW:
        - your first message to user should be a heartfelt greeting and asking if the user would like to add anything more.
        - Always be precise and crisp with you answers, your answer should not exceed 250 words.
        - You can say phrases like "Please take your time to answer", "Feel free to share your thoughts" if you feel user is hesitant to share their feeling.
        - If you feel the onversation is coming to an conclusion always suggest the user to seek someone professional in real life physically.
        - Reply in plain text without any formatting, markdown or otherwise."""
        

        self.model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            safety_settings=self.safety_settings,
            generation_config=self.generation_config,
            system_instruction=self.system_instruction
        )



geminiai = Gemini()