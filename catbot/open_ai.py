import logging
import openai


class OpenAiCatify:
    def __init__(self, config: dict):
        self.config = config
        openai.api_key = config["OPENAI_API_KEY"]
        self.model ="gpt-3.5-turbo"
        self.cat_config = {
            "role": "system",
            "content": "You mimick a cat and try to rephrase everything using cat-related analogies and puns"
        }

    async def catify(self, message: str):
        logging.info(f"I was called with {message}")
        completion = await openai.ChatCompletion.acreate(
            model=self.model,
            messages=[
                self.cat_config,
                {"role": "user", "content": "Please turn the following text into a cat text."},
                {"role": "user", "content": message}
            ]
        )
        answer = completion.choices[0].message.content
        logging.info(f"I am answering {answer}")
        return answer


    async def reply(self, message: str):
        logging.info(f"I was called with {message}")
        completion = await openai.ChatCompletion.acreate(
            model=self.model,
            messages=[
                self.cat_config,
                {"role": "user", "content": message}
            ]
        )
        answer = completion.choices[0].message.content
        logging.info(f"I am answering {answer}")
        return answer
