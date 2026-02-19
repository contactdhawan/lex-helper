# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import logging
from collections.abc import Callable
from typing import Any, TypeVar, cast

from pydantic import BaseModel

from lex_helper.channels.channel_formatting import format_for_channel
from lex_helper.core.call_handler_for_file import call_handler_for_file
from lex_helper.core.dialog import (
    any_unknown_slot_choices,
    get_intent,
    handle_any_unknown_slot_choice,
    parse_lex_request,
)
from lex_helper.core.types import (
    LexMessages,
    LexRequest,
    LexResponse,
    SessionAttributes,
)
from lex_helper.exceptions.handlers import IntentNotFoundError, handle_exceptions

logger = logging.getLogger(__name__)

# Import disambiguation components (lazy import to avoid circular dependencies)
try:
    from lex_helper.core.disambiguation.analyzer import DisambiguationAnalyzer
    from lex_helper.core.disambiguation.handler import DisambiguationHandler
    from lex_helper.core.disambiguation.types import DisambiguationConfig

    disambiguation_available = True
except ImportError:
    disambiguation_available = False
    DisambiguationConfig = None  # type: ignore
    DisambiguationHandler = None  # type: ignore
    DisambiguationAnalyzer = None  # type: ignore

T = TypeVar("T", bound=SessionAttributes)


class Config[T: SessionAttributes](BaseModel):
    session_attributes: T
    package_name: str | None = (
        "fulfillment_function"  # This is the name of the package to import the intents from.  Should be the same as the name of the package you're running the handler from.
    )
    auto_initialize_messages: bool = True  # Automatically initialize MessageManager with locale from request
    auto_handle_exceptions: bool = True  # Automatically handle exceptions and return error responses
    error_message: str | None = None  # Custom error message or message key for exceptions
    enable_disambiguation: bool = False  # Enable smart disambiguation for ambiguous input
    disambiguation_config: Any | None = None  # Configuration for disambiguation behavior


class LexHelper[T: SessionAttributes]:
    def __init__(self, config: Config[T]):
        self.config = config

        # Initialize disambiguation components if enabled
        self.disambiguation_handler = None
        self.disambiguation_analyzer = None

        if self.config.enable_disambiguation and disambiguation_available:
            disambiguation_config = self.config.disambiguation_config or DisambiguationConfig()  # type: ignore
            self.disambiguation_handler = DisambiguationHandler(disambiguation_config)  # type: ignore
            self.disambiguation_analyzer = DisambiguationAnalyzer(disambiguation_config)  # type: ignore
            logger.debug("Disambiguation components initialized")
        elif self.config.enable_disambiguation and not disambiguation_available:
            logger.warning("Disambiguation requested but components not available - falling back to regular behavior")

    def handler(self, event: dict[str, Any], context: Any) -> dict[str, Any]:
        """
        Primary entry point for the lex_helper library.

        This function is designed to handle AWS Lambda events triggered by Amazon Lex. It processes the incoming
        event and context, and utilizes custom session attributes if provided. The function orchestrates the
        entire flow, including parsing the Lex request, handling intents, managing session state, and formatting
        the response for the channel.

        Args:
            event (dict[str, Any]): The event data from AWS Lambda, typically containing the Lex request.
            context (Any): The context object provided by AWS Lambda, containing runtime information.

        Returns:
            dict[str, Any]: A formatted response ready to be sent back to Amazon Lex.
        """
        print("[FLOW - handler.py - Added by Claude Haiku] === HANDLER ENTRY POINT ===")
        print(f"[FLOW - handler.py - Added by Claude Haiku] Auto exception handling enabled: {self.config.auto_handle_exceptions}")
        
        if self.config.auto_handle_exceptions:
            try:
                print("[FLOW - handler.py - Added by Claude Haiku] Starting auto exception handling")
                return self._handle_request_with_auto_exception_handling(event, context)
            except Exception as e:
                print(f"[ERROR - handler.py - Added by Claude Haiku] Exception caught in handler: {type(e).__name__}: {str(e)}")
                logger.exception("Error processing request")
                # Create a basic LexRequest for error handling
                try:
                    print("[FLOW - handler.py - Added by Claude Haiku] Attempting to parse LexRequest from event")
                    lex_request = LexRequest(**event)
                except Exception as parse_error:
                    print(f"[ERROR - handler.py - Added by Claude Haiku] Failed to parse LexRequest: {type(parse_error).__name__}: {str(parse_error)}")
                    # If we can't even parse the event, create a minimal error response
                    return self._create_minimal_error_response()

                # Use handle_exceptions and format the response
                print("[FLOW - handler.py - Added by Claude Haiku] Handling exceptions and formatting response")
                error_response = handle_exceptions(e, lex_request, error_message=self.config.error_message)
                return format_for_channel(response=error_response, channel_string="lex")
        else:
            print("[FLOW - handler.py - Added by Claude Haiku] Auto exception handling disabled")
            return self._handle_request_with_auto_exception_handling(event, context)

    def _handle_request_with_auto_exception_handling(self, event: dict[str, Any], context: Any) -> dict[str, Any]:
        """Handle request without automatic exception handling (original behavior)."""
        print("[FLOW - handler.py - Added by Claude Haiku] === _handle_request_with_auto_exception_handling START ===")
        logger.debug("Handler starting")
        
        try:
            print("[FLOW - handler.py - Added by Claude Haiku] Initializing session attributes")
            session_attributes: T = self.config.session_attributes
            print(f"[FLOW - handler.py - Added by Claude Haiku] SessionAttributes type: {type(session_attributes)}")
            logger.debug("SessionAttributes type: %s", type(session_attributes))
            
            print("[FLOW - handler.py - Added by Claude Haiku] Parsing Lex request from event")
            lex_payload: LexRequest[T] = parse_lex_request(event, session_attributes)
            print(f"[FLOW - handler.py - Added by Claude Haiku] Lex request parsed successfully. Session ID: {lex_payload.sessionId}")

            # Auto-initialize MessageManager if enabled
            if self.config.auto_initialize_messages:
                print("[FLOW - handler.py - Added by Claude Haiku] Auto-initializing MessageManager")
                self._initialize_message_manager(lex_payload)
            else:
                print("[FLOW - handler.py - Added by Claude Haiku] Auto-initialization of MessageManager disabled")

            print(f"[FLOW - handler.py - Added by Claude Haiku] Processing request - sessionId: {lex_payload.sessionId}, utterance: {lex_payload.inputTranscript}")
            logger.debug(
                "Processing request - sessionId: %s, utterance: %s, sessionAttributes: %s",
                lex_payload.sessionId,
                lex_payload.inputTranscript,
                lex_payload.sessionState.sessionAttributes.model_dump(exclude_none=True),
            )
            
            print("[FLOW - handler.py - Added by Claude Haiku] Calling _main_handler")
            result = self._main_handler(lex_payload)
            print("[FLOW - handler.py - Added by Claude Haiku] === _handle_request_with_auto_exception_handling END (SUCCESS) ===")
            return result
            
        except Exception as e:
            print(f"[ERROR - handler.py - Added by Claude Haiku] Exception in _handle_request_with_auto_exception_handling: {type(e).__name__}: {str(e)}")
            import traceback
            print(f"[ERROR - handler.py - Added by Claude Haiku] Traceback: {traceback.format_exc()}")
            raise

    def _main_handler(self, lex_payload: LexRequest[T]) -> dict[str, Any]:
        """
        Core handler for processing Lex requests.

        This function takes a parsed LexRequest object and manages the flow of handling the request. It determines
        the appropriate intent handler, manages session state, and processes any callbacks. It also handles
        exceptions and formats the final response for the channel.

        Args:
            lex_payload (LexRequest[T]): The parsed Lex request containing session and intent information.

        Returns:
            dict[str, Any]: A formatted response ready to be sent back to Amazon Lex.
        """
        print("[FLOW - handler.py - Added by Claude Haiku] === _main_handler START ===")
        messages: LexMessages = []

        try:
            # Display Intent for Debug Purposes
            print("[FLOW - handler.py - Added by Claude Haiku] Extracting intent from lex_payload")
            lex_intent = get_intent(lex_payload)
            lex_intent_name = lex_intent.name
            print(f"[FLOW - handler.py - Added by Claude Haiku] Intent detected: {lex_intent_name}")
            logger.debug("Lex-Intent: %s", lex_intent_name)

            # Handlers is a list of functions that take a LexRequest and return a LexResponse
            handlers: list[Callable[[LexRequest[T]], LexResponse[T] | None]] = []

            # Add disambiguation handler first if enabled
            if self.disambiguation_handler:
                print("[FLOW - handler.py - Added by Claude Haiku] Adding disambiguation handler")
                handlers.append(self.disambiguation_intent_handler)
            else:
                print("[FLOW - handler.py - Added by Claude Haiku] Disambiguation handler not available or disabled")

            # Add regular intent handler
            print("[FLOW - handler.py - Added by Claude Haiku] Adding regular intent handler")
            handlers.append(self.regular_intent_handler)
            print(f"[FLOW - handler.py - Added by Claude Haiku] Total handlers registered: {len(handlers)}")

            response = None
            for idx, message_handler in enumerate(handlers):
                try:
                    print(f"[FLOW - handler.py - Added by Claude Haiku] Executing handler #{idx + 1}: {message_handler.__name__}")
                    response = message_handler(lex_payload)
                    if response:
                        print(f"[FLOW - handler.py - Added by Claude Haiku] Handler #{idx + 1} returned a response")
                        break
                    else:
                        print(f"[FLOW - handler.py - Added by Claude Haiku] Handler #{idx + 1} returned None, trying next handler")
                except IntentNotFoundError as intent_error:
                    print(f"[ERROR - handler.py - Added by Claude Haiku] IntentNotFoundError in handler #{idx + 1}: {str(intent_error)}")
                    raise
                except Exception as e:
                    print(f"[ERROR - handler.py - Added by Claude Haiku] Exception in handler #{idx + 1}: {type(e).__name__}: {str(e)}")
                    import traceback
                    print(f"[ERROR - handler.py - Added by Claude Haiku] Traceback: {traceback.format_exc()}")
                    logger.exception("Handler failed: %s", e)
                    continue

            if not response:
                print(f"[ERROR - handler.py - Added by Claude Haiku] No handler returned a response for intent: {lex_intent_name}")
                raise ValueError(f"Unable to find handler for intent: {lex_intent_name}")

            print("[FLOW - handler.py - Added by Claude Haiku] Validating response has sessionState")
            if not hasattr(response, "sessionState"):
                print("[ERROR - handler.py - Added by Claude Haiku] Response missing sessionState attribute")
                raise ValueError(f"SessionState not found in response: {response}")

            print("[FLOW - handler.py - Added by Claude Haiku] Updating lex_payload with response data")
            lex_payload.sessionState = response.sessionState
            lex_payload.requestAttributes = response.requestAttributes

            messages: LexMessages = []
            print(f"[FLOW - handler.py - Added by Claude Haiku] Response has {len(response.messages)} messages")
            messages += response.messages
            
            if response.requestAttributes and "callback" in response.requestAttributes:
                print(f"[FLOW - handler.py - Added by Claude Haiku] Callback found in requestAttributes")
                callback_name = response.requestAttributes["callback"]
                print(f"[FLOW - handler.py - Added by Claude Haiku] Executing callback: {callback_name}")
                logger.debug("Callback found: %s", callback_name)
                response.requestAttributes.pop("callback")
                response = call_handler_for_file(
                    intent_name=callback_name, lex_request=lex_payload, package_name=self.config.package_name
                )
                print(f"[FLOW - handler.py - Added by Claude Haiku] Callback returned {len(response.messages)} messages")
                lex_payload.sessionState = response.sessionState
                messages += response.messages
            else:
                print("[FLOW - handler.py - Added by Claude Haiku] No callback found in requestAttributes")
                
            response.messages = messages
            print(f"[FLOW - handler.py - Added by Claude Haiku] Final response has {len(response.messages)} messages")

        except IntentNotFoundError as intent_error:
            print(f"[ERROR - handler.py - Added by Claude Haiku] IntentNotFoundError in _main_handler: {str(intent_error)}")
            raise
        except Exception as e:
            print(f"[ERROR - handler.py - Added by Claude Haiku] Exception in _main_handler: {type(e).__name__}: {str(e)}")
            import traceback
            print(f"[ERROR - handler.py - Added by Claude Haiku] Traceback: {traceback.format_exc()}")
            response = handle_exceptions(e, lex_payload)

        print("[FLOW - handler.py - Added by Claude Haiku] Formatting response for Lex channel")
        formatted_response: dict[str, Any] = {}

        try:
            formatted_response = format_for_channel(response=response, channel_string="lex")
            print("[FLOW - handler.py - Added by Claude Haiku] === _main_handler END (SUCCESS) ===")
            return formatted_response

        except Exception as e:
            print(f"[ERROR - handler.py - Added by Claude Haiku] Exception during format_for_channel: {type(e).__name__}: {str(e)}")
            import traceback
            print(f"[ERROR - handler.py - Added by Claude Haiku] Traceback: {traceback.format_exc()}")
            logger.exception(e)
            raise e

    def disambiguation_intent_handler(self, lex_payload: LexRequest[T]) -> LexResponse[T] | None:
        """
        Handle disambiguation responses and trigger disambiguation when needed.

        This handler processes user responses to disambiguation questions and
        triggers new disambiguation when confidence is low.
        """
        print("[FLOW - handler.py - Added by Claude Haiku] === disambiguation_intent_handler START ===")
        
        try:
            if not self.disambiguation_handler:
                print("[FLOW - handler.py - Added by Claude Haiku] Disambiguation handler not initialized, returning None")
                return None

            # First, check if this is a response to a previous disambiguation
            print("[FLOW - handler.py - Added by Claude Haiku] Processing disambiguation response")
            disambiguation_response = self.disambiguation_handler.process_disambiguation_response(lex_payload)
            if disambiguation_response is not None:
                print("[FLOW - handler.py - Added by Claude Haiku] Disambiguation response processed successfully")
                return disambiguation_response

            # If not a disambiguation response, check if we need to trigger disambiguation
            if self.disambiguation_analyzer:
                print("[FLOW - handler.py - Added by Claude Haiku] Analyzing request for disambiguation trigger")
                # Analyze the request for disambiguation
                analysis_result = self.disambiguation_analyzer.analyze_request(cast(Any, lex_payload))

                if analysis_result.should_disambiguate and analysis_result.candidates:
                    print(f"[FLOW - handler.py - Added by Claude Haiku] Triggering disambiguation with {len(analysis_result.candidates)} candidates")
                    logger.info("Triggering disambiguation with %d candidates", len(analysis_result.candidates))
                    return self.disambiguation_handler.handle_disambiguation(lex_payload, analysis_result.candidates)
                else:
                    print("[FLOW - handler.py - Added by Claude Haiku] No disambiguation needed")

            # No disambiguation needed, let regular handler process
            print("[FLOW - handler.py - Added by Claude Haiku] === disambiguation_intent_handler END (returning None) ===")
            return None
            
        except Exception as e:
            print(f"[ERROR - handler.py - Added by Claude Haiku] Exception in disambiguation_intent_handler: {type(e).__name__}: {str(e)}")
            import traceback
            print(f"[ERROR - handler.py - Added by Claude Haiku] Traceback: {traceback.format_exc()}")
            raise

    def regular_intent_handler(self, lex_payload: LexRequest[T]) -> LexResponse[T] | None:
        """
        Route the incoming request based on intent.
        The JSON body of the request is provided in the event slot.
        """
        print("[FLOW - handler.py - Added by Claude Haiku] === regular_intent_handler START ===")
        
        try:
            print("[FLOW - handler.py - Added by Claude Haiku] Logging lex_payload")
            logger.debug("Payload from Lex: %s", lex_payload)
            
            print("[FLOW - handler.py - Added by Claude Haiku] Extracting intent name")
            intent = get_intent(lex_payload)
            intent_name = intent.name
            print(f"[FLOW - handler.py - Added by Claude Haiku] Intent name: {intent_name}")
            
            print("[FLOW - handler.py - Added by Claude Haiku] Setting lex_intent in session attributes")
            lex_payload.sessionState.sessionAttributes.lex_intent = intent.name

            response: LexResponse[T] | None = None

            print("[FLOW - handler.py - Added by Claude Haiku] Checking for Common_Exit_Feedback intent")
            if not intent_name.__contains__("Common_Exit_Feedback"):
                print("[FLOW - handler.py - Added by Claude Haiku] Setting transition_to_exit context")
                lex_payload.sessionState.activeContexts = [
                    {
                        "name": "transition_to_exit",
                        "contextAttributes": {},
                        "timeToLive": {"timeToLiveInSeconds": 900, "turnsToLive": 20},
                    }
                ]
            else:
                print("[FLOW - handler.py - Added by Claude Haiku] Common_Exit_Feedback intent detected, skipping context setup")

            print("[FLOW - handler.py - Added by Claude Haiku] Checking for unknown slot choices")
            if any_unknown_slot_choices(lex_request=lex_payload):
                print("[FLOW - handler.py - Added by Claude Haiku] Unknown slot choices detected, handling")
                response = handle_any_unknown_slot_choice(lex_request=lex_payload)
            else:
                print("[FLOW - handler.py - Added by Claude Haiku] No unknown slot choices, calling intent handler")
                intent_name = lex_payload.sessionState.intent.name
                print(f"[FLOW - handler.py - Added by Claude Haiku] Calling handler for intent: {intent_name}")
                response = call_handler_for_file(
                    intent_name=intent_name, lex_request=lex_payload, package_name=self.config.package_name
                )
                print(f"[FLOW - handler.py - Added by Claude Haiku] Intent handler returned response with {len(response.messages)} messages")
                
            print("[FLOW - handler.py - Added by Claude Haiku] === regular_intent_handler END (returning response) ===")
            return response
            
        except Exception as e:
            print(f"[ERROR - handler.py - Added by Claude Haiku] Exception in regular_intent_handler: {type(e).__name__}: {str(e)}")
            import traceback
            print(f"[ERROR - handler.py - Added by Claude Haiku] Traceback: {traceback.format_exc()}")
            raise

    def _initialize_message_manager(self, lex_payload: LexRequest[T]) -> None:
        """Initialize MessageManager with locale from the Lex request."""
        print("[FLOW - handler.py - Added by Claude Haiku] === _initialize_message_manager START ===")
        
        try:
            from lex_helper import set_locale

            print("[FLOW - handler.py - Added by Claude Haiku] Extracting locale from lex_payload")
            locale = lex_payload.bot.localeId
            print(f"[FLOW - handler.py - Added by Claude Haiku] Setting locale: {locale}")
            set_locale(locale)
            print("[FLOW - handler.py - Added by Claude Haiku] MessageManager initialized successfully")
            logger.debug("MessageManager initialized for locale: %s", locale)

        except Exception as e:
            print(f"[ERROR - handler.py - Added by Claude Haiku] Failed to initialize MessageManager: {type(e).__name__}: {str(e)}")
            import traceback
            print(f"[ERROR - handler.py - Added by Claude Haiku] Traceback: {traceback.format_exc()}")
            logger.warning("Failed to initialize MessageManager: %s", e)

    def _create_minimal_error_response(self) -> dict[str, Any]:
        """Create a minimal error response when event parsing fails."""
        print("[FLOW - handler.py - Added by Claude Haiku] === _create_minimal_error_response START ===")
        
        try:
            error_message = "I'm sorry, I encountered an error while processing your request. Please try again."

            # Try to get custom error message if configured
            if self.config.error_message:
                print(f"[FLOW - handler.py - Added by Claude Haiku] Custom error message configured: {self.config.error_message}")
                try:
                    from lex_helper import get_message

                    print("[FLOW - handler.py - Added by Claude Haiku] Attempting to get message from key")
                    error_message = get_message(self.config.error_message)
                    print(f"[FLOW - handler.py - Added by Claude Haiku] Message retrieved: {error_message}")
                except Exception as msg_error:
                    # If message key lookup fails, use it as direct string
                    print(f"[FLOW - handler.py - Added by Claude Haiku] Message key lookup failed, using as direct string: {type(msg_error).__name__}: {str(msg_error)}")
                    error_message = self.config.error_message

            print("[FLOW - handler.py - Added by Claude Haiku] Creating minimal error response")
            response = {
                "sessionState": {
                    "dialogAction": {"type": "Close"},
                    "intent": {"name": "FallbackIntent", "state": "Failed"},
                    "sessionAttributes": {},
                },
                "messages": [{"contentType": "PlainText", "content": error_message}],
            }
            print("[FLOW - handler.py - Added by Claude Haiku] === _create_minimal_error_response END (SUCCESS) ===")
            return response
            
        except Exception as e:
            print(f"[ERROR - handler.py - Added by Claude Haiku] Exception in _create_minimal_error_response: {type(e).__name__}: {str(e)}")
            import traceback
            print(f"[ERROR - handler.py - Added by Claude Haiku] Traceback: {traceback.format_exc()}")
            raise
