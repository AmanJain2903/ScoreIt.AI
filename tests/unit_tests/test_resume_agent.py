import pytest
from unittest.mock import patch, MagicMock
from src.resume_extractor_agent.resume_agent import ResumeAgent

pytestmark = pytest.mark.unit

@pytest.fixture
def resume_agent(apiKey="fake-api-key",
        modelName="test-model",
        systemPrompt="You are a helpful assistant.",
        useDefaultModelIfNone=False,
        useDefaultSystemPromptIfNone=False):
    return ResumeAgent(
        apiKey=apiKey,
        modelName=modelName,
        systemPrompt=systemPrompt,
        useDefaultModelIfNone=useDefaultModelIfNone,
        useDefaultSystemPromptIfNone=useDefaultSystemPromptIfNone
    )

def test_initialization_success(resume_agent):
    assert resume_agent.modelName == "test-model"
    assert resume_agent.systemPrompt == "You are a helpful assistant."
    assert resume_agent.response is None
    assert resume_agent.client is None
    assert resume_agent.userPrompt is None
    assert resume_agent.jsonOutput is None

def test_initialization_failure_no_api_key():
    with pytest.raises(ValueError, match="API key not found."):
        ResumeAgent(
            apiKey=None,
            modelName="test-model",
            systemPrompt="You are a helpful assistant."
        )

def test_initialization_failure_no_model_name():
    with pytest.raises(ValueError, match="Model name not found."):
        ResumeAgent(
            apiKey="fake-api-key",
            modelName=None,
            systemPrompt="You are a helpful assistant.",
            useDefaultModelIfNone=False,
            useDefaultSystemPromptIfNone=False
        )

def test_initialization_failure_no_system_prompt():
    with pytest.raises(ValueError, match="System prompt not found."):
        ResumeAgent(
            apiKey="fake-api-key",
            modelName="test-model",
            systemPrompt=None,
            useDefaultModelIfNone=False,
            useDefaultSystemPromptIfNone=False
        )

@patch('src.resume_extractor_agent.resume_agent.OpenAI')
def test_getClient_success(mock_openai, resume_agent):
    mock_client = MagicMock()
    mock_openai.return_value = mock_client

    resume_agent.getClient()

    assert resume_agent.client is not None
    assert isinstance(resume_agent.client, MagicMock)

@patch('src.resume_extractor_agent.resume_agent.OpenAI')
def test_getClient_failure(mock_openai, resume_agent):
    mock_openai.side_effect = Exception("Client initialization failed.")

    with pytest.raises(ValueError, match="Failed to initialize client: Client initialization failed."):
        resume_agent.getClient()
        
def test_deleteClient_success(resume_agent):
    class DummyClient:
        def close(self):
            pass

    resume_agent.client = DummyClient()
    resume_agent.deleteClient()
    assert resume_agent.client is None

def test_deleteClient_not_initialized(resume_agent):
    with pytest.raises(ValueError, match="Client not initialized."):
        resume_agent.deleteClient()

def test_getAgentInfo(resume_agent):
    info = resume_agent.getAgentInfo()
    assert isinstance(info, dict)
    assert "modelName" in info
    assert "systemPrompt" in info
    assert "userPrompt" in info
    assert "response" in info
    assert "jsonOutput" in info
    assert "client" in info

@patch('src.resume_extractor_agent.resume_agent.OpenAI')
def test_getAgentStatus_initialized(mock_openai, resume_agent):
    mock_client = MagicMock()
    mock_openai.return_value = mock_client

    resume_agent.getClient()
    status = resume_agent.getAgentStatus()
    assert status == "Agent is good to go with."

def test_getAgentStatus_not_initialized(resume_agent):
    status = resume_agent.getAgentStatus()
    assert status == "Client not initialized."

def test_setUserPrompt_success(resume_agent):
    resume_agent.setUserPrompt("Test prompt")
    assert resume_agent.userPrompt == "test prompt"

def test_setUserPrompt_empty(resume_agent):
    with pytest.raises(ValueError, match="User prompt cannot be empty."):
        resume_agent.setUserPrompt("")

def test_parseResponse_no_response(resume_agent):
    resume_agent.response = None
    with pytest.raises(ValueError, match="No response found."):
        resume_agent.parseRespone()

def test_parseResponse_invalid_json(resume_agent):
    resume_agent.response = "Invalid JSON response"
    with pytest.raises(ValueError, match="Failed to parse JSON response: substring not found"):
        resume_agent.parseRespone()

def test_parseResponse_success(resume_agent):
    resume_agent.response = '{"key": "value"}'
    parsed_json = resume_agent.parseRespone()
    assert isinstance(parsed_json, dict)
    assert parsed_json == {"key": "value"}

def test_getResponse_success(resume_agent):
    resume_agent.userPrompt = "Test prompt"
    resume_agent.response = '{"key": "value"}'
    resume_agent.jsonOutput = {"key": "value"}
    resume_agent.client = MagicMock()
    resume_agent.client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content='{"key": "value"}'))]
    )
    resume_agent.getResponse()
    assert resume_agent.response == '{"key": "value"}'
    assert resume_agent.jsonOutput == {"key": "value"}

def test_getResponse_no_client(resume_agent):
    resume_agent.client = None
    resume_agent.userPrompt = "Test prompt"
    resume_agent.getClient = MagicMock()
    with pytest.raises(ValueError, match="Client not initialized."):
        resume_agent.getResponse()

def test_getResponse_no_model_name(resume_agent):
    resume_agent.modelName = None
    resume_agent.userPrompt = "Test prompt"
    with pytest.raises(ValueError, match="Model name not set."):
        resume_agent.getResponse()

def test_getResponse_no_system_prompt(resume_agent):
    resume_agent.systemPrompt = None
    resume_agent.userPrompt = "Test prompt"
    with pytest.raises(ValueError, match="System prompt not set."):
        resume_agent.getResponse()

def test_getResponse_no_user_prompt(resume_agent):
    resume_agent.userPrompt = None
    with pytest.raises(ValueError, match="User prompt not set."):
        resume_agent.getResponse()

def test_getResonse_error_in_response(resume_agent):
    resume_agent.userPrompt = "Test prompt"
    resume_agent.client = MagicMock()
    resume_agent.client.chat.completions.create.return_value = MagicMock(
        choices=[],
        error={"message": "Error in response"}
    )
    with pytest.raises(ValueError, match="Error in response: Error in response"):
        resume_agent.getResponse()

def test_getResponse_error(resume_agent):
    resume_agent.userPrompt = "Test prompt"
    resume_agent.client = MagicMock()
    resume_agent.client.chat.completions.create.return_value = MagicMock(
        choices=[],
    )
    resume_agent.client.chat.completions.create.side_effect = Exception("API error")
    with pytest.raises(ValueError, match="Failed to get response: API error"):
        resume_agent.getResponse()

def test_getResponse_no_choices(resume_agent):
    resume_agent.userPrompt = "Test prompt"
    resume_agent.client = MagicMock()
    resume_agent.client.chat.completions.create.return_value = MagicMock(choices=[MagicMock(message=MagicMock(content=None))])
    with pytest.raises(ValueError, match="No content in response."):
        resume_agent.getResponse()

def test_getResponse_no_content(resume_agent):
    resume_agent.userPrompt = "Test prompt"
    resume_agent.client = MagicMock()
    resume_agent.client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content=None))]
    )
    with pytest.raises(ValueError, match="No content in response."):
        resume_agent.getResponse()

def test_getJsonOutput_success(resume_agent):
    resume_agent.userPrompt = "Test prompt"
    resume_agent.response = '{"key": "value"}'
    resume_agent.jsonOutput = {"key": "value"}
    resume_agent.client = MagicMock()
    resume_agent.client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content='{"key": "value"}'))]
    )
    resume_agent.getJsonOutput()
    assert resume_agent.jsonOutput == {"key": "value"}

def test_getJsonOutput_try_get_response(resume_agent):
    resume_agent.userPrompt = "Test prompt"
    resume_agent.response = None
    resume_agent.jsonOutput = None
    resume_agent.client = MagicMock()
    resume_agent.client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content='{"key": "value"}'))]
    )
    resume_agent.getJsonOutput()
    assert resume_agent.jsonOutput == {"key": "value"}

def test_getJsonOutput_no_response(resume_agent):
    resume_agent.userPrompt = "Test prompt"
    resume_agent.response = None
    resume_agent.jsonOutput = None
    resume_agent.client = MagicMock()
    resume_agent.client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content=None))]
    )
    with pytest.raises(ValueError, match="No JSON output found."):
        resume_agent.getJsonOutput()

def test_getResponseText_success(resume_agent):
    resume_agent.userPrompt = "Test prompt"
    resume_agent.response = '{"key": "value"}'
    resume_agent.jsonOutput = {"key": "value"}
    resume_agent.client = MagicMock()
    resume_agent.client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content='{"key": "value"}'))]
    )
    resume_agent.getResponseText()
    assert resume_agent.response == '{"key": "value"}'

def test_getResponseText_try_get_response(resume_agent):
    resume_agent.userPrompt = "Test prompt"
    resume_agent.response = None
    resume_agent.jsonOutput = None
    resume_agent.client = MagicMock()
    resume_agent.client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content='{"key": "value"}'))]
    )
    resume_agent.getResponseText()
    assert resume_agent.response == '{"key": "value"}'

def test_getResponseText_no_response(resume_agent):
    resume_agent.userPrompt = "Test prompt"
    resume_agent.response = None
    resume_agent.jsonOutput = None
    resume_agent.client = MagicMock()
    resume_agent.client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content=None))]
    )
    with pytest.raises(ValueError, match="No response found."):
        resume_agent.getResponseText()

def test_getUserPrompt_success(resume_agent):
    resume_agent.userPrompt = "Test prompt"
    assert resume_agent.getUserPrompt() == "Test prompt"

def test_getUserPrompt_no_user_prompt(resume_agent):
    resume_agent.userPrompt = None
    with pytest.raises(ValueError, match="No user prompt found."):
        resume_agent.getUserPrompt()

def test_getUserPrompt_empty(resume_agent):
    resume_agent.userPrompt = ""
    with pytest.raises(ValueError, match="No user prompt found."):
        resume_agent.getUserPrompt()

def test_getModelName_success(resume_agent):
    resume_agent.modelName = "test-model"
    assert resume_agent.getModelName() == "test-model"

def test_getModelName_no_model_name(resume_agent):
    resume_agent.modelName = None
    with pytest.raises(ValueError, match="No model name found."):
        resume_agent.getModelName()

def test_getModelName_empty(resume_agent):
    resume_agent.modelName = ""
    with pytest.raises(ValueError, match="No model name found."):
        resume_agent.getModelName()

def test_getSystemPrompt_success(resume_agent):
    resume_agent.systemPrompt = "You are a helpful assistant."
    assert resume_agent.getSystemPrompt() == "You are a helpful assistant."

def test_getSystemPrompt_no_system_prompt(resume_agent):
    resume_agent.systemPrompt = None
    with pytest.raises(ValueError, match="No system prompt found."):
        resume_agent.getSystemPrompt()

def test_getSystemPrompt_empty(resume_agent):
    resume_agent.systemPrompt = ""
    with pytest.raises(ValueError, match="No system prompt found."):
        resume_agent.getSystemPrompt()

def test_resetAgent_success(resume_agent):
    resume_agent.userPrompt = "Test prompt"
    resume_agent.response = "dummy response"
    resume_agent.client = MagicMock()

    resume_agent.resetAgent()

    assert resume_agent.userPrompt is None
    assert resume_agent.response is None
    assert resume_agent.client is None
    assert resume_agent.jsonOutput is None
    assert resume_agent.modelName == resume_agent.modelName
    assert resume_agent.systemPrompt == resume_agent.systemPrompt

def test_deleteAgent_success(resume_agent):
    resume_agent.userPrompt = "Test prompt"
    resume_agent.response = "dummy response"
    resume_agent.client = MagicMock()
    resume_agent.modelName = "test-model"
    resume_agent.systemPrompt = "You are a helpful assistant."

    resume_agent.deleteAgent()

    assert resume_agent.userPrompt is None
    assert resume_agent.response is None
    assert resume_agent.client is None
    assert resume_agent.modelName is None
    assert resume_agent.systemPrompt is None
    assert resume_agent.jsonOutput is None