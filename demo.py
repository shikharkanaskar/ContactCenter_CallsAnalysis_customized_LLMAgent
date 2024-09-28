import json
import os
import uuid # Used to make transcription job name unique
import time
from datetime import datetime, timedelta, timezone # For getting last 5 mins logs
from securing_credentials import LOGGING_ARN
from helpers.client_initialization import bedrock_runtime_client, bedrock_client, s3_client, transcribe_client, cloudwatch_client
from helpers.transcribe_helper import Transcribe_Helper
from helpers.s3_helper import S3_Helper
from helpers.bedrock_runtime_helper import Bedrock_Runtime_Helper
from common_functions import extract_transcript_from_text, bedrock_summarisation

#Imports for audio files
from pydub import AudioSegment
from pydub.playback import play
#Imports for template
from jinja2 import Template # Used for importing prompt template. It is a good technique to know.
from jinja2 import Environment, FileSystemLoader, PackageLoader, select_autoescape


# Variables
bucket_name = 'audiorecordingsllm' # S3 bucket name
logging_bucket_name = "bedrock-client-logs"
transcript_speaker_content_text = ""
metadata_file = 'transcription_metadata.json' # File to store the mapping
data_folder = 'data'

# Define Helpers
transcribe_helper = Transcribe_Helper(transcribe_client)
s3_helper = S3_Helper(s3_client)
bedrock_runtime_helper = Bedrock_Runtime_Helper(bedrock_runtime_client)

env = Environment(
    loader = FileSystemLoader('templates')
) # Used by jinja to load template
template = env.get_template("prompt_template.txt")

# Load existing metadata
try:
    with open(metadata_file, 'r') as f:
        metadata = json.load(f)
except FileNotFoundError:
    metadata = {}

# Process each audio file in the data folder
for filename in os.listdir(data_folder):
    if filename.endswith('.mp3'):
        if filename in metadata:
            print(f"Skipping {filename}: already processed.")
            continue

        # Load an MP3 file
        audio_path = os.path.join(data_folder, filename)
        audio = AudioSegment.from_mp3(audio_path)
        upload_object = filename

        # Upload audio file to S3
        s3_helper.upload_file(bucket_name, audio_path, upload_object)

        transcript_job_name = 'transcription-job-' + str(uuid.uuid4()) # transcription job needs to be unique

        # Take an object of transcribe helper and call its transscribe_audio function.
        transcript = transcribe_helper.transcribe_audio(transcript_job_name, bucket_name, upload_object)

        transcript_job_status = transcribe_helper.get_job_status(transcript_job_name)

        while True:
            transcript_job_status = transcribe_helper.get_job_status(transcript_job_name)
            if transcript_job_status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
                break
            time.sleep(2)


        if transcript_job_status['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED':
            print("Transcription Job Completed.")
            # Load the transcript from S3
            transcript_key = f"{transcript_job_name}.json"
            transcript_obj = s3_helper.get_object(bucket_name, transcript_key)
            print("Successfully loaded transcript")
            transcript_text = transcript_obj['Body'].read().decode('utf-8')
            transcript_json = json.loads(transcript_text)

            # Get transcript in "Speaker Name": "Content" format.

            current_speaker = None

            items = transcript_json['results']['items']

            for item in items:
                speaker_label = item.get('speaker_label', None)
                content = item['alternatives'][0]['content']

                if speaker_label is not None and speaker_label != current_speaker:
                    current_speaker = speaker_label
                    transcript_speaker_content_text += f"\n{current_speaker}: "

                if item['type'] == 'punctuation':
                    transcript_speaker_content_text = transcript_speaker_content_text.rstrip()

                transcript_speaker_content_text += f"{content} "

            # Save the filename and job name to a JSON file
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
            except FileNotFoundError:
                metadata = {}

            metadata[upload_object] = transcript_job_name

            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=4)

            print("Calling bedrock_summarisation")
            summary = bedrock_summarisation(transcript_speaker_content_text)

            print("Printing Bedrock runtime output")
            print(summary)







