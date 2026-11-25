from fastapi import HTTPException, status

class MissionMindException(HTTPException):
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)

class DocumentProcessingError(MissionMindException):
    def __init__(self, detail: str = "Error occurred during document ingestion or processing"):
        super().__init__(detail=detail, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

class LowConfidenceRetrievalError(MissionMindException):
    def __init__(self, detail: str = "Not Found in the available documents. Please try a different question or add more source documents."):
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)

class AuthenticationError(MissionMindException):
    def __init__(self, detail: str = "Invalid credentials or unauthorized access"):
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED)
