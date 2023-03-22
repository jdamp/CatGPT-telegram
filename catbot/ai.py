from io import BytesIO
import logging
import openai


class Catifier:
    def __init__(self, config: dict):
        self.config = config
        openai.api_key = config["OPENAI_API_KEY"]
        self.model = config["GPT_MODEL"]
        self.cat_config = {
            "role": "system",
            "content": "You mimick a cat and try to rephrase everything using cat-related analogies and puns",
        }

    async def catify(self, message: str) -> str:
        logging.info(f"catify was called with {message}")
        completion = await openai.ChatCompletion.acreate(
            model=self.model,
            messages=[
                self.cat_config,
                {
                    "role": "user",
                    "content": "Please turn the following text into a cat text.",
                },
                {"role": "user", "content": message},
            ],
        )
        answer = completion.choices[0].message.content
        logging.info(f"catify is returning {answer}")
        return answer

    async def reply(self, message: str) -> str:
        logging.info(f"reply was called with {message}")
        completion = await openai.ChatCompletion.acreate(
            model=self.model,
            messages=[self.cat_config, {"role": "user", "content": message}],
        )
        answer = completion.choices[0].message.content
        logging.info(f"reply is returning {answer}")
        return answer

    async def transcribe(self, audio_file: BytesIO) -> str:
        transcript = (await openai.Audio.atranscribe("whisper-1", audio_file))["text"]
        cat_transcript = await self.catify(transcript)
        return cat_transcript
