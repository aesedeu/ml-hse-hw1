from fastapi import FastAPI, File, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
import pandas as pd
from typing import Annotated
from pydantic import BaseModel
import uvicorn
import io

app = FastAPI() 

@app.post("/upload")
async def upload(file: UploadFile = File(...)) -> StreamingResponse:
    if not file.filename.endswith("csv"):
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Incorrect file type")
    else:
        df = pd.read_csv(file.file) # ds_salaries.csv
        required_columns = ["work_year", "experience_level"]

        if not all(col in df.columns for col in required_columns):
            return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Columns in your csv-file must contain {required_columns}")
        df = df.head()
        # <...> model prediction
        
        # output_file_path = f"processed_{file.filename}"
        # df.to_csv(output_file_path, index=False)
        # return FileResponse(path=output_file_path, filename=output_file_path, media_type='text/csv')

        buffer = io.BytesIO()
        df.to_csv(buffer, index=False)
        buffer.seek(0)
        return StreamingResponse(buffer, media_type="csv", headers={
            "Content-Disposition": f"attachment; filename=processed_{file.filename}"
        })
    
        # return JSONResponse(status_code=status.HTTP_200_OK, content={"name":file.filename, "len":len(df)})
    
        # curl -X POST "http://127.0.0.1:8000/upload" -F "file=@apple_quality.csv" -o returned_file.csv

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)