from fastapi import FastAPI , Path , HTTPException , Query 
from fastapi.responses import JSONResponse
import json
from pydantic import BaseModel , Field , computed_field
from typing import Annotated , Literal , Optional

app = FastAPI()

class Patient(BaseModel):
    id : Annotated[str, Field(...,description="id of Patient" , examples=["P001"])]
    name : Annotated[str , Field(..., description="Name of Patient" , examples=["Ali"])]
    city : Annotated[str , Field(..., description="Patient's City" , examples=["Islamabad"])]
    age : Annotated[int , Field(...,gt=0 , lt= 120 , description="Age of Patient range 0-120")]
    gender : Annotated[Literal['male' , 'female','other'] , Field(..., description="Gender of Patient" , examples=['male' , 'female', 'other'])]
    height : Annotated[float, Field(...,gt=0 , description="height of Patient in meters", examples=["183 meter"])]
    weight : Annotated[float , Field(..., gt=0 , description= "weigt of Patient in kg" , examples=["65 kg"])]

    @computed_field
    @property
    def bmi(self) -> float:
       bmi = self.weight / (self.height ** 2)
       return bmi
    
    @computed_field
    @property
    def verdict(self)->str:
        if self.bmi < 18.5:
            return "UnderWeight"
        elif self.bmi < 25:
            return "Normal"
        elif self.bmi < 30:
            return "OverWeight"
        else :
            return "Obese"
        
class PatientUpdate(BaseModel):
    name : Annotated[Optional[str] , Field(default=None)]
    city : Annotated[Optional[str]  ,Field(default=None)]
    age : Annotated[Optional[int]  , Field(default=None , gt=0)]
    gender : Annotated[Optional[Literal['male' , 'female','other']] ,Field(default=None)]
    height : Annotated[Optional[float] , Field(default=None , gt=0)]
    weight : Annotated[Optional[float]  , Field(default=None,gt=0 )]


# This function now parses the JSON string into a Python dictionary
def load_data():
    with open("patients.json", "r") as f:
        data = json.load(f)  # NOT f.read()
    return data

def save_data(data):
    with open("patients.json", "w") as f:
        json.dump(data,f)

@app.get("/")
def hello_world():
    return {"message": "Patient Management System"}

@app.get("/about")
def about():
    return {"message": "This is a fully operational Patient Management System."}

@app.get("/patients")
def view():
    data = load_data()
    return data  # Now it's a dictionary, not a string

@app.get("/patients/{patient_id}")
def view_patient(patient_id: str=Path(..., title="The ID of the patient to view" , example="P001")):
    data = load_data()
    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404, detail="Patient not found")

@app.get("/sort")
def sort_patients(sort_by: str = Query(..., title="Sort by field", description="Field to sort by", example="age"),order: str = Query("asc", title="Sort order", description="Order to sort by", example="asc")):
    data = load_data()
    if sort_by not in ["age","bmi","city"]:
        raise HTTPException(status_code=400, detail="Invalid sort field")
    if order not in ["asc","desc"]:
        raise HTTPException(status_code=400, detail="Invalid sort order")
    
    sorted_data = sorted(data.values(), key=lambda x: x[sort_by], reverse=(order == "desc"))
    return sorted_data
    
@app.post('/insert')
def insert_patient(patient : Patient):
    data = load_data()
    if patient.id in data:
        raise HTTPException(status_code=400 , detail= "Patient with this Id already Exists")
    data[patient.id]=patient.model_dump(exclude=['id'])
    
    save_data(data)
    return JSONResponse(status_code=201 , content={'message' : 'Inserted Succesfully'})

@app.put('/edit/{patient_id}')
def update_patient(patient_id : str  , patient_update: PatientUpdate):
    data=load_data()
    if patient_id not in data:
        raise HTTPException(status_code=404 , detail= "Patient Not found")
    
    existing_patient_data= data[patient_id]
    update_patient_data = patient_update.model_dump(exclude_unset=True)

    for key,value in update_patient_data.items():
        existing_patient_data[key]=value
    
    existing_patient_data['id']= patient_id
    patient_pydantic_obj = Patient(**existing_patient_data)

    existing_patient_data=patient_pydantic_obj.model_dump(exclude='id')
    data[patient_id]= existing_patient_data

    save_data(data)

    return JSONResponse(status_code=200 , content={'message' : 'patient data updated'})

@app.delete('/delete/{patient_id}')
def delete_patient(patient_id : str):
    data = load_data()
    if patient_id not in data:
        raise HTTPException(status_code=404 , detail= "Patient Not found")
    
    del data[patient_id]
    save_data(data)
    return JSONResponse(status_code=200 , content={'message' : 'patient data deleted'})


    