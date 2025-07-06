from google import genai
from google.genai import types
from pydantic import BaseModel
import pathlib

class ExtractedBill(BaseModel):
    invoice_number: str
    total_due_amount: float
    due_date: str
    invoice_date: str

class LLMClient:
    """
    A client for interacting with OpenRouter's LLM
    """
    
    def __init__(self, api_key: str, base_url: str = "https://openrouter.ai/api/v1"):
        self.client = genai.Client()

    def extract_bill_info(self, pdf_path: str) -> dict:
        """
        Extracts bill information from the email content using OpenRouter's LLM.
        
        Args:
            email_content (str): The content of the email containing bill information.
            
        Returns:
            dict: A dictionary containing extracted bill information.
        """
        filepath = pathlib.Path(pdf_path)
        prompt = "You are a helpful assistant that extracts bill information from PDFs."

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Part.from_bytes(
                    data=filepath.read_bytes(),
                    mime_type='application/pdf',
                ),
                prompt
            ],
            config={
                "response_mime_type": "application/json",
                "response_schema": ExtractedBill,
            })
        
        return response.parsed