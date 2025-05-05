from typing import Dict, List, Optional, Any
from agents import Agent
from tools.form_analysis.form_inspector import (
    get_form_elements,
    get_form_structure,
    get_element_by_property,
    get_page_content,
    get_form_field_value
)
from utils.browser_manager import BrowserManager
from configs.logging_config import get_logger

logger = get_logger(__name__)

class FormInteractionAgent(Agent):
    """An agent specialized in analyzing and interacting with forms"""
    
    def __init__(self):
        super().__init__(
            name="Form Interaction Agent",
            instructions="""You are an agent specialized in analyzing and interacting with web forms.
            Your tasks include:
            1. Analyzing form structure and fields
            2. Identifying required fields
            3. Mapping form fields to available data
            4. Determining the best way to fill each field
            5. Tracking form completion progress
            
            You have access to the following tools:
            1. get_form_elements: Get all form elements and their properties
            2. get_form_structure: Get the overall structure of the form
            3. get_element_by_property: Find an element by specific property
            4. get_page_content: Get the current page's HTML content
            5. get_form_field_value: Get the current value of a form field
            
            Use these tools to analyze forms and make decisions about how to proceed.""",
            tools=[
                get_form_elements,
                get_form_structure,
                get_element_by_property,
                get_page_content,
                get_form_field_value
            ]
        )
        self.browser_manager = BrowserManager()
        
    async def initialize(self):
        """Initialize the agent with the current page"""
        await self.browser_manager.initialize()
        
    async def analyze_form(self) -> Dict[str, Any]:
        """Analyze the current form and return its structure"""
        page = await self.browser_manager.get_page()
        
        form_elements = await get_form_elements(page)
        form_structure = await get_form_structure(page)
        
        return {
            "elements": form_elements,
            "structure": form_structure
        }
        
    async def identify_required_fields(self) -> List[Dict[str, Any]]:
        """Identify all required fields in the current form"""
        form_analysis = await self.analyze_form()
        return [
            field for field in form_analysis["elements"]
            if field.get("required", False)
        ]
        
    async def map_fields_to_data(self, available_data: Dict[str, Any]) -> Dict[str, Any]:
        """Map available data to form fields based on field properties"""
        form_analysis = await self.analyze_form()
        field_mapping = {}
        
        for field in form_analysis["elements"]:
            # Try to match field with available data using various properties
            field_id = field.get("id")
            field_name = field.get("name")
            field_label = field.get("label", [])
            field_aria_label = field.get("ariaLabel")
            
            # Check each property against available data keys
            for key in available_data.keys():
                if (key.lower() in [f.lower() for f in field_label] or
                    key.lower() == field_id.lower() or
                    key.lower() == field_name.lower() or
                    key.lower() == field_aria_label.lower()):
                    field_mapping[field_id or field_name] = {
                        "field": field,
                        "data_key": key,
                        "value": available_data[key]
                    }
                    break
                    
        return field_mapping
        
    async def get_form_progress(self) -> Dict[str, Any]:
        """Get the current progress of form completion"""
        form_analysis = await self.analyze_form()
        total_fields = len(form_analysis["elements"])
        required_fields = await self.identify_required_fields()
        filled_fields = sum(1 for field in form_analysis["elements"]
                          if field.get("value"))
        
        return {
            "total_fields": total_fields,
            "required_fields": len(required_fields),
            "filled_fields": filled_fields,
            "progress_percentage": (filled_fields / total_fields * 100) if total_fields > 0 else 0
        } 