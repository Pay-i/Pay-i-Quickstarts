import os
from dotenv import load_dotenv
from openai import OpenAI
from payi import Payi
from payi.lib.helpers import payi_openai_url, PayiHeaderNames
from payi.lib.instrument import payi_instrument, track_context

# Load environment variables from .env file
load_dotenv()

# Initialize Pay-i client for limit management
payi_client = Payi()  # Automatically uses PAYI_API_KEY environment variable

# Enable Pay-i instrumentation
payi_instrument(config={"proxy": True})  # Automatically creates payi sync/async clients using environment variables

# Initialize OpenAI client with Pay-i integration
openai_client = OpenAI(base_url=payi_openai_url(), default_headers={PayiHeaderNames.api_key: os.getenv("PAYI_API_KEY")})

# Create a limit (optional)
limit_name = "QuickStart Limit"
limit_response = payi_client.limits.create(
    limit_name=limit_name,
    max=10.00  # $10 USD limit
)
limit_id = limit_response.limit.limit_id  # Store limit ID to track costs against it

# Make a standard API call, just like we would with regular OpenAI
with track_context(request_tags=["standard-request"], limit_ids=[limit_id]):
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Explain why value GenAI brings does in one sentence."}],
        max_tokens=50
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

status = payi_client.limits.retrieve(limit_id=limit_id)  # Retrieve current limit status

# Get the total cost from the limit status
total_cost = status.limit.totals.cost.total.base        
usage_percent = (total_cost / status.limit.max) * 100  # Calculate usage percentage
    
print(f"✓ Current usage: ${total_cost:.6f} of ${status.limit.max:.2f} ({usage_percent:.2f}%)")
    
# Make streaming request
with track_context(request_tags=["streaming-request"], limit_ids=[limit_id]):
    stream = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
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
total_cost = status.limit.totals.cost.total.base        
usage_percent = (total_cost / status.limit.max) * 100  # Calculate usage percentage
    
print(f"\nChecking final limit status...")
print(f"✓ Final usage: ${total_cost:.6f} of ${status.limit.max:.2f} ({usage_percent:.2f}%)")

print("Now you can check your Pay-i dashboard to see detailed metrics and costs.")