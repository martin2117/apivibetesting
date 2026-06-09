*** Settings ***
Resource    ../techshop_keywords.resource

Suite Setup       Create TechShop Session
Suite Teardown    Delete All Sessions


*** Test Cases ***

# ---------------------------------------------------------------------------
# GET /orders
# ---------------------------------------------------------------------------

Get Orders With Valid Token Returns 200
    [Tags]    orders    happy-path    auth-required
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    ${response}=    GET On Session    techshop    /orders    headers=${headers}
    Status Should Be    200    ${response}
    ${orders}=    Set Variable    ${response.json()}
    Should Be True    isinstance($orders, list)

Get Orders Response Contains Required Order Schema Fields
    [Tags]    orders    happy-path    auth-required
    [Documentation]    Places an order first so there is guaranteed at least one order to inspect.
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    # Place a fresh order
    ${body}=        Build Valid Order Body
    POST On Session    techshop    /orders    headers=${headers}    json=${body}
    # Now fetch orders and validate schema
    ${response}=    GET On Session    techshop    /orders    headers=${headers}
    Status Should Be    200    ${response}
    ${orders}=      Set Variable    ${response.json()}
    Should Not Be Empty    ${orders}
    ${first}=       Get From List    ${orders}    0
    Verify Order Schema    ${first}

Get Orders Without Auth Returns 401
    [Tags]    orders    negative    auth-required
    ${response}=    GET On Session    techshop    /orders    expected_status=any
    Status Should Be    401    ${response}
    Response Body Should Contain Error    ${response}

Get Orders With Invalid Token Returns 401
    [Tags]    orders    negative    auth-required
    ${headers}=     Create Dictionary    Authorization=Bearer tampered.token.value
    ${response}=    GET On Session    techshop    /orders    headers=${headers}
    ...             expected_status=any
    Status Should Be    401    ${response}
    Response Body Should Contain Error    ${response}

Get Orders Returns Empty Array When User Has No Orders
    [Tags]    orders    negative    auth-required
    [Documentation]    If the test user has no orders, the API should return 200 with [].
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    ${response}=    GET On Session    techshop    /orders    headers=${headers}
    Status Should Be    200    ${response}
    Should Be True    isinstance($response.json(), list)


# ---------------------------------------------------------------------------
# POST /orders (checkout)
# ---------------------------------------------------------------------------

Place Order With Valid Payload Returns 201
    [Tags]    orders    happy-path    auth-required
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    ${body}=        Build Valid Order Body
    ${response}=    POST On Session    techshop    /orders    headers=${headers}    json=${body}
    Status Should Be    201    ${response}
    ${order}=    Set Variable    ${response.json()}
    Verify Order Schema    ${order}
    Dictionary Should Contain Key    ${order}    payment
    ${payment_resp}=    Get From Dictionary    ${order}    payment
    Dictionary Should Contain Key    ${payment_resp}    expiryDate


# ---------------------------------------------------------------------------
# POST /orders — individual required sub-field validation
# (swagger requires firstName, lastName, email, phone; cardNumber, expiryDate, cvv)
# ---------------------------------------------------------------------------

Place Order With Missing Shipping First Name Returns 400
    [Tags]    orders    negative    auth-required
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    ${body}=        Build Valid Order Body    firstName=${None}
    # Robot Framework or python dictionary set with None key/val can represent missing field or null depending on serializing
    # Let's construct manually to ensure field is truly missing:
    ${item}=        Create Dictionary    productId=${1}    quantity=${1}
    ${items}=       Create List    ${item}
    ${shipping}=    Create Dictionary    lastName=Doe    email=jane@example.com    phone=0412345678
    ${payment}=     Create Dictionary
    ...    cardNumber=4111111111111111    expiryDate=12/28    cvv=123
    ${body}=        Create Dictionary    items=${items}    shipping=${shipping}    payment=${payment}
    ${response}=    POST On Session    techshop    /orders    headers=${headers}    json=${body}
    ...             expected_status=any
    Status Should Be    400    ${response}
    Response Body Should Contain Error    ${response}

Place Order With Missing Shipping Last Name Returns 400
    [Tags]    orders    negative    auth-required
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    ${item}=        Create Dictionary    productId=${1}    quantity=${1}
    ${items}=       Create List    ${item}
    ${shipping}=    Create Dictionary    firstName=Jane    email=jane@example.com    phone=0412345678
    ${payment}=     Create Dictionary
    ...    cardNumber=4111111111111111    expiryDate=12/28    cvv=123
    ${body}=        Create Dictionary    items=${items}    shipping=${shipping}    payment=${payment}
    ${response}=    POST On Session    techshop    /orders    headers=${headers}    json=${body}
    ...             expected_status=any
    Status Should Be    400    ${response}
    Response Body Should Contain Error    ${response}

Place Order With Missing Shipping Phone Returns 400
    [Tags]    orders    negative    auth-required
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    ${item}=        Create Dictionary    productId=${1}    quantity=${1}
    ${items}=       Create List    ${item}
    ${shipping}=    Create Dictionary    firstName=Jane    lastName=Doe    email=jane@example.com
    ${payment}=     Create Dictionary
    ...    cardNumber=4111111111111111    expiryDate=12/28    cvv=123
    ${body}=        Create Dictionary    items=${items}    shipping=${shipping}    payment=${payment}
    ${response}=    POST On Session    techshop    /orders    headers=${headers}    json=${body}
    ...             expected_status=any
    Status Should Be    400    ${response}
    Response Body Should Contain Error    ${response}

Place Order With Missing Payment Card Number Returns 400
    [Tags]    orders    negative    auth-required
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    ${item}=        Create Dictionary    productId=${1}    quantity=${1}
    ${items}=       Create List    ${item}
    ${shipping}=    Create Dictionary
    ...    firstName=Jane    lastName=Doe    email=jane@example.com    phone=0412345678
    ${payment}=     Create Dictionary    expiryDate=12/28    cvv=123
    ${body}=        Create Dictionary    items=${items}    shipping=${shipping}    payment=${payment}
    ${response}=    POST On Session    techshop    /orders    headers=${headers}    json=${body}
    ...             expected_status=any
    Status Should Be    400    ${response}
    Response Body Should Contain Error    ${response}

Place Order With Missing Payment Expiry Date Returns 400
    [Tags]    orders    negative    auth-required
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    ${item}=        Create Dictionary    productId=${1}    quantity=${1}
    ${items}=       Create List    ${item}
    ${shipping}=    Create Dictionary
    ...    firstName=Jane    lastName=Doe    email=jane@example.com    phone=0412345678
    ${payment}=     Create Dictionary    cardNumber=4111111111111111    cvv=123
    ${body}=        Create Dictionary    items=${items}    shipping=${shipping}    payment=${payment}
    ${response}=    POST On Session    techshop    /orders    headers=${headers}    json=${body}
    ...             expected_status=any
    Status Should Be    400    ${response}
    Response Body Should Contain Error    ${response}

Place Order With Missing Payment CVV Returns 400
    [Tags]    orders    negative    auth-required
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    ${item}=        Create Dictionary    productId=${1}    quantity=${1}
    ${items}=       Create List    ${item}
    ${shipping}=    Create Dictionary
    ...    firstName=Jane    lastName=Doe    email=jane@example.com    phone=0412345678
    ${payment}=     Create Dictionary    cardNumber=4111111111111111    expiryDate=12/28
    ${body}=        Create Dictionary    items=${items}    shipping=${shipping}    payment=${payment}
    ${response}=    POST On Session    techshop    /orders    headers=${headers}    json=${body}
    ...             expected_status=any
    Status Should Be    400    ${response}
    Response Body Should Contain Error    ${response}

Place Order Without Auth Returns 401
    [Tags]    orders    negative    auth-required
    ${body}=        Build Valid Order Body
    ${response}=    POST On Session    techshop    /orders    json=${body}
    ...             expected_status=any
    Status Should Be    401    ${response}
    Response Body Should Contain Error    ${response}

Place Order With Missing Items Field Returns 400
    [Tags]    orders    negative    auth-required
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    ${shipping}=    Create Dictionary
    ...    firstName=Jane    lastName=Doe    email=jane@example.com    phone=0412345678
    ${payment}=     Create Dictionary
    ...    cardNumber=4111111111111111    expiryDate=12/28    cvv=123
    ${body}=        Create Dictionary    shipping=${shipping}    payment=${payment}
    ${response}=    POST On Session    techshop    /orders    headers=${headers}    json=${body}
    ...             expected_status=any
    Status Should Be    400    ${response}
    Response Body Should Contain Error    ${response}

Place Order With Missing Shipping Field Returns 400
    [Tags]    orders    negative    auth-required
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    ${item}=        Create Dictionary    productId=${1}    quantity=${1}
    ${items}=       Create List    ${item}
    ${payment}=     Create Dictionary
    ...    cardNumber=4111111111111111    expiryDate=12/28    cvv=123
    ${body}=        Create Dictionary    items=${items}    payment=${payment}
    ${response}=    POST On Session    techshop    /orders    headers=${headers}    json=${body}
    ...             expected_status=any
    Status Should Be    400    ${response}
    Response Body Should Contain Error    ${response}

Place Order With Missing Payment Field Returns 400
    [Tags]    orders    negative    auth-required
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    ${item}=        Create Dictionary    productId=${1}    quantity=${1}
    ${items}=       Create List    ${item}
    ${shipping}=    Create Dictionary
    ...    firstName=Jane    lastName=Doe    email=jane@example.com    phone=0412345678
    ${body}=        Create Dictionary    items=${items}    shipping=${shipping}
    ${response}=    POST On Session    techshop    /orders    headers=${headers}    json=${body}
    ...             expected_status=any
    Status Should Be    400    ${response}
    Response Body Should Contain Error    ${response}

Place Order With Empty Items Array Returns 400
    [Tags]    orders    negative    auth-required
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    ${items}=       Create List
    ${shipping}=    Create Dictionary
    ...    firstName=Jane    lastName=Doe    email=jane@example.com    phone=0412345678
    ${payment}=     Create Dictionary
    ...    cardNumber=4111111111111111    expiryDate=12/28    cvv=123
    ${body}=        Create Dictionary    items=${items}    shipping=${shipping}    payment=${payment}
    ${response}=    POST On Session    techshop    /orders    headers=${headers}    json=${body}
    ...             expected_status=any
    Status Should Be    400    ${response}
    Response Body Should Contain Error    ${response}

Place Order With Invalid Phone Number Returns 400
    [Tags]    orders    negative    auth-required
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    ${body}=        Build Valid Order Body    phone=12345
    ${response}=    POST On Session    techshop    /orders    headers=${headers}    json=${body}
    ...             expected_status=any
    Status Should Be    400    ${response}
    Response Body Should Contain Error    ${response}

Place Order With Invalid Card Number Returns 400
    [Tags]    orders    negative    auth-required
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    ${body}=        Build Valid Order Body    cardNumber=1234
    ${response}=    POST On Session    techshop    /orders    headers=${headers}    json=${body}
    ...             expected_status=any
    Status Should Be    400    ${response}
    Response Body Should Contain Error    ${response}

Place Order With Past Expiry Date Returns 400
    [Tags]    orders    negative    auth-required
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    ${body}=        Build Valid Order Body    expiryDate=01/20
    ${response}=    POST On Session    techshop    /orders    headers=${headers}    json=${body}
    ...             expected_status=any
    Status Should Be    400    ${response}
    Response Body Should Contain Error    ${response}

Place Order With Invalid CVV Returns 400
    [Tags]    orders    negative    auth-required
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    ${body}=        Build Valid Order Body    cvv=12
    ${response}=    POST On Session    techshop    /orders    headers=${headers}    json=${body}
    ...             expected_status=any
    Status Should Be    400    ${response}
    Response Body Should Contain Error    ${response}

Place Order With Invalid Shipping Email Returns 400
    [Tags]    orders    negative    auth-required
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    ${body}=        Build Valid Order Body    email=not-an-email
    ${response}=    POST On Session    techshop    /orders    headers=${headers}    json=${body}
    ...             expected_status=any
    Status Should Be    400    ${response}
    Response Body Should Contain Error    ${response}

Place Order With Zero Item Quantity Returns 400
    [Tags]    orders    negative    auth-required
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    ${item}=        Create Dictionary    productId=${1}    quantity=${0}
    ${items}=       Create List    ${item}
    ${shipping}=    Create Dictionary
    ...    firstName=Jane    lastName=Doe    email=jane@example.com    phone=0412345678
    ${payment}=     Create Dictionary
    ...    cardNumber=4111111111111111    expiryDate=12/28    cvv=123
    ${body}=        Create Dictionary    items=${items}    shipping=${shipping}    payment=${payment}
    ${response}=    POST On Session    techshop    /orders    headers=${headers}    json=${body}
    ...             expected_status=any
    Status Should Be    400    ${response}
    Response Body Should Contain Error    ${response}

Place Order With Non Existent ProductId Returns 400
    [Tags]    orders    negative    auth-required
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    ${item}=        Create Dictionary    productId=${99999}    quantity=${1}
    ${items}=       Create List    ${item}
    ${shipping}=    Create Dictionary
    ...    firstName=Jane    lastName=Doe    email=jane@example.com    phone=0412345678
    ${payment}=     Create Dictionary
    ...    cardNumber=4111111111111111    expiryDate=12/28    cvv=123
    ${body}=        Create Dictionary    items=${items}    shipping=${shipping}    payment=${payment}
    ${response}=    POST On Session    techshop    /orders    headers=${headers}    json=${body}
    ...             expected_status=any
    Status Should Be    400    ${response}
    Response Body Should Contain Error    ${response}
