from merketLink.settings import * 

INSTALLED_APPS += [
    "drf_spectacular", # swagger doc
]

REST_FRAMEWORK |= {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}
