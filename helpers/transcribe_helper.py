class Transcribe_Helper:
    def __init__(self, transcribe_client) -> None:
        self.transcribe_client = transcribe_client

    def transcribe_audio(self, job_name, bucket_name, upload_object):
        try:
            transcribe_response = self.transcribe_client.start_transcription_job(
                TranscriptionJobName = job_name,
                Media = {
                    'MediaFileUri': f's3://{bucket_name}/{upload_object}'
                },
                MediaFormat = 'mp3',
                LanguageCode = 'en-US',
                OutputBucketName = bucket_name,
                Settings = {
                    'ShowSpeakerLabels': True,
                    'MaxSpeakerLabels': 2
                }
            )
            print(f"Successfully transcribed job {job_name} to bucket {bucket_name}")
            return transcribe_response
        except self.transcribe_client.exceptions.ConflictException:
            print(f"A transcription job with the name '{job_name}' already exists. Please use a different job name.")
            return None

    def get_job_status(self, job_name):
        return self.transcribe_client.get_transcription_job(TranscriptionJobName = job_name)
