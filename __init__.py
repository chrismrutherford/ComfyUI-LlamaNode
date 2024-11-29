# __init__.py

from .llama_node import LlamaNode, TextInputNode, TextOutputNode, ChunkInputNode, LoopController, IntegerComparisonNode, RegexMatchNode, ConditionalRouterNode, TextSplitterNode, ImageLoaderNode

# A dictionary that contains all nodes you want to export with their names
# NOTE: names should be globally unique
NODE_CLASS_MAPPINGS = {
    "LlamaNode": LlamaNode,
    "TextInputNode": TextInputNode,
    "TextOutputNode": TextOutputNode,
    "ChunkInputNode": ChunkInputNode,
    "LoopController": LoopController,
    "IntegerComparisonNode": IntegerComparisonNode,
    "RegexMatchNode": RegexMatchNode,
    "ConditionalRouterNode": ConditionalRouterNode,
    "TextSplitterNode": TextSplitterNode,
    "ImageLoaderNode": ImageLoaderNode
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
    "TextSplitterNode": "Text Splitter",
    "ImageLoaderNode": "Image Loader",
    "TextFindReplaceNode": "Text Find & Replace"
}
