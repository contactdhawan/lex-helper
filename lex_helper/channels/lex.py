# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Lex-specific channel implementation."""

from lex_helper.channels.base import Channel
from lex_helper.core.types import (
    LexBaseResponse,
    LexCustomPayload,
    LexImageResponseCard,
    LexMessages,
    LexPlainText,
    LexSSML,
)


class LexChannel(Channel):
    """Channel implementation for Lex-specific message formatting."""

    def format_message(self, message: LexMessages) -> LexBaseResponse:
        """Format a single Lex message.

        Args:
            message: The Lex message to format

        Returns:
            The formatted message string
        """
        print(f"[FLOW - lex.py - Added by Claude Haiku] format_message called with type: {type(message).__name__}")
        
        try:
            if isinstance(message, LexSSML):
                print(f"[FLOW - lex.py - Added by Claude Haiku] Message is LexSSML, formatting...")
                return self.format_ssml_text(message)
            if isinstance(message, LexPlainText):
                print(f"[FLOW - lex.py - Added by Claude Haiku] Message is LexPlainText, formatting...")
                return self.format_plain_text(message)
            if isinstance(message, LexImageResponseCard):
                print(f"[FLOW - lex.py - Added by Claude Haiku] Message is LexImageResponseCard, formatting...")
                return self.format_image_card(message)
            if isinstance(message, LexCustomPayload):  # type: ignore
                print(f"[FLOW - lex.py - Added by Claude Haiku] Message is LexCustomPayload, formatting...")
                return self.format_custom_payload(message)
            
            print(f"[ERROR - lex.py - Added by Claude Haiku] Unsupported message type: {type(message).__name__}")
            return LexPlainText(content="Unsupported message type")
            
        except Exception as e:
            print(f"[ERROR - lex.py - Added by Claude Haiku] Exception in format_message: {type(e).__name__}: {str(e)}")
            import traceback
            print(f"[ERROR - lex.py - Added by Claude Haiku] Traceback: {traceback.format_exc()}")
            raise

    def format_messages(self, messages: list[LexMessages]) -> list[LexBaseResponse]:
        """Format a list of Lex messages.

        Args:
            messages: List of Lex messages to format

        Returns:
            List of formatted message strings
        """
        print(f"[FLOW - lex.py - Added by Claude Haiku] format_messages called with {len(messages)} messages")
        
        try:
            result = [self.format_message(message) for message in messages]
            print(f"[FLOW - lex.py - Added by Claude Haiku] Formatted {len(result)} messages successfully")
            return result
        except Exception as e:
            print(f"[ERROR - lex.py - Added by Claude Haiku] Exception in format_messages: {type(e).__name__}: {str(e)}")
            import traceback
            print(f"[ERROR - lex.py - Added by Claude Haiku] Traceback: {traceback.format_exc()}")
            raise

    def format_plain_text(self, message: LexPlainText) -> LexBaseResponse:
        """Format a Lex plain text message.

        Overrides the base implementation to handle Lex-specific formatting.

        Args:
            message: The plain text message to format

        Returns:
            The formatted plain text
        """
        # For Lex, we can just use the base implementation
        return super().format_plain_text(message)

    def format_ssml_text(self, message: LexSSML) -> LexBaseResponse:
        """Format a Lex plain text message.

        Overrides the base implementation to handle Lex-specific formatting.

        Args:
            message: The plain text message to format

        Returns:
            The formatted plain text
        """
        # For Lex, we can just use the base implementation
        return super().format_ssml_text(message)

    def format_image_card(self, card: LexImageResponseCard) -> LexBaseResponse:
        """Format a Lex image response card.

        Overrides the base implementation to handle Lex-specific formatting.

        Args:
            card: The image card to format

        Returns:
            The formatted card text
        """
        # For Lex, we want to format buttons with their value rather than text
        parts = [card.imageResponseCard.title]
        if card.imageResponseCard.subtitle:
            parts.append(card.imageResponseCard.subtitle)
        if card.imageResponseCard.imageUrl:
            parts.append(f"Image: {card.imageResponseCard.imageUrl}")
        if card.imageResponseCard.buttons:
            button_texts = [f"[{btn.text} -> {btn.value}]" for btn in card.imageResponseCard.buttons]
            parts.append("Buttons: " + " ".join(button_texts))
        return LexPlainText(content="\n".join(parts))

    def format_custom_payload(self, payload: LexCustomPayload) -> LexBaseResponse:
        """Format a Lex custom payload message.

        Overrides the base implementation to handle Lex-specific formatting.

        Args:
            payload: The custom payload to format

        Returns:
            The formatted payload text
        """
        content = payload.content
        if isinstance(content, dict):
            if "text" in content:
                return str(content["text"])  # type: ignore
            if "message" in content:
                return str(content["message"])  # type: ignore
            return LexCustomPayload(content=str(content))
        return LexCustomPayload(content=str(content))
