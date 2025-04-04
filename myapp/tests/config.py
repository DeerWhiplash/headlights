from datetime import datetime

class ErrorCodes:
    OK = 200
    REDIRECT = 302
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    SERVER_ERROR = 500

class Views:
    HOME = "index"
    MACHINE_LEARNING = "ml_dashboard"
    CUSTOMER_DASHBOARD = "customer_dashboard"
    CUSTOMER_UPLOAD = "upload_claims"
    ACCOUNT_CREATION = "account_creation"
    CONTACT_DETAILS = "contact_details"
    PREDICTION_FEEDBACK = "prediction_feedback"
    FINANCE_DASHBOARD = "finance_dashboard"
    COMPANY_DETAILS = "company_details"
    COMPANY_MANAGE_EMPLOYEES = "company_manage_employees"

    API_MODELS_LIST = "api_models_list"
    API_UPLOAD_MODEL = "api_upload_model"

class Templates:
    HOME = "index.html"
    MACHINE_LEARNING = "ml/ml.html"
    ML_UPLOAD_MODEL = "ml/upload_model.html"
    CUSTOMER = "customer.html"
    FINANCE = "finance.html"
    CONTACT_DETAILS = "contact_details.html"
    PREDICTION_FEEDBACK = "forms/prediction_feedback_form.html"
    COMPANY_DETAILS = "company_details.html"
    COMPANY_USER_MANAGEMENT = "company_manage_users.html"
    
    ACCOUNT_CREATION = "registration/account_creation.html"
    LOGGED_OUT = "registration/logged_out.html"
    LOGIN = "registration/login.html"
    PASSWORD_RESET_COMPLETE = "registration/password_reset_complete.html"
    PASSWORD_RESET_CONFIRM = "registration/password_reset_confirm.html"
    PASSWORD_RESET_DONE = "registration/password_reset_done.html"
    PASSWORD_RESET_EMAIL = "registration/password_reset_email.html"
    PASSWORD_RESET_FORM = "registration/password_reset_form.html"

class TestData:
    EMAIL = "test@headlights.com"
    PHONE = "07123456789"
    ADDRESS = "123 Fake Street, Bristol, BS1 1BJ"
    NAME = "test name"
    PASSWORD = "$password123"
    VALUE = 8000
    PAST_DATE = datetime(year = 2020, month = 1, day = 1)
    PAST_DATETIME = datetime(year = 2020, month = 1, day = 1, hour = 0, minute = 0, second = 0)
    YEAR = 2020
    RATING = 5
