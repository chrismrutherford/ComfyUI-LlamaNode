from .LlamaCppApi import LlamaCppApi
import os
import hashlib
import re

class ChunkInputNode:
    def __init__(self):
        self.file_path = None
        self.file = None

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "file_path": ("STRING", {"default": "input.txt"}),
                "chunk_to_read": ("INT", {"default": 0, "min": 0, "max": 1000000})
            }
        }
    
    RETURN_TYPES = ("STRING", "BOOLEAN")
    FUNCTION = "read_specific_paragraph"
    CATEGORY = "LlamaApi"

    def read_specific_paragraph(self, file_path, chunk_to_read):
        print(f"Reading chunk {chunk_to_read} from {file_path}")
        if not self.file_path or self.file_path != file_path:
            self.file_path = file_path
            if self.file:
                self.file.close()
            if not os.path.exists(self.file_path):
                return ("File not found", False)
            self.file = open(self.file_path, 'r')

        self.file.seek(0)
        current_chunk = 0
        paragraph = []
        more_chunks = True

        for line in self.file:
            if line.strip():
                paragraph.append(line)
            elif paragraph:
                if current_chunk == chunk_to_read:
                    return (''.join(paragraph), True)
                current_chunk += 1
                paragraph = []

        if paragraph and current_chunk == chunk_to_read:
            return (''.join(paragraph), True)
        elif current_chunk < chunk_to_read:
            more_chunks = False
            return ("End of file reached", False)
        else:
            return ("Chunk not found", False)

class TextInputNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "Enter your text here..."})
            }
        }
    
    RETURN_TYPES = ("STRING",)
    FUNCTION = "output_text"
    CATEGORY = "LlamaApi"

    def output_text(self, text):
        return (text,)

class TextOutputNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True})
            }
        }
    
    RETURN_TYPES = ()
    FUNCTION = "display_text"
    CATEGORY = "LlamaApi"

    def display_text(self, text):
        print(f"Text Output: {text}")
        return ()

class LlamaNode:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "A world without prompts"
                }),
                "api_url": ("STRING", {
                    "multiline": False,
                    "default": "http://127.0.0.1:8080"
                }),
                "temperature": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "round": 0.01,
                    "display": "number"
                }),
                "sys_prefix": ("STRING", {
                    "multiline": True,
                    "default": "You are a prompt generation AI. your task is to take a user input for a stable difusion prompt and output and expand the supplied prompt in a stable difusion format to provide better output. Do not deviate from the format. Do not output anything other than a stable diffusion prompt."
                }),
                "stop": ("STRING", {
                    "multiline": False,
                    "default": "</s>"
                }),
                "max_tokens": ("INT", {
                        "default": 8192,
                        "min": -1, 
                        "max": 8192,
                        "display": "number"
                }),
                "seed": ("INT", {
                        "default": 0,
                        "min": 0, 
                        "max": 0xffffffffffffffff
                })
            }
        }

    RETURN_TYPES = ("STRING",)

    FUNCTION = "get_completion"

    CATEGORY = "LlamaApi"

    def get_completion(self, prompt, api_url, temperature, sys_prefix, stop, max_tokens, seed):
        try:
            print("Call request", api_url)
            client = LlamaCppApi(base_url=api_url)

            full_prompt = f"<s>[INST] {sys_prefix}\n\n{prompt} [/INST]"
            options = {
                "temperature": temperature,
                "n_predict": max_tokens,
                "stop": [stop, "</s>"],
                "seed": seed,
                "cache_prompt": True
            }

            response = client.post_completion(full_prompt, options=options)

            print("Call response",response)
            
            if response and response.status_code == 200:
                return (response.json()['content'],)
            else:
                error_message = f"Error: API request failed with status code {response.status_code if response else 'N/A'}"
                print(error_message)
                return ("Bad Panda",)

        except Exception as e:
            error_message = f"Error: {str(e)}"
            print(error_message)
            return ("Bad Panda",)

class LoopController:
    current_iteration = 0

    def __init__(self):
        self.max_iterations = 0

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "max_iterations": ("INT", {"default": 10, "min": 1, "max": 100}),
                "run": ("BOOLEAN", {"default": False}),
            }
        }
    
    RETURN_TYPES = ("INT", "BOOLEAN")
    FUNCTION = "control_loop"
    CATEGORY = "LlamaApi"

    def control_loop(self, max_iterations, run):
        self.max_iterations = max_iterations

        if run:
            self.__class__.current_iteration += 1
            continue_loop = self.__class__.current_iteration < self.max_iterations
            return (self.__class__.current_iteration, continue_loop)
        else:
            self.__class__.current_iteration = 0
            return (self.__class__.current_iteration, False)
    @classmethod
    def IS_CHANGED(cls, max_iterations, **kwargs):
        if cls.current_iteration >= max_iterations:
            return "loop_completed"
        m = hashlib.sha256()
        m.update(str(cls.current_iteration).encode())
        return m.digest().hex()

class IntegerComparisonNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_string": ("STRING", {"multiline": False}),
                "comparison_value": ("INT", {"default": 0, "min": -1000000, "max": 1000000}),
            }
        }
    
    RETURN_TYPES = ("BOOLEAN", "BOOLEAN", "BOOLEAN")
    RETURN_NAMES = ("is_greater_or_equal", "is_less", "error")
    FUNCTION = "compare_integer"
    CATEGORY = "LlamaApi"

    def compare_integer(self, input_string, comparison_value):
        # Remove non-numeric characters, keeping minus sign for negative numbers
        cleaned_input = ''.join(char for char in input_string if char.isdigit() or char == '-')
        cleaned_input = cleaned_input.lstrip('-+')  # Remove leading + or - signs
        
        if not cleaned_input:
            print(f"Error: No valid numeric data in '{input_string}'.")
            return (False, False, True)
        
        try:
            input_int = int(cleaned_input)
            is_greater_or_equal = input_int >= comparison_value
            is_less = input_int < comparison_value
            return (is_greater_or_equal, is_less, False)
        except ValueError:
            print(f"Error: Unable to convert '{cleaned_input}' to an integer.")
            return (False, False, True)

class RegexMatchNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_string": ("STRING", {"multiline": True}),
                "regex_pattern": ("STRING", {"multiline": False, "default": ".*"}),
            }
        }
    
    RETURN_TYPES = ("BOOLEAN", "BOOLEAN")
    FUNCTION = "match_regex"
    CATEGORY = "LlamaApi"

    def match_regex(self, input_string, regex_pattern):
        try:
            match = re.search(regex_pattern, input_string)
            is_match = bool(match)
            is_no_match = not is_match
            return (is_match, is_no_match)
        except re.error as e:
            print(f"Error: Invalid regular expression pattern - {str(e)}")
            return (False, False)

# A dictionary that contains all nodes you want to export with their names
# NOTE: names should be globally unique
NODE_CLASS_MAPPINGS = {
    "LlamaNode": LlamaNode,
    "TextInputNode": TextInputNode,
    "TextOutputNode": TextOutputNode,
    "ChunkInputNode": ChunkInputNode,
    "LoopController": LoopController,
    "IntegerComparisonNode": IntegerComparisonNode,
    "RegexMatchNode": RegexMatchNode
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "LlamaNode": "Llama Node",
    "TextInputNode": "Text Input",
    "TextOutputNode": "Text Output",
    "ChunkInputNode": "Chunk Input",
    "LoopController": "Loop Controller",
    "IntegerComparisonNode": "Integer Comparison",
    "RegexMatchNode": "Regex Match",
    "ConditionalRouterNode": "Conditional Router",
    "TextSplitterNode": "Text Splitter"
}

class ConditionalRouterNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True}),
                "condition": ("BOOLEAN", {"default": True}),
            }
        }
    
    RETURN_TYPES = ("STRING", "BOOLEAN")
    RETURN_NAMES = ("output_text", "continue_pipeline")
    FUNCTION = "route"
    CATEGORY = "LlamaApi"

    def route(self, text, condition):
        if condition:
            return (text, True)  # Continue pipeline
        else:
            return ("", False)  # Stop pipeline

class TextSplitterNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_text": ("STRING", {"multiline": True}),
                "delimiter_1": ("STRING", {"default": ""}),
                "delimiter_2": ("STRING", {"default": ""}),
                "delimiter_3": ("STRING", {"default": ""}),
                "delimiter_4": ("STRING", {"default": ""}),
                "delimiter_5": ("STRING", {"default": ""}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("output_1", "output_2", "output_3", "output_4", "output_5")
    FUNCTION = "split_text"
    CATEGORY = "LlamaApi"

    def split_text(self, input_text, delimiter_1, delimiter_2, delimiter_3, delimiter_4, delimiter_5):
        delimiters = [d for d in [delimiter_1, delimiter_2, delimiter_3, delimiter_4, delimiter_5] if d]
        outputs = []
        remaining_text = input_text

        for i, delimiter in enumerate(delimiters):
            if delimiter in remaining_text:
                parts = remaining_text.split(delimiter, 1)
                outputs.append(parts[0].strip())
                remaining_text = parts[1].strip()
            else:
                outputs.append(remaining_text)
                remaining_text = ""

        # Add any remaining text to the last output
        if remaining_text:
            outputs.append(remaining_text)

        # Ensure we always return exactly 5 outputs
        outputs = outputs[:5]  # Truncate if we have more than 5
        while len(outputs) < 5:
            outputs.append("")  # Pad with empty strings if we have less than 5

        return tuple(outputs)

# Update NODE_CLASS_MAPPINGS
NODE_CLASS_MAPPINGS["ConditionalRouterNode"] = ConditionalRouterNode
NODE_CLASS_MAPPINGS["TextSplitterNode"] = TextSplitterNode

