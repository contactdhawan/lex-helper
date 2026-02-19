# Debug Print Statements Summary

## Overview
Comprehensive print statements have been added to the lex-helper library to help you understand the flow of execution and catch any errors. All print statements include:
- **Filename** - Source of the print statement
- **Log Level** - Either `[FLOW - ...]` for normal execution or `[ERROR - ...]` for exceptions
- **Attribution** - "Added by Claude Haiku" to identify the debug statements
- **Full Tracebacks** - Complete exception details with traceback information

## Files Modified

### 1. `lex_helper/core/handler.py` ✅
**Methods with print statements:**

#### `handler(event, context)`
- Entry point logging
- Auto exception handling status check
- Exception catching with full traceback
- Event parsing attempts
- Error response creation

#### `_handle_request_with_auto_exception_handling(event, context)`
- Session attributes initialization
- Lex request parsing with session ID logging
- MessageManager initialization status
- Request processing with utterance logging
- Call to _main_handler with status tracking

#### `_main_handler(lex_payload)`
- Intent extraction and detection
- Handler registration (disambiguation + regular handlers)
- Handler execution with individual status tracking
- Handler response validation
- SessionState validation
- Callback detection and execution
- Message counting and formatting
- Channel formatting with exception handling

#### `disambiguation_intent_handler(lex_payload)`
- Handler initialization check
- Disambiguation response processing
- Request analysis for disambiguation triggers
- Candidate count logging
- Flow control decisions

#### `regular_intent_handler(lex_payload)`
- Intent extraction and logging
- Session attributes setting
- Context setup decisions (Common_Exit_Feedback check)
- Slot choice validation
- Intent handler invocation
- Response message counting

#### `_initialize_message_manager(lex_payload)`
- Locale extraction
- MessageManager setup
- Error handling for initialization failures

#### `_create_minimal_error_response()`
- Custom error message configuration
- Message key lookup attempts
- Minimal error response creation

---

### 2. `lex_helper/channels/channel_formatting.py` ✅
**Functions with print statements:**

#### `format_for_channel(response, channel_string)`
- Channel parameter logging
- Message count tracking
- Channel instance creation
- Individual message formatting with type identification
- Formatter lookup and execution
- ImageResponseCard special handling
- Options management
- Session attribute stringification
- Full response dumping

**Print Statement Pattern:**
```
[FLOW - channel_formatting.py - Added by Claude Haiku] Response has X messages to format
[FLOW - channel_formatting.py - Added by Claude Haiku] Getting channel for: lex
[FLOW - channel_formatting.py - Added by Claude Haiku] Processing message #1: LexPlainText
```

---

### 3. `lex_helper/channels/lex.py` ✅
**Methods with print statements:**

#### `format_message(message)`
- Message type identification
- Type-specific formatting routing
- Unsupported type handling

#### `format_messages(messages)`
- Message list processing
- Individual message formatting
- Result count tracking

**Print Statement Pattern:**
```
[FLOW - lex.py - Added by Claude Haiku] format_message called with type: LexPlainText
[FLOW - lex.py - Added by Claude Haiku] Formatted 3 messages successfully
```

---

### 4. `lex_helper/core/dialog.py` ✅
**Functions with print statements:**

#### `get_sentiment(lex_request)`
- Interpretations availability check
- Interpretation count logging
- Sentiment response detection
- Sentiment value extraction

**Print Statement Pattern:**
```
[FLOW - dialog.py - Added by Claude Haiku] get_sentiment called
[FLOW - dialog.py - Added by Claude Haiku] Found 2 interpretations
[FLOW - dialog.py - Added by Claude Haiku] Sentiment found: POSITIVE
```

---

### 5. `lex_helper/core/call_handler_for_file.py` ✅
**Functions with print statements:**

#### `call_handler_for_file(intent_name, lex_request, package_name)`
- Intent name parameter logging
- Package name defaulting
- Module path determination
- Module import attempts with error details
- Handler function lookup
- Handler invocation
- Result message counting
- Exception handling for all stages

**Print Statement Pattern:**
```
[FLOW - call_handler_for_file.py - Added by Claude Haiku] === call_handler_for_file START (intent: BookingIntent) ===
[FLOW - call_handler_for_file.py - Added by Claude Haiku] Module path: fulfillment_function.intents.booking_intent
[FLOW - call_handler_for_file.py - Added by Claude Haiku] Handler function found
[FLOW - call_handler_for_file.py - Added by Claude Haiku] Handler function returned successfully with 2 messages
[FLOW - call_handler_for_file.py - Added by Claude Haiku] === call_handler_for_file END (SUCCESS) ===
```

---

## Print Statement Format

### Flow Messages (Normal Execution)
```
[FLOW - {filename} - Added by Claude Haiku] {detailed message}
```

### Error Messages (Exceptions)
```
[ERROR - {filename} - Added by Claude Haiku] {error type and message}
[ERROR - {filename} - Added by Claude Haiku] Traceback: {full traceback}
```

### Markers for Flow Tracking
```
[FLOW - {filename} - Added by Claude Haiku] === {function_name} START ===
[FLOW - {filename} - Added by Claude Haiku] === {function_name} END (SUCCESS) ===
```

---

## How to Use These Debug Statements

### 1. **CloudWatch Logs (Lambda)**
When running on AWS Lambda, all print statements appear in CloudWatch logs:
```
[FLOW - handler.py - Added by Claude Haiku] === HANDLER ENTRY POINT ===
[FLOW - handler.py - Added by Claude Haiku] Auto exception handling enabled: True
[FLOW - handler.py - Added by Claude Haiku] Starting auto exception handling
[FLOW - handler.py - Added by Claude Haiku] === _handle_request_with_auto_exception_handling START ===
...
```

### 2. **Local Testing**
When testing locally, redirect stdout to see the messages:
```python
import sys
sys.stdout.flush()
```

### 3. **Filtering by Filename**
Search CloudWatch for specific modules:
```
fields @timestamp, @message
| filter @message like /handler.py/
| sort @timestamp desc
```

### 4. **Filtering by Log Level**
Find errors quickly:
```
fields @timestamp, @message
| filter @message like /ERROR/
| sort @timestamp desc
```

### 5. **Tracking Flow**
Follow the flow from start to end:
```
fields @timestamp, @message
| filter @message like /START|END/
| sort @timestamp
```

---

## Key Information Captured

✅ **Execution Flow**
- What function was called
- In what order functions are executing
- What parameters were passed
- What values were returned

✅ **Data Transformations**
- Message types being processed
- Channel selections
- Session attributes changes
- Intent routing decisions

✅ **Error Details**
- Full exception types
- Exception messages
- Complete Python tracebacks
- Error location and context

✅ **Performance Insights**
- Message counts at each stage
- Handler execution attempts
- Number of interpretations/candidates
- Formatter selection

---

## Sample Log Output

```
[FLOW - handler.py - Added by Claude Haiku] === HANDLER ENTRY POINT ===
[FLOW - handler.py - Added by Claude Haiku] Auto exception handling enabled: True
[FLOW - handler.py - Added by Claude Haiku] Starting auto exception handling
[FLOW - handler.py - Added by Claude Haiku] === _handle_request_with_auto_exception_handling START ===
[FLOW - handler.py - Added by Claude Haiku] Initializing session attributes
[FLOW - handler.py - Added by Claude Haiku] SessionAttributes type: <class 'fulfillment_function.models.session_attributes.SessionAttributes'>
[FLOW - handler.py - Added by Claude Haiku] Parsing Lex request from event
[FLOW - handler.py - Added by Claude Haiku] Lex request parsed successfully. Session ID: 1a2b3c4d-5e6f-7g8h-9i0j-k1l2m3n4o5p6
[FLOW - handler.py - Added by Claude Haiku] Auto-initializing MessageManager
[FLOW - handler.py - Added by Claude Haiku] Processing request - sessionId: 1a2b3c4d-5e6f-7g8h-9i0j-k1l2m3n4o5p6, utterance: book me a flight
[FLOW - handler.py - Added by Claude Haiku] Calling _main_handler
[FLOW - handler.py - Added by Claude Haiku] === _main_handler START ===
[FLOW - handler.py - Added by Claude Haiku] Extracting intent from lex_payload
[FLOW - handler.py - Added by Claude Haiku] Intent detected: BookingIntent
[FLOW - handler.py - Added by Claude Haiku] Adding regular intent handler
[FLOW - handler.py - Added by Claude Haiku] Total handlers registered: 1
[FLOW - handler.py - Added by Claude Haiku] Executing handler #1: regular_intent_handler
[FLOW - handler.py - Added by Claude Haiku] === regular_intent_handler START ===
[FLOW - handler.py - Added by Claude Haiku] Extracting intent name
[FLOW - handler.py - Added by Claude Haiku] Intent name: BookingIntent
[FLOW - handler.py - Added by Claude Haiku] Setting lex_intent in session attributes
[FLOW - handler.py - Added by Claude Haiku] Checking for Common_Exit_Feedback intent
[FLOW - handler.py - Added by Claude Haiku] Setting transition_to_exit context
[FLOW - handler.py - Added by Claude Haiku] Checking for unknown slot choices
[FLOW - handler.py - Added by Claude Haiku] No unknown slot choices, calling intent handler
[FLOW - handler.py - Added by Claude Haiku] Calling handler for intent: BookingIntent
[FLOW - call_handler_for_file.py - Added by Claude Haiku] === call_handler_for_file START (intent: BookingIntent) ===
[FLOW - call_handler_for_file.py - Added by Claude Haiku] No package name provided, using default: fulfillment_function
[FLOW - call_handler_for_file.py - Added by Claude Haiku] Determining file to import for intent: BookingIntent
[FLOW - call_handler_for_file.py - Added by Claude Haiku] Converting title to snake case: booking_intent
[FLOW - call_handler_for_file.py - Added by Claude Haiku] Module path: fulfillment_function.intents.booking_intent
[FLOW - call_handler_for_file.py - Added by Claude Haiku] Importing module: fulfillment_function.intents.booking_intent
[FLOW - call_handler_for_file.py - Added by Claude Haiku] Module imported successfully
[FLOW - call_handler_for_file.py - Added by Claude Haiku] Looking for handler function in module
[FLOW - call_handler_for_file.py - Added by Claude Haiku] Handler function found
[FLOW - call_handler_for_file.py - Added by Claude Haiku] Calling handler function
[FLOW - call_handler_for_file.py - Added by Claude Haiku] Handler function returned successfully with 2 messages
[FLOW - call_handler_for_file.py - Added by Claude Haiku] === call_handler_for_file END (SUCCESS) ===
[FLOW - handler.py - Added by Claude Haiku] Intent handler returned response with 2 messages
[FLOW - handler.py - Added by Claude Haiku] === regular_intent_handler END (returning response) ===
[FLOW - handler.py - Added by Claude Haiku] Handler #1 returned a response
[FLOW - handler.py - Added by Claude Haiku] Validating response has sessionState
[FLOW - handler.py - Added by Claude Haiku] Updating lex_payload with response data
[FLOW - handler.py - Added by Claude Haiku] Response has 2 messages
[FLOW - handler.py - Added by Claude Haiku] No callback found in requestAttributes
[FLOW - handler.py - Added by Claude Haiku] Final response has 2 messages
[FLOW - handler.py - Added by Claude Haiku] Formatting response for Lex channel
[FLOW - channel_formatting.py - Added by Claude Haiku] === format_for_channel START (channel: lex) ===
[FLOW - channel_formatting.py - Added by Claude Haiku] Response has 2 messages to format
[FLOW - channel_formatting.py - Added by Claude Haiku] Getting channel for: lex
[FLOW - channel_formatting.py - Added by Claude Haiku] Channel type: LexChannel
[FLOW - channel_formatting.py - Added by Claude Haiku] Processing 2 messages
[FLOW - channel_formatting.py - Added by Claude Haiku] Processing message #1: LexPlainText
[FLOW - lex.py - Added by Claude Haiku] format_message called with type: LexPlainText
[FLOW - lex.py - Added by Claude Haiku] Message is LexPlainText, formatting...
[FLOW - channel_formatting.py - Added by Claude Haiku] Message #1 formatted successfully
[FLOW - channel_formatting.py - Added by Claude Haiku] Processing message #2: LexCustomPayload
[FLOW - lex.py - Added by Claude Haiku] format_message called with type: LexCustomPayload
[FLOW - lex.py - Added by Claude Haiku] Message is LexCustomPayload, formatting...
[FLOW - channel_formatting.py - Added by Claude Haiku] Message #2 formatted successfully
[FLOW - channel_formatting.py - Added by Claude Haiku] Checking for imageResponseCard special handling
[FLOW - channel_formatting.py - Added by Claude Haiku] Dumping response and stringifying session attributes
[FLOW - channel_formatting.py - Added by Claude Haiku] === format_for_channel END (SUCCESS) ===
dumped_response {...}
[FLOW - handler.py - Added by Claude Haiku] === _main_handler END (SUCCESS) ===
[FLOW - handler.py - Added by Claude Haiku] === _handle_request_with_auto_exception_handling END (SUCCESS) ===
```

---

## Notes

- All print statements go to **stdout** which is captured by CloudWatch Logs on Lambda
- The filename helps identify which module is executing
- The "Added by Claude Haiku" attribution makes it easy to identify debug statements vs. application logs
- Error messages include full Python tracebacks for complete debugging information
- Markers like `=== START ===` and `=== END ===` make flow tracking easy

---

**Last Updated:** February 19, 2026
**Version:** 1.0
