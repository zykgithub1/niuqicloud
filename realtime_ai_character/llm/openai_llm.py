import os
from typing import Optional

from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.schema import BaseMessage, HumanMessage

from realtime_ai_character.database.chroma import get_chroma
from realtime_ai_character.llm.base import AsyncCallbackAudioHandler, AsyncCallbackTextHandler, LLM
from realtime_ai_character.logger import get_logger
from realtime_ai_character.utils import Character, timed


logger = get_logger(__name__)


class OpenaiLlm(LLM):
    def __init__(self, model):
        # 检查是否使用 DeepSeek API
        openai_api_base = os.getenv("OPENAI_API_BASE", "")
        if "deepseek.com" in openai_api_base:
            # 使用 DeepSeek 模型名称
            actual_model = "deepseek-chat"
            logger.info(f"Using DeepSeek API with model: {actual_model}")
        else:
            actual_model = model
            logger.info(f"Using OpenAI API with model: {actual_model}")
            
        if os.getenv("OPENAI_API_TYPE") == "azure":
            from langchain.chat_models import AzureChatOpenAI

            self.chat_open_ai = AzureChatOpenAI(
                deployment_name=os.getenv("OPENAI_API_MODEL_DEPLOYMENT_NAME", "gpt-35-turbo"),
                model=actual_model,
                temperature=0.5,
                streaming=True,
            )
        else:
            from langchain.chat_models import ChatOpenAI

            self.chat_open_ai = ChatOpenAI(
                model=actual_model, 
                temperature=0.5, 
                streaming=True,
                openai_api_base=openai_api_base if openai_api_base else None
            )
        self.config = {"model": actual_model, "temperature": 0.5, "streaming": True}
        self.db = get_chroma()

    def get_config(self):
        return self.config

    @timed
    async def achat(
        self,
        history: list[BaseMessage],
        user_input: str,
        user_id: str,
        character: Character,
        callback: AsyncCallbackTextHandler,
        audioCallback: Optional[AsyncCallbackAudioHandler] = None,
        metadata: Optional[dict] = None,
        *args,
        **kwargs,
    ) -> str:
        # 1. Generate context
        context = self._generate_context(user_input, character)

        # 2. Add user input to history
        history.append(
            HumanMessage(
                content=character.llm_user_prompt.format(context=context, query=user_input)
            )
        )

        # 3. Generate response
        callbacks = [callback, StreamingStdOutCallbackHandler()]
        if audioCallback is not None:
            callbacks.append(audioCallback)
        response = await self.chat_open_ai.agenerate(
            [history], callbacks=callbacks, metadata=metadata
        )
        logger.info(f"Response: {response}")
        return response.generations[0][0].text

    def _generate_context(self, query, character: Character) -> str:
        docs = self.db.similarity_search(query)
        docs = [d for d in docs if d.metadata["character_name"] == character.name]
        logger.info(f"Found {len(docs)} documents")

        context = "\n".join([d.page_content for d in docs])
        return context
