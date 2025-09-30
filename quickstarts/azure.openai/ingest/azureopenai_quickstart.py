import os
from dotenv import load_dotenv
from openai import AzureOpenAI
from payi import Payi
from payi.lib.instrument import payi_instrument, track_context

# Load environment variables from .env file
load_dotenv()

AZURE_OPENAI_MODEL = os.getenv("AZURE_OPENAI_MODEL")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
AZURE_OPENAI_DEPLOYMENT_TYPE = os.getenv("AZURE_OPENAI_DEPLOYMENT_TYPE", None)

# Initialize Pay-i client for limit management
payi_client = Payi()  # Automatically uses PAYI_API_KEY environment variable

# Enable Pay-i instrumentation
payi_instrument()  

# Initialize Azure OpenAI client with Pay-i integration
azure_client = AzureOpenAI(
# Expected environment variables:
    # - AZURE_OPENAI_API_KEY=...
    # - AZURE_OPENAI_ENDPOINT=https://openai-xx-eastus.openai.azure.com/
    # - OPENAI_API_VERSION=2024-02-15-preview
)

# Create a limit (optional)
limit_name = "QuickStart Limit"
limit_response = payi_client.limits.create(
    limit_name=limit_name,
    max=10.00  # $10 USD limit
)
limit_id = limit_response.limit.limit_id  # Store limit ID to track costs against it

# Make a standard API call, just like we would with regular Azure OpenAI
with track_context(price_as_resource=AZURE_OPENAI_MODEL, resource_scope=AZURE_OPENAI_DEPLOYMENT_TYPE, limit_ids=[limit_id]):
    response = azure_client.chat.completions.create(
        model=AZURE_OPENAI_DEPLOYMENT,
        messages=[{"role": "user", "content": "Explain why value GenAI brings does in one sentence."}],
        max_tokens=50
    )

# Print the result
print("\nResponse:")
print(f"---\n{response.choices[0].message.content}\n---")

# Pay-i automatically captures tracking information like cost and request ID. xproxy_result is only available if the request was made through the Pay-i proxy.

status = payi_client.limits.retrieve(limit_id=limit_id)  # Retrieve current limit status
    
# Get the total cost from the limit status
total_cost = status.limit.totals.cost.total.base        
usage_percent = (total_cost / status.limit.max) * 100  # Calculate usage percentage
    
print(f"✓ Current usage: ${total_cost:.6f} of ${status.limit.max:.2f} ({usage_percent:.2f}%)")

# Make streaming request
with track_context(price_as_resource=AZURE_OPENAI_MODEL, resource_scope=AZURE_OPENAI_DEPLOYMENT_TYPE, limit_ids=[limit_id]):
    stream = azure_client.chat.completions.create(
        model=AZURE_OPENAI_DEPLOYMENT,
        messages=[{"role": "user", "content": "Write a short poem about AI cost efficiency."}],
        max_tokens=100,
        stream=True
    )


# Process the streaming response
print("\nStreaming response:")
print("---")

for chunk in stream:
    if chunk.choices and chunk.choices[0].delta.content:
        content = chunk.choices[0].delta.content
        print(content, end="")

print("\n---")

# Check final limit status
status = payi_client.limits.retrieve(limit_id=limit_id)  # Retrieve current limit status
    
# Get the total cost from the limit status
total_cost = status.limit.totals.cost.total
if hasattr(total_cost, 'base'):
    total_cost = total_cost.base  # Handle different cost object formats
        
usage_percent = (total_cost / status.limit.max) * 100  # Calculate usage percentage
    
print(f"\nChecking final limit status...")
print(f"✓ Final usage: ${total_cost:.6f} of ${status.limit.max:.2f} ({usage_percent:.2f}%)")

print("Now you can check your Pay-i dashboard to see detailed metrics and costs.")