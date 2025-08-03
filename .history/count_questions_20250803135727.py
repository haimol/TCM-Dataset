#!/usr/bin/env python3
"""
Script to count questions in TCM data files and output summary
"""

import json
import os
from pathlib import Path

def count_questions_in_file(filepath):
    """Count questions in a single JSON file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Skip metadata files
        if filepath.name.endswith('-metadata.json'):
            return 0, "metadata"
        
        if isinstance(data, list):
            # Check if it's the standard extracted format or generated format
            if len(data) > 0:
                first_item = data[0]
                if isinstance(first_item, dict):
                    # Check for different formats
                    if 'query' in first_item and 'choices' in first_item:
                        # Standard extracted format
                        return len(data), "extracted"
                    elif 'generated_question' in first_item:
                        # Generated format
                        return len(data), "generated"
                    elif 'question' in first_item or 'item_id' in first_item:
                        # Other question formats
                        return len(data), "questions"
                    else:
                        # Generic list of objects
                        return len(data), "unknown"
            return 0, "empty"
        else:
            # Not a list, check if it's a single question or other structure
            if isinstance(data, dict):
                if 'query' in data or 'question' in data:
                    return 1, "single"
                else:
                    return 0, "other"
            return 0, "invalid"
            
    except json.JSONDecodeError:
        return 0, "json_error"
    except Exception as e:
        return 0, f"error: {str(e)}"

def main():
    """Main function to process all files and generate report"""
    base_dir = Path('.')
    results = []
    
    # Process both directories
    for directory in ['Extracted-Data', 'Generated-Data']:
        dir_path = base_dir / directory
        if not dir_path.exists():
            print(f"Directory {directory} not found!")
            continue
            
        print(f"Processing {directory}...")
        
        # Get all JSON files in the directory
        json_files = list(dir_path.glob('*.json'))
        json_files.sort()  # Sort for consistent output
        
        for filepath in json_files:
            count, file_type = count_questions_in_file(filepath)
            relative_path = str(filepath.relative_to(base_dir))
            results.append((relative_path, count, file_type))
            print(f"  {filepath.name}: {count} questions ({file_type})")
    
    # Write results to output file
    output_file = 'question_count_summary.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("TCM Question Database Summary\n")
        f.write("=" * 50 + "\n\n")
        
        # Group by directory
        extracted_total = 0
        generated_total = 0
        
        f.write("EXTRACTED DATA:\n")
        f.write("-" * 20 + "\n")
        for filepath, count, file_type in results:
            if filepath.startswith('Extracted-Data'):
                if file_type != 'metadata':
                    f.write(f"{filepath}: {count} questions\n")
                    extracted_total += count
                else:
                    f.write(f"{filepath}: metadata file\n")
        
        f.write(f"\nExtracted Data Subtotal: {extracted_total} questions\n\n")
        
        f.write("GENERATED DATA:\n")
        f.write("-" * 20 + "\n")
        for filepath, count, file_type in results:
            if filepath.startswith('Generated-Data'):
                f.write(f"{filepath}: {count} questions\n")
                generated_total += count
        
        f.write(f"\nGenerated Data Subtotal: {generated_total} questions\n\n")
        
        f.write("SUMMARY:\n")
        f.write("-" * 20 + "\n")
        f.write(f"Total Extracted Questions: {extracted_total}\n")
        f.write(f"Total Generated Questions: {generated_total}\n")
        f.write(f"Grand Total: {extracted_total + generated_total} questions\n")
        
        # Detailed breakdown
        f.write(f"\nDETAILED BREAKDOWN:\n")
        f.write("-" * 30 + "\n")
        for filepath, count, file_type in results:
            f.write(f"{filepath:<60} {count:>8} ({file_type})\n")
    
    print(f"\nResults written to: {output_file}")
    print(f"Total questions found: {extracted_total + generated_total}")

if __name__ == "__main__":
    main() 