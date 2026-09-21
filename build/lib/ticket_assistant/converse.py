""" 
    Converse API 
        - one message format that works with EVERY model in Bedrock

        - format:
            - system:           list of dict. instructions, not messages. 
            - messages:         list of dict. conversation lives
            - inferenceConfig:  max tokens, temperature, Top P, Top K, etc.
            - modelId:          id of bedrock model to use
            - toolConfig:       dict. information on tools for the model to use.
            - guardrailConfig:  dict. info about what guardrail to wrap around the model call.
"""

from ticket_assistant.config import MODEL_ID
from ticket_assistant.aws import bedrock_runtime

def converse(
        messages: list[dict],
        system: str | None = None, 
        max_tokens: int = 1024, 
        temperature: float = 0.2,           # more deterministic responses for ticket priority classification
        tool_config: dict | None = None,
        guardrail_config: dict | None = None,
) -> dict:
    """ Make a converse callout and return the entire response for further inspection """

    request = {
        "modelId": MODEL_ID,
        "messages": messages,
        "inferenceConfig": {"maxTokens": max_tokens, "temperature": temperature}
    }

    # bedrock doesn't allow null values, but it does allow properties to be absent
    if system:
        request["system"] = [{"text": system}]
    if tool_config:
        request["toolConfig"] = tool_config
    if guardrail_config:
        request["guardrailConfig"] = guardrail_config

    # calling the Converse API and returning the response
    return bedrock_runtime().converse(**request)


def usage_of(response: dict) -> dict:
    """ retreiving the token usage of a Converse response """
    usage = response["usage"]

    return {
        "input_tokens": usage["inputTokens"],
        "output_tokens": usage["outputTokens"],
        "total_tokens": usage["totalTokens"],
    }

def text_of(response: dict) -> str:
    """ retreiving the generated text of a Converse response """
    blocks = response["output"]["message"]["content"]

    # grabbing only the text blocks and appending them to one string
    return "".join(block["text"] for block in blocks if "text" in block)    

def format_user_message(message: str) -> dict:
    """ Formats text into a message Converse API expects to receive """
    return {
        "role": "user",
        "content": [{"text": message}]
    }


if __name__ == "__main__":

    print("--- NORMAL RESPONSE ---")
    response = converse([format_user_message("In one sentence, what is Amazon Bedrock?")])
    print(text_of(response))
    print(usage_of(response))

    print("\n ENTIRE RESPONSE")
    print(response)


    print("--- GRUMPY RESPONSE ---")
    response = converse(
        [format_user_message("In one sentence, what is Amazon Bedrock?")],
        system = "You are a terse and grumpy engineer. Respond in as few words as possible."
    )
    print(text_of(response))
    print(usage_of(response))


    print("--- TICKET TRIAGE ---")

    ticket = "It is fine, I suppose. It has only been three days since I reported that checkout fails for saved cards, and I have only had to explain to about forty of my own customers why their orders will not go through."
    response = converse(
        [format_user_message(f"Assign a priority (high/medium/low) and justify in one sentence:\n\n {ticket}")],
        system = "You triage customer support tickets. Be decisive."
    )
    print(text_of(response))
    print(usage_of(response))