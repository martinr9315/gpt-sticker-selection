import openai
import csv
import tiktoken
import os


# Initialize API client
openai.api_key = os.environ["OPENAI_API_KEY"]


def num_tokens_from_messages(messages, model="gpt-3.5-turbo-16k"):
    """Return the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model in {
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-16k-0613",
        "gpt-3.5-turbo-16k",
        "gpt-4-0314",
        "gpt-4-32k-0314",
        "gpt-4-0613",
        "gpt-4-32k-0613",
        }:
        tokens_per_message = 3
        tokens_per_name = 1
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
        )
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3
    return num_tokens


def parse_stickers(file):
    # Read stickers from a CSV file
    stickers = []
    with open("sticker_slugs.csv", mode='r') as file:
        csv_file = csv.reader(file)
        for line in csv_file:
            stickers.append(line[0])
    return stickers


def caption_stickering(stickers, captions, model="gpt-3.5-turbo-16k", report_cost=False):
    prompt = "You are a designer who must select 3 text stickers to add them to a page of a scrapbook that contains images described by the captions below. In one full sentence, identify the theme of this page. Use that explanation to return a JSON of the 3 most appropriate text stickers from the sticker list below, with the keys as '1', '2', '3'."
    prompt += "The format of your response should be: Theme: sentence \n JSON: json_text"

    conversation = [{"role": "system", "content": f"{prompt}"}]

    # Include image captions
    conversation.append({"role": "user", "content": f"\nImage captions: {captions}"})

    # Load text stickers
    conversation.append({"role": "user", "content": f'\nSticker list: {stickers[:1000]}'})

    # Make the API call
    response = openai.ChatCompletion.create(
      model=model,
      messages=conversation,
      temperature=0.2
    )

    # Calculate number of tokens & cost
    if report_cost:
        # tokens = num_tokens_from_messages(conversation, model)
        # print(f"{tokens} prompt tokens counted.")
        # print(f'{response["usage"]["prompt_tokens"]} prompt tokens used.')
        # print(f'{response["usage"]["completion_tokens"]} completion tokens used.')
        print(f'{response["usage"]["total_tokens"]} total tokens used.')
        print(f"cost: {(response['usage']['total_tokens']/1000)*.003}")

    model_response = response['choices'][0]['message']['content']
    return model_response


def main():
    stickers = parse_stickers("sticker_slugs.csv")

    captions = [["A boy and girl sitting in a train",
                 "A red machine with a sign",
                 "A couple of kids sitting next to luggage",
                 "A boy standing next to a train"],
                ["a woman is holding a baby on a bed",
                 "a woman holding a baby in her arms",
                 "a basket filled with baby blankets",
                 "a toy airplane sitting on top of a table",
                 "a baby boy laying on a pillow on a bed"],
                ["a rainbow painted street in the city",
                 "a woman walking down a rainbow painted street",
                 "two people standing on a rainbow painted street",
                 "a woman standing in front of a bar",
                 "a red building with a green and red sign"]]

    for spread in captions:
        print(caption_stickering(stickers, spread, report_cost=True))


if __name__ == "__main__":
    main()
