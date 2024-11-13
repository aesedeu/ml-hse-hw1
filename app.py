from fastapi import FastAPI, File, UploadFile, HTTPException, status
from pydantic import BaseModel
from fastapi.responses import StreamingResponse, JSONResponse
import pandas as pd
import numpy as np
import pickle
import uvicorn
import io

app = FastAPI()



class Item(BaseModel):
    year: float
    km_driven: float
    fuel: float
    seller_type: float
    transmission: float
    owner: float
    mileage: float
    engine: float
    max_power: float
    seats: float

@app.on_event("startup")
def load_model():
    with open("my_model.pkl", "rb") as f:
        global model
        model = pickle.load(f)


@app.post("/predict_item")
async def predict_item(item: Item) -> JSONResponse:
    values = [item.year, item.km_driven, item.fuel, item.seller_type, item.transmission, item.owner, item.mileage, item.engine, item.max_power, item.seats]
    values = np.array(values).reshape(1,-1)
    pred = model.predict(values)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"your_price": pred[0]}
    )

@app.post("/predict_items")
async def predict_items(file: UploadFile = File(...)) -> StreamingResponse:
    print(f"Мы получили файл с названием: {file.filename}")
    if not file.filename.endswith("csv"):
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ваш файл должен быть с расширением .csv",
            headers={"info":None}
        )
    else:
        df = pd.read_csv(file.file)

        pred = model.predict(df.values)
        df['pred'] = pred

        buffer = io.BytesIO()
        df.to_csv(buffer, index=False)
        buffer.seek(0)

        return StreamingResponse(
            buffer
        )



if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )