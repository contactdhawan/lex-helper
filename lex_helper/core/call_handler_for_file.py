# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import importlib
import inspect
import logging
from typing import TypeVar

from lex_helper.core.types import LexRequest, LexResponse, SessionAttributes
from lex_helper.exceptions.handlers import IntentNotFoundError, handle_exceptions
from lex_helper.utils.string import title_to_snake

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=SessionAttributes)


def call_handler_for_file[T: SessionAttributes](
    intent_name: str, lex_request: LexRequest[T], package_name: str | None = None
) -> LexResponse[T]:
    print(f"[FLOW - call_handler_for_file.py - Added by Claude Haiku] === call_handler_for_file START (intent: {intent_name}) ===")
    
    try:
        if package_name is None:
            package_name = "fulfillment_function"
            print(f"[FLOW - call_handler_for_file.py - Added by Claude Haiku] No package name provided, using default: {package_name}")
        else:
            print(f"[FLOW - call_handler_for_file.py - Added by Claude Haiku] Package name: {package_name}")
            
        # Determine the file to import based on intent_name
        print(f"[FLOW - call_handler_for_file.py - Added by Claude Haiku] Determining file to import for intent: {intent_name}")
        logger.debug("Calling handler for %s", intent_name)

        if "_" in intent_name:
            file_to_import = intent_name.lower()
            print(f"[FLOW - call_handler_for_file.py - Added by Claude Haiku] Intent contains underscore, using lowercase: {file_to_import}")
        else:
            file_to_import = title_to_snake(intent_name)
            print(f"[FLOW - call_handler_for_file.py - Added by Claude Haiku] Converting title to snake case: {file_to_import}")

        # Prepend the module path with 'fulfillment_function.'
        file_to_import = f"{package_name}.intents.{file_to_import}"
        print(f"[FLOW - call_handler_for_file.py - Added by Claude Haiku] Module path: {file_to_import}")

        try:
            print(f"[FLOW - call_handler_for_file.py - Added by Claude Haiku] Importing module: {file_to_import}")
            module = importlib.import_module(file_to_import)
            print(f"[FLOW - call_handler_for_file.py - Added by Claude Haiku] Module imported successfully")
        except ImportError as e:
            print(f"[ERROR - call_handler_for_file.py - Added by Claude Haiku] Failed to import module {file_to_import}: {str(e)}")
            logger.exception('Error: Import module %s failed due to the error "%s"', file_to_import, e)
            raise IntentNotFoundError("Unable to find handler for intent") from e

        # Get the "handler" function from the module
        print(f"[FLOW - call_handler_for_file.py - Added by Claude Haiku] Looking for handler function in module")
        if hasattr(module, "handler") and inspect.isfunction(module.handler):
            handler_func = module.handler
            print(f"[FLOW - call_handler_for_file.py - Added by Claude Haiku] Handler function found")
        else:
            print(f"[ERROR - call_handler_for_file.py - Added by Claude Haiku] Handler function not found in {file_to_import}")
            logger.error("Error: Unable to load handler, %s.py does not have a 'handler' function.", file_to_import)
            raise ValueError(f"Error: Unable to load handler, {file_to_import}.py does not have a 'handler' function.")

        # Call the "handler" function with event and context arguments
        print(f"[FLOW - call_handler_for_file.py - Added by Claude Haiku] Calling handler function")
        try:
            result = handler_func(lex_request)
            print(f"[FLOW - call_handler_for_file.py - Added by Claude Haiku] Handler function returned successfully with {len(result.messages)} messages")
            print(f"[FLOW - call_handler_for_file.py - Added by Claude Haiku] === call_handler_for_file END (SUCCESS) ===")
            return result
        except Exception as e:
            print(f"[ERROR - call_handler_for_file.py - Added by Claude Haiku] Handler function raised exception: {type(e).__name__}: {str(e)}")
            import traceback
            print(f"[ERROR - call_handler_for_file.py - Added by Claude Haiku] Traceback: {traceback.format_exc()}")
            raise
            
    except IntentNotFoundError:
        print(f"[ERROR - call_handler_for_file.py - Added by Claude Haiku] Intent not found for: {intent_name}")
        raise
    except Exception as e:
        print(f"[ERROR - call_handler_for_file.py - Added by Claude Haiku] Exception in call_handler_for_file: {type(e).__name__}: {str(e)}")
        import traceback
        print(f"[ERROR - call_handler_for_file.py - Added by Claude Haiku] Traceback: {traceback.format_exc()}")
        return handle_exceptions(e, lex_request)
