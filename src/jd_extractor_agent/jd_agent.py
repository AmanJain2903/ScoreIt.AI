# EXAMPLE USAGE

# load_dotenv() 
# API_NAME = config.API_NAME
# if not os.getenv(API_NAME):
#     raise ValueError(f"{API_NAME} environment variable not set")
# JDAgent = JobDescriptionAgent(
#     apiKey=os.getenv(API_NAME),
#     modelName=config.MODEL_NAME,
#     systemPrompt=None, # Default system prompt will be used
#     useDefaultModelIfNone=True,
#     useDefaultSystemPromptIfNone=True
# )
# jobDescription = "We are looking for a software engineer with experience in Python and machine learning. The ideal candidate should have a strong understanding of algorithms and data structures, as well as experience with cloud computing platforms. Responsibilities include developing and maintaining software applications, collaborating with cross-functional teams, and participating in code reviews."
# JDAgent.setUserPrompt(jobDescription)
# output = JDAgent.getJsonOutput()
# JDAgent.deleteAgent()
# print(output)

import os
import gc
import json
from openai import OpenAI
from dotenv import load_dotenv
from src.utils import security
from src.jd_extractor_agent import config
import importlib.resources
import yaml
# Load configuration
config = config.Config()
    
class JobDescriptionAgent:
    def __init__(self, apiKey, modelName, systemPrompt, useDefaultModelIfNone=True, useDefaultSystemPromptIfNone=True):
        if useDefaultModelIfNone and modelName is None:
            modelName = config.MODEL_NAME
        if useDefaultSystemPromptIfNone and systemPrompt is None:
            systemPromptPath = config.DEFAULT_SYSTEM_PROMPT_PATH
            try:
                with importlib.resources.open_text('src.jd_extractor_agent.data', systemPromptPath) as file:
                    systemPrompt = file.read()
            except Exception as e:
                    raise RuntimeError(f"Failed to load system prompt '{systemPromptPath}': {e}")
        if not systemPrompt:
            raise ValueError(f"System prompt not found.")
        if not apiKey:
            raise ValueError("API key not found.")
        if not modelName:
            raise ValueError("Model name not found.")
        self.SCM = security.SecureKeyManager()
        self.SCM.store_key(apiKey)
        self.modelName = modelName
        self.systemPrompt = systemPrompt
        self.response = None
        self.jsonOutput = None
        self.userPrompt = None
        self.client = None
    
    def getClient(self):
        if not self.client:
            try:
                decryptedKey = self.SCM.get_key()
                self.client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=decryptedKey,
                )
                decryptedKey = 'x' * len(decryptedKey)  # Clear the decrypted key from memory
                del decryptedKey
                gc.collect()  # Force garbage collection
            except Exception as e:
                raise ValueError(f"Failed to initialize client: {e}")

    def deleteClient(self):
        if not self.client:
            raise ValueError("Client not initialized.")
        self.client.close()
        self.client = None

    def getAgentInfo(self):
        return {
            "modelName": self.modelName,
            "systemPrompt": self.systemPrompt,
            "userPrompt": self.userPrompt,
            "response": self.response,
            "jsonOutput": self.jsonOutput,
            "client": self.client,
        }
    
    
    def getAgentStatus(self):
        if not self.client:
            return "Client not initialized."
        return "Agent is good to go with."
    
    def setUserPrompt(self, userPrompt):
        if not userPrompt:
            raise ValueError("User prompt cannot be empty.")
        userPrompt = security.sanitizeInput(userPrompt, 10000)
        self.userPrompt = userPrompt
    
    def parseRespone(self):
        if not self.response:
            raise ValueError("No response found.")
        try:
            startIndex = self.response.index('{')
            endIndex = self.response.rindex('}') + 1
            jsonString = self.response[startIndex:endIndex]
            jsonOutput = json.loads(jsonString)
        except (ValueError, json.JSONDecodeError) as e:
            raise ValueError(f"Failed to parse JSON response: {e}")
        if not isinstance(jsonOutput, dict):
            raise ValueError("Parsed JSON is not a dictionary.")
        return jsonOutput
    
    def getResponse(self):
        if not self.modelName:
            raise ValueError("Model name not set.")
        if not self.systemPrompt:
            raise ValueError("System prompt not set.")
        if not self.userPrompt:
            raise ValueError("User prompt not set.")
        
        self.getClient()
        if not self.client:
            raise ValueError("Client not initialized.")
        try:
            completion = self.client.chat.completions.create(
                model=self.modelName,
                messages=[
                    {"role": "system", "content": self.systemPrompt},
                    {"role": "user", "content": self.userPrompt}
                ],
                response_format={'type': 'json_object', 'format': 'json'},
            )
        except Exception as e:
            raise ValueError(f"Failed to get response: {e}")
        self.deleteClient()
        
        if not completion or not completion.choices:
            try:
                if completion and hasattr(completion, 'error'):
                    error = completion.error['message']
                    raise ValueError(f"Error in response: {error}")
            except Exception as e:
                raise ValueError(f"Failed to get response: {e}")
        if not completion.choices[0].message or not completion.choices[0].message.content:
            raise ValueError("No content in response.")
        
        self.response = completion.choices[0].message.content
        self.jsonOutput = self.parseRespone()

    def getJsonOutput(self):
        if not self.jsonOutput:
            try :
                self.getResponse()
            except ValueError:
                raise ValueError("No JSON output found.")
        return self.jsonOutput

    def getResponseText(self):
        if not self.response:
            try:
                self.getResponse()
            except ValueError:
                raise ValueError("No response found.")
        return self.response

    def getUserPrompt(self):
        if not self.userPrompt:
            raise ValueError("No user prompt found.")
        return self.userPrompt

    def getModelName(self):
        if not self.modelName:
            raise ValueError("No model name found.")
        return self.modelName

    def getSystemPrompt(self):
        if not self.systemPrompt:
            raise ValueError("No system prompt found.")
        return self.systemPrompt

    def resetAgent(self):
        if self.client:
            self.client.close()
        self.client = None
        self.response = None
        self.jsonOutput = None
        self.userPrompt = None

    def deleteAgent(self):
        self.resetAgent()
        self.modelName = None
        self.systemPrompt = None

        if hasattr(self, 'SCM'):
            self.SCM._key = b'0' * 32  # Clear the key from memory
            self.SCM._encryptedKey = b'0' * len(self.SCM._encryptedKey)  # Clear the encrypted key from memory
            del self.SCM
            self.SCM = None
        gc.collect()
    
