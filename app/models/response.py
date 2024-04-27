from typing import Union
from typing import Optional
from pydantic import BaseModel
from fastapi.responses import StreamingResponse

class BaseResponse(BaseModel):
    code: int = 200
    status: str

class UserResponse(BaseResponse):
    data: Optional[Union[dict, list]]

class UserResponsePagination(UserResponse):
    page: Optional[dict]

class AuthResponse(BaseResponse):
    data: Optional[Union[dict, list]]

class GeneralDataResponse(BaseResponse):
    data: Optional[Union[dict, list]]

class GeneralDataPaginateResponse(BaseResponse):
    data: Optional[Union[dict, list]]
    meta: Optional[Union[dict, list]]

def response_streaming(data, filename):
    return StreamingResponse(
        data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )