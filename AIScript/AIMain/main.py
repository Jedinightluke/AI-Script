

import json
import os
import re
import sys
import readline

import google.generativeai as genai
import pyperclip as clipboard
from google.api_core import exceptions

def format_text(text: str) -> str:
    
    
    patterns = {
        # code snippet
        r"```(?P<content>.*?)```": ["", ""],
        # bold_italic
        r"\*\*\*(?P<content>.*?)\*\*\*": ["", ""],
        # bold
        r"\*\*(?P<content>.*?)\*\*": ["", ""],
        # italic
        r"\*(?P<content>.*?)\*": ["", ""],
        # headings
        r"^#{1,6}(?P<content>.*)": ["#", ""],
        # unordered lists
        r"^\* (?P<content>.*?)": ["•", ""],
        # strikethrough
        r"\~\~(?P<content>.*?)\~\~": ["", ""],
        # code
        r"\s\`(?P<content>.*?)\`\s": ["", ""],
    }

    for key, value in patterns.items():
        matches = re.finditer(key, text, re.MULTILINE)

        for match in matches:
            formatted_text = value[0] + match.group("content") + value[1]
            text = text.replace(match.group(0), formatted_text)

    return text

def initialize_genai():
    

    try:
        script_dir = os.path.dirname(os.path.realpath(__file__))
        file = os.path.join(script_dir, "keys.json")

        with open(file, "r", encoding="utf-8") as f:
            content = json.load(f)
            gemini_api_key = content["GEMINI_API_KEY"]

            if gemini_api_key == "your gemini api key here":
                print("To use the Gemini API, you'll need an API key.")
                print("Create a key in Google AI Studio.")
                print("Save the key to 'keys.json' file.")

                sys.exit(1)

            gemini_model = content["GEMINI_MODEL"]
            safety_settings = content["SAFETY_SETTINGS"]
            generation_config = content["GENERATION_CONFIG"]

            genai.configure(api_key=gemini_api_key)

    except FileNotFoundError:
        print("Could not find the configuration file 'keys.json'. Ensure it exists")
        sys.exit(1)

    except json.JSONDecodeError:
        print("Error: Could not parse the key file 'keys.json'. Please check the file format.")
        sys.exit(1)

    except KeyError as e:
        print(f"Error: Missing key '{e.args[0]}' in 'keys.json' file.")
        sys.exit(1)

    model = genai.GenerativeModel(
        model_name=gemini_model,
        safety_settings=safety_settings,
        generation_config=generation_config,
    )

    return model

def text_to_text():
    """Input: text  ->  output: text"""
    print("You are using Text-to-Text(T2T) Model.")
    model = initialize_genai()
    chat = model.start_chat(history=[])

    while True:
        query = input("Ask Me: ")

        if query == "" or query.isspace():
            print("The query is empty.\n")
            continue

        try:
            response = chat.send_message(query, stream=False)
            print("Response: ")
            print(format_text(response.text))

        except exceptions.DeadlineExceeded as error:
            print("Deadline exceeded (Internet connection could be lost)")
            print(error.message, "\n")
            continue

        except exceptions.InvalidArgument as error:
            print("Request fails API validation or you tried to access a model that requires allowlisting.")
            print(error.message, "\n")
            sys.exit(1)

        except exceptions.PermissionDenied as error:
            print("Client doesn't have sufficient permission to call the API.")
            print(error.message, "\n")
            sys.exit(1)

        except exceptions.NotFound as error:
            print("No valid object is found from the designated URL.")
            print(error.message, "\n")
            sys.exit(1)

        except exceptions.ResourceExhausted as error:
            print("API quota over the limit or server overload.")
            print(error.message, "\n")
            sys.exit(1)

        except exceptions.Unknown as error:
            print("Server error due to overload or dependency failure.")
            print(error.message, "\n")
            sys.exit(1)

        except exceptions.ServiceUnavailable as error:
            print("Service is temporarily unavailable.")
            print(error.message, "\n")
            sys.exit(1)

def main():
    """Main logic of the script."""
    os.system("clear -x")

    if len(sys.argv) > 1:
        print(f"Error: Unknown argument: {sys.argv[1]}")
        sys.exit(1)

    text_to_text()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Good Bye")
        sys.exit(0)
