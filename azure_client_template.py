import os
from openai import AzureOpenAI

class AzureEnrichmentClient:
    """
    A template client for connecting this middleware output
    to an Enterprise Azure OpenAI instance.
    """

    def __init__(self, api_key: str, endpoint: str, deployment_name: str, api_version="2024-02-15-preview"):
        """
        Initialize the Azure Client.

        Args:
            api_key: Your Azure OpenAI API Key.
            endpoint: Your Azure OpenAI Endpoint (e.g., https://my-org.openai.azure.com/).
            deployment_name: The name of your model deployment (e.g., 'gpt-4-turbo').
            api_version: API version to use.
        """
        self.client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=endpoint
        )
        self.deployment_name = deployment_name

    def enrich_content(self, content: str, prompt_system: str = None) -> str:
        """
        Sends the scraped content to Azure for enrichment/summarization.
        """
        if not prompt_system:
            # Load default prompt if available
            prompt_path = os.path.join("config", "synthesis-prompt.md")
            if os.path.exists(prompt_path):
                with open(prompt_path, "r", encoding="utf-8") as f:
                    prompt_system = f.read()
            else:
                prompt_system = "You are a helpful assistant. Summarize this content."

        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": prompt_system},
                    {"role": "user", "content": f"Analyze the following content:\n\n{content[:15000]}"} # Truncate for safety
                ],
                temperature=0.7,
                max_tokens=800
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error calling Azure API: {str(e)}"

# Example Usage:
if __name__ == "__main__":
    # PASTE YOUR CREDENTIALS HERE FOR LOCAL TESTING
    KEY = "paste-your-key-here"
    ENDPOINT = "https://your-org.openai.azure.com/"
    DEPLOYMENT = "gpt-4"

    if KEY != "paste-your-key-here":
        client = AzureEnrichmentClient(KEY, ENDPOINT, DEPLOYMENT)
        print("Client initialized. Ready to process content.")
    else:
        print("Please configure your Azure credentials in the file.")
