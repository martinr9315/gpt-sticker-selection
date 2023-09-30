import openai
import csv
import tiktoken
import os

# TODO: change 'sticker' to 'text phrase'

# Initialize API client
openai.api_key = os.environ['OPENAI_API_KEY']


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


def parse_stickers(f):
    # Read stickers from a CSV file
    stickers = []
    with open(f, mode='r') as file:
        csv_file = csv.reader(file)
        next(csv_file, None)
        for line in csv_file:
            stickers.append(line[0])
    return stickers



def caption_stickering(stickers, spread_captions, model="gpt-3.5-turbo-16k", report_cost=False):
    prompt = "Task: You are a designer who must select 3 text stickers to add them to a page of a scrapbook given a set of captions describing the images in the spread. In one full sentence, identify the theme of this page. Use that explanation to return a JSON of the 3 most appropriate text stickers from the sticker list below, with the keys as '1', '2', '3'."
    prompt += "The format of each response should be:\nTheme: sentence\nJSON: json_text"

    conversation = [{"role": "system", "content": f"{prompt}"}]

    # Load text stickers
    conversation.append({"role": "user", "content": f'\nSticker list: {stickers[:1000]}'})

    # Format captions
    result = [', '.join(spread) for spread in spread_captions]
    captions = '\n\n'.join(result)

    # Include image captions
    conversation.append({"role": "user", "content": f"You are given the following {len(spread_captions)} sets of captions. Return one response for each set:\n {captions}."})

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
        print(f'{response["usage"]["total_tokens"]} total tokens used.')
        print(f"cost: {(response['usage']['total_tokens']/1000)*.003}")

    model_response = response['choices'][0]['message']['content']
    return model_response


def main():
    stickers = parse_stickers("representative_slugs.csv")

    captions = [["a woman is holding a baby on a bed",
                 "a woman holding a baby in her arms",
                 "a basket filled with baby blankets",
                 "a toy airplane sitting on top of a table",
                 "a baby boy laying on a pillow on a bed"],
                ["a rainbow painted street in the city",
                 "a woman walking down a rainbow painted street",
                 "two people standing on a rainbow painted street",
                 "a woman standing in front of a bar",
                 "a red building with a green and red sign"],
                ["a couple of kids sitting next to luggage",
                 "a red machine with a sign",
                 "a boy and girl sitting in a train",
                 "a boy standing next to a train"]]

    print(caption_stickering(stickers, captions, report_cost=True))


if __name__ == "__main__":
    main()

