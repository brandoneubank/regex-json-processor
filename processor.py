from typing import List, Optional, Union
import json
import re
from regex_processor import RegexProcessor

def process_patterns_to_json(
    all_patterns: List[List[Union[str, dict]]],
    input_text: str,
    verbose: bool = False
) -> str:
    """
    Process multiple pattern sets and create JSON output with rule-level options for multiple matches.
    
    Args:
        all_patterns: List of pattern sets, where each set contains a name, patterns, 
                      and optionally a dictionary with rule-level options (e.g., allow_multiple).
        input_text: Text to process.
        verbose: Enable verbose output from RegexProcessor.
    
    Returns:
        A JSON string containing the processed results.
    
    Raises:
        ValueError: If a pattern returns multiple matches and allow_multiple is False.
    """
    results = {}
    
    def filter_results(matches, ranges):
        """
        Filter matches based on the result_ranges parameter.
        """
        if not ranges:
            return matches  # No filtering, include all results
        
        # Parse ranges (e.g., [+3-6,-10-12])
        include = set()
        exclude = set()
        for range_str in re.findall(r'([+-])(\d+)-(\d+)', ranges):
            sign, start, end = range_str
            indices = set(range(int(start) - 1, int(end)))  # Convert to 0-based indexing
            if sign == '+':
                include.update(indices)
            elif sign == '-':
                exclude.update(indices)
        
        if include:
            matches = [match for i, match in enumerate(matches) if i in include]
        if exclude:
            matches = [match for i, match in enumerate(matches) if i not in exclude]
        
        return matches
    
    for pattern_set in all_patterns:
        # Extract rule name and patterns
        json_name = pattern_set[0]
        patterns = pattern_set[1:-1] if isinstance(pattern_set[-1], dict) else pattern_set[1:]
        
        # Extract rule-level options (if provided)
        options = pattern_set[-1] if isinstance(pattern_set[-1], dict) else {}
        allow_multiple = options.get("allow_multiple", False)  # Default: False
        result_ranges = options.get("result_ranges", None)  # Default: all results
        
        if verbose:
            print(f"\nProcessing pattern set for: {json_name}")
        
        # Process patterns using RegexProcessor
        processor = RegexProcessor(patterns)
        matches = processor.process_text(input_text, verbose)
        
        # Apply result range filtering
        matches = filter_results(matches, result_ranges)
        
        # Check for multiple matches
        if len(matches) > 1 and not allow_multiple:
            raise ValueError(
                f"Pattern set '{json_name}' returned multiple matches, "
                f"but 'allow_multiple' is set to False."
            )
        
        # Add results to JSON
        if len(matches) == 1:
            results[json_name] = matches[0]
        elif len(matches) > 1:
            results[json_name] = matches  # Always return a flat list for multiple matches
    
    # Convert results to JSON string
    json_result = json.dumps(results, indent=2)
    
    if verbose:
        print(f"\nGenerated JSON:\n{json_result}")
    
    return json_result