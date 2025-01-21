# Regex JSON Processor

A Python package for processing regex patterns and converting results to JSON format.

## Installation
```pip install regex-json-processor```

## Usage
```python
from regex_json_processor import process_patterns_to_json

patterns = [
    ["example", r"pattern.*"],
    {"allow_multiple": True}
]
result = process_patterns_to_json(patterns, "your text here")