"""
Descriptive HTTP status codes, for code readability.

See RFC 2616 - https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html
And RFC 6585 - https://tools.ietf.org/html/rfc6585
And RFC 4918 - https://tools.ietf.org/html/rfc4918
"""


def is_informational(code):
    return 100 <= code <= 199


def is_success(code):
    return 200 <= code <= 299


def is_redirect(code):
    return 300 <= code <= 399


def is_client_error(code):
    return 400 <= code <= 499


def is_server_error(code):
    return 500 <= code <= 599


HTTP_100_CONTINUE = 100
HTTP_101_SWITCHING_PROTOCOLS = 101
HTTP_102_PROCESSING = 102
HTTP_103_EARLY_HINTS = 103
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_202_ACCEPTED = 202
HTTP_203_NON_AUTHORITATIVE_INFORMATION = 203
HTTP_204_NO_CONTENT = 204
HTTP_205_RESET_CONTENT = 205
HTTP_206_PARTIAL_CONTENT = 206
HTTP_207_MULTI_STATUS = 207
HTTP_208_ALREADY_REPORTED = 208
HTTP_226_IM_USED = 226
HTTP_300_MULTIPLE_CHOICES = 300
HTTP_301_MOVED_PERMANENTLY = 301
HTTP_302_FOUND = 302
HTTP_303_SEE_OTHER = 303
HTTP_304_NOT_MODIFIED = 304
HTTP_305_USE_PROXY = 305
HTTP_306_RESERVED = 306
HTTP_307_TEMPORARY_REDIRECT = 307
HTTP_308_PERMANENT_REDIRECT = 308
HTTP_400_BAD_REQUEST = 400
HTTP_401_UNAUTHORIZED = 401
HTTP_402_PAYMENT_REQUIRED = 402
HTTP_403_FORBIDDEN = 403
HTTP_404_NOT_FOUND = 404
HTTP_405_METHOD_NOT_ALLOWED = 405
HTTP_406_NOT_ACCEPTABLE = 406
HTTP_407_PROXY_AUTHENTICATION_REQUIRED = 407
HTTP_408_REQUEST_TIMEOUT = 408
HTTP_409_CONFLICT = 409
HTTP_410_GONE = 410
HTTP_411_LENGTH_REQUIRED = 411
HTTP_412_PRECONDITION_FAILED = 412
HTTP_413_REQUEST_ENTITY_TOO_LARGE = 413
HTTP_414_REQUEST_URI_TOO_LONG = 414
HTTP_415_UNSUPPORTED_MEDIA_TYPE = 415
HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE = 416
HTTP_417_EXPECTATION_FAILED = 417
HTTP_418_IM_A_TEAPOT = 418
HTTP_421_MISDIRECTED_REQUEST = 421
HTTP_422_UNPROCESSABLE_ENTITY = 422
HTTP_423_LOCKED = 423
HTTP_424_FAILED_DEPENDENCY = 424
HTTP_425_TOO_EARLY = 425
HTTP_426_UPGRADE_REQUIRED = 426
HTTP_428_PRECONDITION_REQUIRED = 428
HTTP_429_TOO_MANY_REQUESTS = 429
HTTP_431_REQUEST_HEADER_FIELDS_TOO_LARGE = 431
HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS = 451
HTTP_500_INTERNAL_SERVER_ERROR = 500
HTTP_501_NOT_IMPLEMENTED = 501
HTTP_502_BAD_GATEWAY = 502
HTTP_503_SERVICE_UNAVAILABLE = 503
HTTP_504_GATEWAY_TIMEOUT = 504
HTTP_505_HTTP_VERSION_NOT_SUPPORTED = 505
HTTP_506_VARIANT_ALSO_NEGOTIATES = 506
HTTP_507_INSUFFICIENT_STORAGE = 507
HTTP_508_LOOP_DETECTED = 508
HTTP_509_BANDWIDTH_LIMIT_EXCEEDED = 509
HTTP_510_NOT_EXTENDED = 510
HTTP_511_NETWORK_AUTHENTICATION_REQUIRED = 511


h100_HTTP_100_CONTINUE = 100
h101_HTTP_101_SWITCHING_PROTOCOLS = 101
h102_HTTP_102_PROCESSING = 102
h103_HTTP_103_EARLY_HINTS = 103
h200_HTTP_200_OK = 200
h201_HTTP_201_CREATED = 201
h202_HTTP_202_ACCEPTED = 202
h203_HTTP_203_NON_AUTHORITATIVE_INFORMATION = 203
h204_HTTP_204_NO_CONTENT = 204
h205_HTTP_205_RESET_CONTENT = 205
h206_HTTP_206_PARTIAL_CONTENT = 206
h207_HTTP_207_MULTI_STATUS = 207
h208_HTTP_208_ALREADY_REPORTED = 208
h226_HTTP_226_IM_USED = 226
h300_HTTP_300_MULTIPLE_CHOICES = 300
h301_HTTP_301_MOVED_PERMANENTLY = 301
h302_HTTP_302_FOUND = 302
h303_HTTP_303_SEE_OTHER = 303
h304_HTTP_304_NOT_MODIFIED = 304
h305_HTTP_305_USE_PROXY = 305
h306_HTTP_306_RESERVED = 306
h307_HTTP_307_TEMPORARY_REDIRECT = 307
h308_HTTP_308_PERMANENT_REDIRECT = 308
h400_HTTP_400_BAD_REQUEST = 400
h401_HTTP_401_UNAUTHORIZED = 401
h402_HTTP_402_PAYMENT_REQUIRED = 402
h403_HTTP_403_FORBIDDEN = 403
h404_HTTP_404_NOT_FOUND = 404
h405_HTTP_405_METHOD_NOT_ALLOWED = 405
h406_HTTP_406_NOT_ACCEPTABLE = 406
h407_HTTP_407_PROXY_AUTHENTICATION_REQUIRED = 407
h408_HTTP_408_REQUEST_TIMEOUT = 408
h409_HTTP_409_CONFLICT = 409
h410_HTTP_410_GONE = 410
h411_HTTP_411_LENGTH_REQUIRED = 411
h412_HTTP_412_PRECONDITION_FAILED = 412
h413_HTTP_413_REQUEST_ENTITY_TOO_LARGE = 413
h414_HTTP_414_REQUEST_URI_TOO_LONG = 414
h415_HTTP_415_UNSUPPORTED_MEDIA_TYPE = 415
h416_HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE = 416
h417_HTTP_417_EXPECTATION_FAILED = 417
h418_HTTP_418_IM_A_TEAPOT = 418
h421_HTTP_421_MISDIRECTED_REQUEST = 421
h422_HTTP_422_UNPROCESSABLE_ENTITY = 422
h423_HTTP_423_LOCKED = 423
h424_HTTP_424_FAILED_DEPENDENCY = 424
h425_HTTP_425_TOO_EARLY = 425
h426_HTTP_426_UPGRADE_REQUIRED = 426
h428_HTTP_428_PRECONDITION_REQUIRED = 428
h429_HTTP_429_TOO_MANY_REQUESTS = 429
h431_HTTP_431_REQUEST_HEADER_FIELDS_TOO_LARGE = 431
h451_HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS = 451
h500_HTTP_500_INTERNAL_SERVER_ERROR = 500
h501_HTTP_501_NOT_IMPLEMENTED = 501
h502_HTTP_502_BAD_GATEWAY = 502
h503_HTTP_503_SERVICE_UNAVAILABLE = 503
h504_HTTP_504_GATEWAY_TIMEOUT = 504
h505_HTTP_505_HTTP_VERSION_NOT_SUPPORTED = 505
h506_HTTP_506_VARIANT_ALSO_NEGOTIATES = 506
h507_HTTP_507_INSUFFICIENT_STORAGE = 507
h508_HTTP_508_LOOP_DETECTED = 508
h509_HTTP_509_BANDWIDTH_LIMIT_EXCEEDED = 509
h510_HTTP_510_NOT_EXTENDED = 510
h511_HTTP_511_NETWORK_AUTHENTICATION_REQUIRED = 511
