from fastapi import APIRouter, Depends, HTTPException, status
from api.schemas import (
    SalesCreate,
    Sales,
)
from starlette.responses import RedirectResponse
from api.controller import (
    create_product_sale_transaction,
)
import traceback
from common.db.session import get_db
from sqlalchemy.orm import Session
from common.custom_exceptions import (
    ProductNotFoundException,
    ProductOutofStockException,
)

router = APIRouter()


@router.get("/")
def main():
    return RedirectResponse(url="/docs/")


@router.post("/create/", response_model=Sales, status_code=201)
def create_product_sale(potential_sale: SalesCreate, db: Session = Depends(get_db)):
    """
    Create a product sale:
    - a sales transaction is only created when the quantity of the product sold is less than or equal to the current inventory
    - product gets sold when a sales transaction is created in the dataabase
    - the current inventory is updated after a sales transaction is created
    - the revenue is calculated by multiplying the quantity of the product sold by the price of the product
    """
    try:
        created_sales_transaction = create_product_sale_transaction(potential_sale, db)
        return created_sales_transaction
    except ProductOutofStockException as error:
        raise HTTPException(status_code=422, detail=str(error))
    except ProductNotFoundException as error:
        raise HTTPException(status_code=404, detail=str(error))
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal Server Error")


# # Define a model for the revenue data
# class RevenueData(BaseModel):
#     product_id: int
#     category_name: str
#     revenue: float

# # Define a route to get the revenue data for a given time period and category
# @router.get("/revenue")
# async def get_revenue_data(
#     start_date: Optional[datetime] = Query(
#         datetime.now() - timedelta(days=7), description="Start date of the time period"
#     ),
#     end_date: Optional[datetime] = Query(
#         datetime.now(), description="End date of the time period"
#     ),
#     category_name: Optional[str] = Query(
#         None, description="Name of the product category"
#     )
# ) -> List[RevenueData]:
#     # Query the database for the revenue data
#     # You can use the start_date, end_date, and category_name parameters to filter the data
#     # and aggregate the revenue by product and category
#     # Here's an example query using SQLAlchemy:
#     # revenue_data = db.query(Sales.product_id, Product.category_name, func.sum(Sales.revenue)).\
#     #     join(Product, Sales.product_id == Product.id).\
#     #     filter(Sales.date_sold >= start_date).\
#     #     filter(Sales.date_sold <= end_date).\
#     #     filter(Product.category_name == category_name).\
#     #     group_by(Sales.product_id, Product.category_name).\
#     #     all()

#     # For this example, let's just return some dummy data
#     revenue_data = [
#         {"product_id": 1, "category_name": "Electronics", "revenue": 1000.0},
#         {"product_id": 2, "category_name": "Clothing", "revenue": 500.0},
#         {"product_id": 3, "category_name": "Home", "revenue": 750.0},
#     ]

#     # Convert the data to the RevenueData model
#     revenue_data_models = [
#         RevenueData(
#             product_id=data["product_id"],
#             category_name=data["category_name"],
#             revenue=data["revenue"]
#         )
#         for data in revenue_data
#     ]

#     return revenue_data_models
