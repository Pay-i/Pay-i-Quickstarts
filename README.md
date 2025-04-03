# Pay-i Quickstarts

Welcome to the Pay-i Quickstarts repository! This repository contains examples and quickstarts to help you integrate Pay-i with various GenAI providers.

## 🚀 Quickstart

### 1️⃣ Install SDK

```bash
pip install payi openai
```
For Jupyter notebooks:
```python
%pip install payi openai
```

### 2️⃣ Set API keys

```python
OPENAI_API_KEY = "sk-..."  # Your OpenAI API key
PAYI_API_KEY = "api-..."   # Your Pay-i API key
```

### 3️⃣ Configure client

```python
from openai import OpenAI
from payi.lib.helpers import payi_openai_url

# Configure OpenAI client to use Pay-i
client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url=payi_openai_url(),
    default_headers={"xProxy-api-key": PAYI_API_KEY}
)
```

### 4️⃣ Use normally

```python
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello, world!"}]
)

print(response.choices[0].message.content)
```

> 💡 **Tip**
>
> Looking for more features? Check out our [Quickstart Walkthrough](https://docs.pay-i.com/docs/quickstart-demo) for limits, analytics tags, streaming, and more.

## 📚 Example Notebooks

This repository contains several Python notebooks that make it easy to get up and running with popular providers:

- [OpenAI](./quickstarts/openai/)
- [Azure OpenAI](./quickstarts/azure.openai/)
- [Anthropic](./quickstarts/anthropic/)
- [AWS Bedrock](./quickstarts/bedrock/)
- [LangChain](./quickstarts/langchain/)

## 🛠️ Provider Configuration

For detailed guides on configuring Pay-i with different GenAI providers, check out our [documentation](https://docs.pay-i.com/docs/genai-provider-configuration).

## 🧩 Decorators

Our Python SDK provides decorators that make it easy to use Pay-i with Python applications, letting you annotate your functions with metadata that gets passed to Pay-i. See our [decorator examples](https://docs.pay-i.com/docs/inheritable-decorators) for more information.

## 📊 Additional Resources

- [Pay-i Documentation](https://docs.pay-i.com)
- [Pay-i API Reference](https://docs.pay-i.com/reference/)
- [Support](mailto:support@pay-i.com)

## Getting Help

At any time, you can send mail to [support@pay-i.com](mailto:support@pay-i.com) to report issues, ask questions, or get help.

We're excited you're here! 💚

<p align="center">
  <img src="https://files.readme.io/c20eecb-pay-i-logo-full-color-rgb-400px-w-72ppi.jpg" alt="Pay-i Logo">
</p>
