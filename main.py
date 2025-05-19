from fastapi import FastAPI , Path , HTTPException , Query
import json

app = FastAPI()

# This function now parses the JSON string into a Python dictionary
def load_data():
    with open("patients.json", "r") as f:
        data = json.load(f)  # NOT f.read()
    return data

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
    

