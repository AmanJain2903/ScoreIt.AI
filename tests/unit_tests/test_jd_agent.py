import pytest
from unittest.mock import patch, MagicMock
from src.jd_extractor_agent.jd_agent import JobDescriptionAgent
from src.jd_extractor_agent import config

pytestmark = pytest.mark.unit

@pytest.fixture
def jd_agent(apiKey="fake-api-key",
        modelName="test-model",
        systemPrompt="You are a helpful assistant.",
        useDefaultModelIfNone=False,
        useDefaultSystemPromptIfNone=False):
    return JobDescriptionAgent(
        apiKey=apiKey,
        modelName=modelName,
        systemPrompt=systemPrompt,
        useDefaultModelIfNone=useDefaultModelIfNone,
        useDefaultSystemPromptIfNone=useDefaultSystemPromptIfNone
    )

def test_initialization_success(jd_agent):
    assert jd_agent.modelName == "test-model"
    assert jd_agent.systemPrompt == "You are a helpful assistant."
    assert jd_agent.response is None
    assert jd_agent.client is None
    assert jd_agent.userPrompt is None
    assert jd_agent.jsonOutput is None

def test_initialization_failure_no_api_key():
    with pytest.raises(ValueError, match="API key not found."):
        JobDescriptionAgent(
            apiKey=None,
            modelName="test-model",
            systemPrompt="You are a helpful assistant."
        )

def test_initialization_failure_no_model_name():
    with pytest.raises(ValueError, match="Model name not found."):
        JobDescriptionAgent(
            apiKey="fake-api-key",
            modelName=None,
            systemPrompt="You are a helpful assistant.",
            useDefaultSystemPromptIfNone=False,
            useDefaultModelIfNone=False
        )

def test_initialization_failure_no_system_prompt():
    with pytest.raises(ValueError, match="System prompt not found."):
        JobDescriptionAgent(
            apiKey="fake-api-key",
            modelName="test-model",
            systemPrompt=None,
            useDefaultModelIfNone=False,
            useDefaultSystemPromptIfNone=False
        )

@patch('src.jd_extractor_agent.jd_agent.OpenAI')
def test_getClient_success(mock_openai, jd_agent):
    mock_client = MagicMock()
    mock_openai.return_value = mock_client

    jd_agent.getClient()

    assert jd_agent.client is not None
    assert isinstance(jd_agent.client, MagicMock)

@patch('src.jd_extractor_agent.jd_agent.OpenAI')
def test_getClient_failure(mock_openai, jd_agent):
    mock_openai.side_effect = Exception("Client initialization failed.")

    with pytest.raises(ValueError, match="Failed to initialize client: Client initialization failed."):
        jd_agent.getClient()
        
def test_deleteClient_success(jd_agent):
    class DummyClient:
        def close(self):
            pass

    jd_agent.client = DummyClient()
    jd_agent.deleteClient()
    assert jd_agent.client is None

def test_deleteClient_not_initialized(jd_agent):
    with pytest.raises(ValueError, match="Client not initialized."):
        jd_agent.deleteClient()

def test_getAgentInfo(jd_agent):
    info = jd_agent.getAgentInfo()
    assert isinstance(info, dict)
    assert "modelName" in info
    assert "systemPrompt" in info
    assert "userPrompt" in info
    assert "response" in info
    assert "jsonOutput" in info
    assert "client" in info

@patch('src.jd_extractor_agent.jd_agent.OpenAI')
def test_getAgentStatus_initialized(mock_openai, jd_agent):
    mock_client = MagicMock()
    mock_openai.return_value = mock_client

    jd_agent.getClient()
    status = jd_agent.getAgentStatus()
    assert status == "Agent is good to go with."

def test_getAgentStatus_not_initialized(jd_agent):
    status = jd_agent.getAgentStatus()
    assert status == "Client not initialized."

def test_setUserPrompt_success(jd_agent):
    jd_agent.setUserPrompt("Test prompt")
    assert jd_agent.userPrompt == "test prompt"

def test_setUserPrompt_empty(jd_agent):
    with pytest.raises(ValueError, match="User prompt cannot be empty."):
        jd_agent.setUserPrompt("")

def test_parseResponse_no_response(jd_agent):
    jd_agent.response = None
    with pytest.raises(ValueError, match="No response found."):
        jd_agent.parseRespone()

def test_parseResponse_invalid_json(jd_agent):
    jd_agent.response = "Invalid JSON response"
    with pytest.raises(ValueError, match="Failed to parse JSON response: substring not found"):
        jd_agent.parseRespone()

def test_parseResponse_success(jd_agent):
    jd_agent.response = '{"key": "value"}'
    parsed_json = jd_agent.parseRespone()
    assert isinstance(parsed_json, dict)
    assert parsed_json == {"key": "value"}

def test_getResponse_success(jd_agent):
    jd_agent.userPrompt = "Test prompt"
    jd_agent.response = '{"key": "value"}'
    jd_agent.jsonOutput = {"key": "value"}
    jd_agent.client = MagicMock()
    jd_agent.client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content='{"key": "value"}'))]
    )
    jd_agent.getResponse()
    assert jd_agent.response == '{"key": "value"}'
    assert jd_agent.jsonOutput == {"key": "value"}

def test_getResponse_no_client(jd_agent):
    jd_agent.client = None
    jd_agent.userPrompt = "Test prompt"
    jd_agent.getClient = MagicMock()
    with pytest.raises(ValueError, match="Client not initialized."):
        jd_agent.getResponse()

def test_getResponse_no_model_name(jd_agent):
    jd_agent.modelName = None
    jd_agent.userPrompt = "Test prompt"
    with pytest.raises(ValueError, match="Model name not set."):
        jd_agent.getResponse()

def test_getResponse_no_system_prompt(jd_agent):
    jd_agent.systemPrompt = None
    jd_agent.userPrompt = "Test prompt"
    with pytest.raises(ValueError, match="System prompt not set."):
        jd_agent.getResponse()

def test_getResponse_no_user_prompt(jd_agent):
    jd_agent.userPrompt = None
    with pytest.raises(ValueError, match="User prompt not set."):
        jd_agent.getResponse()

def test_getResponse_error_in_response(jd_agent):
    jd_agent.userPrompt = "Test prompt"
    jd_agent.client = MagicMock()
    jd_agent.client.chat.completions.create.return_value = MagicMock(
        choices=[],
        error={"message": "Error in response"}
    )
    with pytest.raises(ValueError, match="Error in response: Error in response"):
        jd_agent.getResponse()

def test_getResponse_error(jd_agent):
    jd_agent.userPrompt = "Test prompt"
    jd_agent.client = MagicMock()
    jd_agent.client.chat.completions.create.return_value = MagicMock(
        choices=[],
    )
    jd_agent.client.chat.completions.create.side_effect = Exception("API error")
    with pytest.raises(ValueError, match="Failed to get response: API error"):
        jd_agent.getResponse()

def test_getResponse_no_choices(jd_agent):
    jd_agent.userPrompt = "Test prompt"
    jd_agent.client = MagicMock()
    jd_agent.client.chat.completions.create.return_value = MagicMock(choices=[MagicMock(message=MagicMock(content=None))])
    with pytest.raises(ValueError, match="No content in response."):
        jd_agent.getResponse()

def test_getResponse_no_content(jd_agent):
    jd_agent.userPrompt = "Test prompt"
    jd_agent.client = MagicMock()
    jd_agent.client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content=None))]
    )
    with pytest.raises(ValueError, match="No content in response."):
        jd_agent.getResponse()

def test_getJsonOutput_success(jd_agent):
    jd_agent.userPrompt = "Test prompt"
    jd_agent.response = '{"key": "value"}'
    jd_agent.jsonOutput = {"key": "value"}
    jd_agent.client = MagicMock()
    jd_agent.client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content='{"key": "value"}'))]
    )
    jd_agent.getJsonOutput()
    assert jd_agent.jsonOutput == {"key": "value"}

def test_getJsonOutput_try_get_response(jd_agent):
    jd_agent.userPrompt = "Test prompt"
    jd_agent.response = None
    jd_agent.jsonOutput = None
    jd_agent.client = MagicMock()
    jd_agent.client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content='{"key": "value"}'))]
    )
    jd_agent.getJsonOutput()
    assert jd_agent.jsonOutput == {"key": "value"}

def test_getJsonOutput_no_response(jd_agent):
    jd_agent.userPrompt = "Test prompt"
    jd_agent.response = None
    jd_agent.jsonOutput = None
    jd_agent.client = MagicMock()
    jd_agent.client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content=None))]
    )
    with pytest.raises(ValueError, match="No JSON output found."):
        jd_agent.getJsonOutput()

def test_getResponseText_success(jd_agent):
    jd_agent.userPrompt = "Test prompt"
    jd_agent.response = '{"key": "value"}'
    jd_agent.jsonOutput = {"key": "value"}
    jd_agent.client = MagicMock()
    jd_agent.client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content='{"key": "value"}'))]
    )
    jd_agent.getResponseText()
    assert jd_agent.response == '{"key": "value"}'

def test_getResponseText_try_get_response(jd_agent):
    jd_agent.userPrompt = "Test prompt"
    jd_agent.response = None
    jd_agent.jsonOutput = None
    jd_agent.client = MagicMock()
    jd_agent.client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content='{"key": "value"}'))]
    )
    jd_agent.getResponseText()
    assert jd_agent.response == '{"key": "value"}'

def test_getResponseText_no_response(jd_agent):
    jd_agent.userPrompt = "Test prompt"
    jd_agent.response = None
    jd_agent.jsonOutput = None
    jd_agent.client = MagicMock()
    jd_agent.client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content=None))]
    )
    with pytest.raises(ValueError, match="No response found."):
        jd_agent.getResponseText()

def test_getUserPrompt_success(jd_agent):
    jd_agent.userPrompt = "Test prompt"
    assert jd_agent.getUserPrompt() == "Test prompt"

def test_getUserPrompt_no_user_prompt(jd_agent):
    jd_agent.userPrompt = None
    with pytest.raises(ValueError, match="No user prompt found."):
        jd_agent.getUserPrompt()

def test_getUserPrompt_empty(jd_agent):
    jd_agent.userPrompt = ""
    with pytest.raises(ValueError, match="No user prompt found."):
        jd_agent.getUserPrompt()

def test_getModelName_success(jd_agent):
    jd_agent.modelName = "test-model"
    assert jd_agent.getModelName() == "test-model"

def test_getModelName_no_model_name(jd_agent):
    jd_agent.modelName = None
    with pytest.raises(ValueError, match="No model name found."):
        jd_agent.getModelName()

def test_getModelName_empty(jd_agent):
    jd_agent.modelName = ""
    with pytest.raises(ValueError, match="No model name found."):
        jd_agent.getModelName()

def test_getSystemPrompt_success(jd_agent):
    jd_agent.systemPrompt = "You are a helpful assistant."
    assert jd_agent.getSystemPrompt() == "You are a helpful assistant."

def test_getSystemPrompt_no_system_prompt(jd_agent):
    jd_agent.systemPrompt = None
    with pytest.raises(ValueError, match="No system prompt found."):
        jd_agent.getSystemPrompt()

def test_getSystemPrompt_empty(jd_agent):
    jd_agent.systemPrompt = ""
    with pytest.raises(ValueError, match="No system prompt found."):
        jd_agent.getSystemPrompt()

def test_resetAgent_success(jd_agent):
    jd_agent.userPrompt = "Test prompt"
    jd_agent.response = "dummy response"
    jd_agent.client = MagicMock()

    jd_agent.resetAgent()

    assert jd_agent.userPrompt is None
    assert jd_agent.response is None
    assert jd_agent.client is None
    assert jd_agent.jsonOutput is None
    assert jd_agent.modelName == jd_agent.modelName
    assert jd_agent.systemPrompt == jd_agent.systemPrompt

def test_deleteAgent_success(jd_agent):
    jd_agent.userPrompt = "Test prompt"
    jd_agent.response = "dummy response"
    jd_agent.client = MagicMock()
    jd_agent.modelName = "test-model"
    jd_agent.systemPrompt = "You are a helpful assistant."

    jd_agent.deleteAgent()

    assert jd_agent.userPrompt is None
    assert jd_agent.response is None
    assert jd_agent.client is None
    assert jd_agent.modelName is None
    assert jd_agent.systemPrompt is None
    assert jd_agent.jsonOutput is None