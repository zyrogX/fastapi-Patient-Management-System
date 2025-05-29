from pydantic import BaseModel, AnyUrl, Field, field_validator, computed_field
from typing import List, Dict, Optional, Annotated

class Patient(BaseModel):
    # --- Fields ---
    name: Annotated[str, Field(max_length=50)]
    website: AnyUrl
    age: Annotated[int, Field(gt=0, strict=True)]
    # We need height in meters for the BMI calculation
    height: Annotated[float, Field(gt=0, description="Height in meters")]
    weight: float = Field(gt=5, lt=300)
    married: bool = False
    allergies: Optional[List[str]] = None
    contact_detail: Dict[str, str]

    # --- Field Validator ---
    @field_validator('name')
    def transform_name(cls, value):
        return value.upper()
    
    # --- Computed Field (with correct formula) ---
    @computed_field
    # Note: @property is not needed here
    def calculate_bmi(self) -> float:
        """Calculates BMI using the correct formula: weight / height^2"""
        # The ** 2 is for squaring the height
        bmi = self.weight / (self.height ** 2)
        # Round the result to two decimal places
        return round(bmi, 2)

def add_patient(patient: Patient):
    print(f"Patient Name: {patient.name}")
    print(f"Patient Age: {patient.age}")
    print(f"Is Married: {patient.married}")
    # Access the computed field just like a regular field
    print(f"Calculated BMI: {patient.calculate_bmi}")

# Add the new 'height' field to your patient data
patient_info = {
    'name': "ali",
    "website": "https://gemini.google.com",
    'age': 30,
    'height': 1.75,  # Added height in meters (e.g., 1.75m)
    'weight': 70.2,
    'married': True,
    "allergies": ["polan", "flu"],
    "contact_detail": {'email': "abc@gmail.com", "number": "24325"}
}

patient1 = Patient(**patient_info)

add_patient(patient1)