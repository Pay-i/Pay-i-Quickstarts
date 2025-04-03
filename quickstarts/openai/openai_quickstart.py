import os
from datetime import datetime

# Import required libraries
from openai import OpenAI
from payi import Payi
from payi.lib.helpers import payi_openai_url, create_headers

# API Keys (from environment variables)
# Replace with your actual API keys or use environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-api-key")
PAYI_API_KEY = os.getenv("PAYI_API_KEY", "your-payi-api-key")

# Initialize Pay-i client (for limit management)
payi_client = Payi(api_key=PAYI_API_KEY)

# Initialize OpenAI client with Pay-i integration
openai_client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url=payi_openai_url(),  # Uses Pay-i as proxy
    default_headers={"xProxy-api-key": PAYI_API_KEY}  # Authenticates with Pay-i
)

# Create a limit (optional)
try:
    limit_name = "QuickStart Demo Limit"
    limit_response = payi_client.limits.create(
        limit_name=limit_name,
        max=10.00  # $10 USD limit
    )
    limit_id = limit_response.limit.limit_id  # Store limit ID to track costs against it
except Exception as e:
    limit_id = None

# Create request tags for custom analytics and track costs against limit
tags = ["standard-request"]
headers = create_headers(request_tags=tags, limit_ids=[limit_id] if limit_id else None)

# Make a standard API call, just like we would with regular OpenAI
response = openai_client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Explain what Pay-i does in one sentence."}],
    max_tokens=50,
    extra_headers=headers
)


# Print the result
print("\nResponse:")
print(f"---\n{response.choices[0].message.content}\n---")

# Pay-i automatically captures tracking information like cost and request ID
if hasattr(response, 'xproxy_result'):
    cost_info = response.xproxy_result.get('cost', {})
    request_id = response.xproxy_result.get('request_id', 'N/A')
    print("\nPay-i tracking information:")
    print(f"- Request ID: {request_id}")
    print(f"- Cost: ${cost_info}")

if limit_id:
    status = payi_client.limits.retrieve(limit_id=limit_id)  # Retrieve current limit status
    
    # Get the total cost from the limit status
    total_cost = status.limit.totals.cost.total
    if hasattr(total_cost, 'base'):
        total_cost = total_cost.base  # Handle different cost object formats
        
    usage_percent = (total_cost / status.limit.max) * 100  # Calculate usage percentage
    
    print(f"✓ Current usage: ${total_cost:.6f} of ${status.limit.max:.2f} ({usage_percent:.2f}%)")
    
# Tags for analytics and tracking against our limit
tags = ["streaming-request"]
headers = create_headers(request_tags=tags, limit_ids=[limit_id] if limit_id else None)

# Make streaming request
stream = openai_client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Write a short poem about AI cost efficiency."}],
    max_tokens=100,
    stream=True,  # Enable streaming
    extra_headers=headers
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
if limit_id:
    status = payi_client.limits.retrieve(limit_id=limit_id)  # Retrieve current limit status
    
    # Get the total cost from the limit status
    total_cost = status.limit.totals.cost.total
    if hasattr(total_cost, 'base'):
        total_cost = total_cost.base  # Handle different cost object formats
        
    usage_percent = (total_cost / status.limit.max) * 100  # Calculate usage percentage
    
    print(f"\nChecking final limit status...")
    print(f"✓ Final usage: ${total_cost:.6f} of ${status.limit.max:.2f} ({usage_percent:.2f}%)")

print("Now you can check your Pay-i dashboard to see detailed metrics and costs.")