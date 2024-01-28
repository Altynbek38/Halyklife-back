from typing import List
from google.cloud import storage
import PyPDF2
import os
import openai
import requests
import httpx
from fastapi import HTTPException
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain.callbacks.base import BaseCallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain import PromptTemplate
from dotenv import load_dotenv
load_dotenv()

openai_key = os.getenv("OPENAI_API_KEY")
openai.api_key = openai_key

template = """
Answer with only one word: "True" or "False"
Text: {question}
"""

class OpenAI:
    def __init__(self):
        self.chat = ChatOpenAI(temperature=0.4, openai_api_key=openai_key, model_name="gpt-3.5-turbo-0613", max_tokens= 1900,streaming=True, callback_manager=BaseCallbackManager([StreamingStdOutCallbackHandler()]))
        self.embedding = OpenAIEmbeddings()
        self.prompt = PromptTemplate(
            input_variables=["question"],
            template=template,
        )
        self.BarcodeTypes = "Code128,Code39,Interleaved2of5,EAN13"
        self.Pages = ""
        self.certificate_checker = [
            SystemMessage(
            content="""
                        Answer with only one word: "True" or "False"
                        Does this diagnosis belong to one of the following groups?

                        Explosion, electric current, lightning strike
                        Acute food or chemical poisoning
                        Burns and frostbite
                        An attack by intruders or animals
                        An accident, a train, ship or plane crash
                        Consequences of erroneous medical manipulations
                    """
            )
        ]
        self.messages = [
            SystemMessage(
            content=f"""You are the Insurance Assistant. You must answer in the first person for each query and answer only the question. Always retrieve data from the database.

            You can answer different questions such as "How are you?", "Hi!" or "What do you think?".

            Never forget that you are the Insurance Assistant, and answer every question about insurance in the first person.

            If the question does not relate to insurance or related topics, I may not know what the question is about. Please clarify if you want to know something specific about insurance or related matters.
                    """
            )
        ]

    async def readBarcodes(self, uploadedFileUrl, iin):
        """Get Barcode Information using PDF.co Web API"""
        print("Start readBarCodes")
        # Prepare requests params as JSON
        # See documentation: https://apidocs.pdf.co
        parameters = {}
        parameters["types"] = self.BarcodeTypes
        parameters["pages"] = self.Pages
        parameters["url"] = uploadedFileUrl

        # Prepare URL for 'Barcode Reader' API request
        url = "{}/barcode/read/from/url".format(os.getenv("BASE_URL"))
        print("pre response")
        # Execute request and get response as JSON
        response = requests.post(url, data=parameters, headers={ "x-api-key": os.getenv("API_KEY") })
        if (response.status_code == 200):
            json = response.json()

            if json["error"] == False:
                # Display information
                for barcode in json["barcodes"]:
                    guid = barcode["Value"]["GUID"]

                    api_url = "https://fastapi-5lcu.onrender.com/damumed/check_certificate"

                    data = {"IIN": iin, "GUID": guid}

                    async with httpx.AsyncClient() as client:
                        response = await client.post(api_url, json=data)

                    if response.is_error:
                        raise HTTPException(status_code=response.status_code, detail="Error from external API")

                    if response.status_code == 404:
                            raise HTTPException(
                            status_code=404,
                            detail="GUID not found",
                            )
            else:
                # Show service reported error
                return json["message"]
        else:
            return f"Request error: {response.status_code} {response.reason}"
        print("post response")
        return self.pdf_reader(uploadedFileUrl)

    def pdf_reader(self, uploadedFileUrl):
        # Assuming `uploadedFileUrl` is the URL of the PDF file in Google Cloud Storage
        print("start pdf reader")
        # Initialize Google Cloud Storage client
        storage_client = storage.Client()
        
        # Get the bucket and blob from the URL
        bucket_name, blob_name = self.parse_bucket_and_blob(uploadedFileUrl)
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        # Download the PDF content
        pdf_content = blob.download_as_text()

        # Use PyPDF2 to extract text from the PDF
        pdf_text = ""
        with open(pdf_content, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfFileReader(pdf_file)
            for page_number in range(pdf_reader.numPages):
                page = pdf_reader.getPage(page_number)
                pdf_text += page.extractText()

        final_prompt = self.prompt.format(question=pdf_text)
        print("end pdf reader")
        self.certificate_checker.append(HumanMessage(content=final_prompt))
        ai_response = self.chat(self.certificate_checker).content
        return ai_response
    
    def parse_bucket_and_blob(self, url):
        print("parse")
        parts = url.split("//")[1].split("/")
        return parts[0], "/".join(parts[1:])

    def get_bot_response(self,user_query):

        self.messages.append(HumanMessage(content=user_query))
        ai_response = self.chat(self.messages).content
        self.messages.pop()
        self.messages.append(HumanMessage(content=user_query))
        self.messages.append(AIMessage(content=ai_response))
        return ai_response