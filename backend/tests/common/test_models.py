from app.common.models import DataResponse, ErrorResponse, ListResponse, StatusResponse


def test_data_response_defaults() -> None:
    r: DataResponse[str] = DataResponse(data="hello")
    assert r.success is True
    assert r.data == "hello"
    assert r.message is None


def test_list_response_defaults() -> None:
    r: ListResponse[int] = ListResponse()
    assert r.success is True
    assert r.data == []
    assert r.total == 0


def test_list_response_with_data() -> None:
    r: ListResponse[int] = ListResponse(data=[1, 2], total=2)
    assert r.total == 2


def test_error_response() -> None:
    r = ErrorResponse(error_code="ERR_001")
    assert r.success is False
    assert r.error_code == "ERR_001"
    assert r.error_details is None


def test_status_response() -> None:
    r = StatusResponse(status="done")
    assert r.success is True
    assert r.status == "done"
