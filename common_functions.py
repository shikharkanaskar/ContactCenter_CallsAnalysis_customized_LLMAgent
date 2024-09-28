import json

from jinja2 import Environment, FileSystemLoader
from helpers.client_initialization import bedrock_runtime_client

env = Environment(
    loader = FileSystemLoader('templates')
) # Used by jinja to load template

def extract_transcript_from_text(file_content):
    transcript_json = json.loads(file_content)
    output_text = ""
    current_speaker = None

    items = transcript_json['results']['items']

    for item in items:
        speaker_label = item.get('speaker_label', None)
        content = item['alternatives'][0]['content']

        if speaker_label is not None and speaker_label != current_speaker:
            current_speaker = speaker_label
            output_text += f"\n{current_speaker}: "

        if item['type'] == 'punctuation':
            output_text = output_text.rstrip()

        output_text += f"{content} "

    return output_text


def bedrock_summarisation(transcript):
    template = env.get_template("prompt_template.txt")
    data = {
        'transcript': transcript,
        'topics': ['charges', 'location', 'availability']
    }
    prompt = template.render(data)

    print(prompt)

    kwargs = {
        "modelId": "amazon.titan-text-lite-v1", #LLM from Amazon
        "contentType": "application/json", #Mine type of data we are going to send in i.e input in our request
        "accept": "*/*", # Mine type of data we're going to receive well i.e the output [json by default]
        "body": json.dumps(
            {
                "inputText": prompt,
                "textGenerationConfig": {
                    "maxTokenCount": 512,
                    "temperature": 0,
                    "topP": 0.9
                }
            },
        )
    }

    response = bedrock_runtime_client.invoke_model(**kwargs) #Body of the response returned gives a pointer to a streaming boto3 object where the actual data is stored.
    response_body = json.loads(response.get('body').read())
    summary = response_body['results'][0]['outputText']
    return summary
