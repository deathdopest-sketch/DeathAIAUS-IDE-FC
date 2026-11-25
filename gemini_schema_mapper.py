#!/usr/bin/env python3
"""
Gemini Schema Mapper for DeathAIAUS IDE
======================================

Converts JSON schemas to natural language prompts for Pantheon models.
Since Pantheon models don't have native schema support, we convert schemas
to detailed prompt instructions and validate responses.

Author: DeathAIAUS
Copyright: DeathAIAUS 2025
"""

import json
import re
import logging
from typing import Dict, List, Optional, Any, Union

logger = logging.getLogger(__name__)

class SchemaMapper:
    """Maps JSON schemas to prompts and validates responses"""
    
    def __init__(self):
        self.max_retries = 3
    
    def schema_to_prompt(self, schema: Dict[str, Any], context: str = "") -> str:
        """Convert JSON schema to natural language prompt instructions"""
        
        if not schema or "properties" not in schema:
            return "Return a valid JSON response."
        
        prompt_parts = []
        
        # Add context if provided
        if context:
            prompt_parts.append(f"Context: {context}")
        
        # Main instruction
        prompt_parts.append("You must return a valid JSON object with the following structure:")
        
        # Process each property
        for prop_name, prop_info in schema["properties"].items():
            prop_prompt = self._property_to_prompt(prop_name, prop_info)
            prompt_parts.append(f"- {prop_prompt}")
        
        # Add required fields note
        required_fields = schema.get("required", [])
        if required_fields:
            prompt_parts.append(f"\nRequired fields: {', '.join(required_fields)}")
        
        # Add validation instructions
        prompt_parts.append("\nImportant:")
        prompt_parts.append("- Return ONLY valid JSON, no additional text")
        prompt_parts.append("- All required fields must be present")
        prompt_parts.append("- Use correct data types (string, number, array, object)")
        prompt_parts.append("- If a field is an array, use [] for empty arrays")
        prompt_parts.append("- If a field is an object, use {} for empty objects")
        
        return "\n".join(prompt_parts)
    
    def _property_to_prompt(self, prop_name: str, prop_info: Dict[str, Any]) -> str:
        """Convert a single property to prompt text"""
        
        prop_type = prop_info.get("type", "string")
        description = prop_info.get("description", "")
        
        # Base property description
        if description:
            prompt = f"{prop_name} ({prop_type}): {description}"
        else:
            prompt = f"{prop_name} ({prop_type})"
        
        # Add type-specific instructions
        if prop_type == "array":
            items_info = prop_info.get("items", {})
            if isinstance(items_info, dict) and "type" in items_info:
                prompt += f" - Array of {items_info['type']}s"
            else:
                prompt += " - Array"
        
        elif prop_type == "object":
            properties = prop_info.get("properties", {})
            if properties:
                prompt += f" - Object with properties: {', '.join(properties.keys())}"
            else:
                prompt += " - Object"
        
        elif prop_type == "number":
            if "minimum" in prop_info or "maximum" in prop_info:
                constraints = []
                if "minimum" in prop_info:
                    constraints.append(f"min: {prop_info['minimum']}")
                if "maximum" in prop_info:
                    constraints.append(f"max: {prop_info['maximum']}")
                prompt += f" - Number ({', '.join(constraints)})"
        
        elif prop_type == "string":
            if "enum" in prop_info:
                prompt += f" - One of: {', '.join(prop_info['enum'])}"
            elif "minLength" in prop_info or "maxLength" in prop_info:
                constraints = []
                if "minLength" in prop_info:
                    constraints.append(f"min length: {prop_info['minLength']}")
                if "maxLength" in prop_info:
                    constraints.append(f"max length: {prop_info['maxLength']}")
                prompt += f" - String ({', '.join(constraints)})"
        
        return prompt
    
    def validate_response(self, response: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Validate response against schema with auto-fixing"""
        
        # First, try to extract JSON from response
        try:
            data = self._extract_json(response)
        except ValueError as e:
            return {"error": f"Could not parse JSON: {e}"}
        
        # Validate against schema
        try:
            validated_data = self._validate_against_schema(data, schema)
            return {"success": True, "data": validated_data}
        except ValidationError as e:
            return {"error": f"Schema validation failed: {e}"}
    
    def _extract_json(self, response: str) -> Dict[str, Any]:
        """Extract JSON from response with multiple fallback strategies"""
        
        # Strategy 1: Try direct JSON parse
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass
        
        # Strategy 2: Extract from markdown code blocks
        json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Strategy 3: Find first JSON object
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
        
        # Strategy 4: Find JSON array
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
        
        raise ValueError(f"Could not extract valid JSON from: {response[:200]}...")
    
    def _validate_against_schema(self, data: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data against schema with auto-fixing"""
        
        if not isinstance(data, dict):
            raise ValidationError("Response must be a JSON object")
        
        validated_data = {}
        properties = schema.get("properties", {})
        required_fields = schema.get("required", [])
        
        # Process each property
        for prop_name, prop_info in properties.items():
            if prop_name in data:
                # Property exists, validate it
                validated_data[prop_name] = self._validate_property(
                    data[prop_name], prop_info, prop_name
                )
            elif prop_name in required_fields:
                # Required field missing, add default
                validated_data[prop_name] = self._get_default_value(prop_info)
                logger.warning(f"Added default value for missing required field: {prop_name}")
            # Optional fields are skipped if not present
        
        return validated_data
    
    def _validate_property(self, value: Any, prop_info: Dict[str, Any], prop_name: str) -> Any:
        """Validate a single property value"""
        
        prop_type = prop_info.get("type", "string")
        
        # Type validation
        if prop_type == "string" and not isinstance(value, str):
            if isinstance(value, (int, float)):
                value = str(value)
            else:
                raise ValidationError(f"{prop_name} must be a string, got {type(value).__name__}")
        
        elif prop_type == "number" and not isinstance(value, (int, float)):
            if isinstance(value, str) and value.replace('.', '').replace('-', '').isdigit():
                value = float(value)
            else:
                raise ValidationError(f"{prop_name} must be a number, got {type(value).__name__}")
        
        elif prop_type == "array" and not isinstance(value, list):
            if isinstance(value, str):
                # Try to parse as JSON array
                try:
                    value = json.loads(value)
                    if not isinstance(value, list):
                        raise ValueError()
                except:
                    # Treat as single item array
                    value = [value]
            else:
                raise ValidationError(f"{prop_name} must be an array, got {type(value).__name__}")
        
        elif prop_type == "object" and not isinstance(value, dict):
            if isinstance(value, str):
                try:
                    value = json.loads(value)
                    if not isinstance(value, dict):
                        raise ValueError()
                except:
                    raise ValidationError(f"{prop_name} must be an object, got {type(value).__name__}")
            else:
                raise ValidationError(f"{prop_name} must be an object, got {type(value).__name__}")
        
        # Additional validations
        if prop_type == "string":
            if "enum" in prop_info and value not in prop_info["enum"]:
                raise ValidationError(f"{prop_name} must be one of {prop_info['enum']}")
            
            if "minLength" in prop_info and len(value) < prop_info["minLength"]:
                raise ValidationError(f"{prop_name} too short (min {prop_info['minLength']})")
            
            if "maxLength" in prop_info and len(value) > prop_info["maxLength"]:
                raise ValidationError(f"{prop_name} too long (max {prop_info['maxLength']})")
        
        elif prop_type == "number":
            if "minimum" in prop_info and value < prop_info["minimum"]:
                raise ValidationError(f"{prop_name} too small (min {prop_info['minimum']})")
            
            if "maximum" in prop_info and value > prop_info["maximum"]:
                raise ValidationError(f"{prop_name} too large (max {prop_info['maximum']})")
        
        return value
    
    def _get_default_value(self, prop_info: Dict[str, Any]) -> Any:
        """Get default value for a property based on its type"""
        
        prop_type = prop_info.get("type", "string")
        
        if prop_type == "string":
            return ""
        elif prop_type == "number":
            return 0
        elif prop_type == "array":
            return []
        elif prop_type == "object":
            return {}
        elif prop_type == "boolean":
            return False
        else:
            return None
    
    def retry_with_schema_fix(self, func, schema: Dict[str, Any], max_retries: int = None) -> Dict[str, Any]:
        """Retry function with increasingly specific schema prompts"""
        
        if max_retries is None:
            max_retries = self.max_retries
        
        for attempt in range(max_retries):
            try:
                result = func()
                validated = self.validate_response(result, schema)
                if validated.get("success"):
                    return validated
                else:
                    logger.warning(f"Schema validation failed (attempt {attempt + 1}): {validated.get('error')}")
            except Exception as e:
                logger.warning(f"Function failed (attempt {attempt + 1}): {e}")
            
            if attempt == max_retries - 1:
                break
            
            # Add more specific instructions for next attempt
            # This would be implemented by the calling function
        
        return {"error": f"Failed after {max_retries} attempts"}

class ValidationError(Exception):
    """Custom exception for schema validation errors"""
    pass

# Predefined schemas for v2 UI
FEASIBILITY_SCHEMA = {
    "type": "object",
    "properties": {
        "feasibility_score": {
            "type": "number",
            "description": "A score from 1-10 indicating feasibility. 1 is impossible, 10 is trivial.",
            "minimum": 1,
            "maximum": 10
        },
        "complexity_level": {
            "type": "string",
            "description": "e.g., 'Low', 'Medium', 'High', 'Very High'",
            "enum": ["Low", "Medium", "High", "Very High"]
        },
        "estimated_time": {
            "type": "string",
            "description": "A rough time estimate, e.g., '2-3 days', '1 week'"
        },
        "reality_check": {
            "type": "string",
            "description": "A brutally honest, slightly pessimistic assessment of the project's viability."
        },
        "red_flags": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Critical issues or potential blockers."
        },
        "warnings": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Potential challenges or things to watch out for."
        }
    },
    "required": ["feasibility_score", "complexity_level", "estimated_time", "reality_check", "red_flags", "warnings"]
}

PROJECT_PLAN_SCHEMA = {
    "type": "object",
    "properties": {
        "thought_process": {
            "type": "string",
            "description": "Your reasoning for the proposed structure and technologies."
        },
        "file_structure": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of all files and folders to be created, like a file tree."
        },
        "dependencies": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of required external libraries or packages (e.g., npm packages)."
        },
        "next_steps": {
            "type": "string",
            "description": "A brief summary of the first few development steps after scaffolding."
        }
    },
    "required": ["thought_process", "file_structure", "dependencies", "next_steps"]
}

TASK_PLAN_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {
            "type": "string",
            "description": "A concise title for the overall task."
        },
        "tasks": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "number"},
                    "description": {"type": "string"},
                    "dependencies": {
                        "type": "array",
                        "items": {"type": "number"}
                    },
                    "estimatedTime": {
                        "type": "string",
                        "description": "e.g., '15 minutes', '2 hours'"
                    },
                    "status": {
                        "type": "string",
                        "description": "Should be 'pending' by default."
                    }
                },
                "required": ["id", "description", "dependencies", "estimatedTime", "status"]
            }
        }
    },
    "required": ["title", "tasks"]
}

FILE_TREE_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "path": {"type": "string"},
            "content": {
                "type": "string",
                "description": "File content. Omit for directories."
            },
            "children": {
                "type": "array",
                "items": {"type": "object"},
                "description": "Child files/folders. Omit for files."
            }
        },
        "required": ["name", "path"]
    }
}

def main():
    """Test the schema mapper"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Gemini Schema Mapper")
    parser.add_argument("--schema", help="Schema to test")
    parser.add_argument("--response", help="Response to validate")
    
    args = parser.parse_args()
    
    mapper = SchemaMapper()
    
    if args.schema and args.response:
        # Test validation
        schema = json.loads(args.schema)
        result = mapper.validate_response(args.response, schema)
        print(json.dumps(result, indent=2))
    else:
        # Test schema to prompt conversion
        prompt = mapper.schema_to_prompt(FEASIBILITY_SCHEMA, "Analyze the feasibility of a React app")
        print("Generated prompt:")
        print(prompt)

if __name__ == "__main__":
    main()
