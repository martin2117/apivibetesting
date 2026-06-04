*** Settings ***
Resource    techshop_keywords.robot

Suite Setup       Create TechShop Session
Suite Teardown    Delete All Sessions


*** Test Cases ***

# ---------------------------------------------------------------------------
# POST /auth/login
# ---------------------------------------------------------------------------

Login With Valid Credentials Returns Token
    [Tags]    auth    happy-path
    ${body}=        Create Dictionary    email=${EMAIL}    password=${PASSWORD}
    ${response}=    POST On Session    techshop    /auth/login    json=${body}
    Status Should Be    200    ${response}
    ${json}=    Set Variable    ${response.json()}
    Dictionary Should Contain Key    ${json}    token
    Dictionary Should Contain Key    ${json}    user
    ${user}=    Get From Dictionary    ${json}    user
    Dictionary Should Contain Key    ${user}    id
    Dictionary Should Contain Key    ${user}    email
    Dictionary Should Contain Key    ${user}    name

Login With Wrong Password Returns 401
    [Tags]    auth    negative
    ${body}=        Create Dictionary    email=${EMAIL}    password=wrong_password_xyz
    ${response}=    POST On Session    techshop    /auth/login    json=${body}
    ...             expected_status=any
    Status Should Be    401    ${response}

Login With Missing Email Returns 400
    [Tags]    auth    negative
    ${body}=        Create Dictionary    password=${PASSWORD}
    ${response}=    POST On Session    techshop    /auth/login    json=${body}
    ...             expected_status=any
    Status Should Be    400    ${response}

Login With Missing Password Returns 400
    [Tags]    auth    negative
    ${body}=        Create Dictionary    email=${EMAIL}
    ${response}=    POST On Session    techshop    /auth/login    json=${body}
    ...             expected_status=any
    Status Should Be    400    ${response}

Login With Empty Body Returns 400
    [Tags]    auth    negative
    ${body}=        Create Dictionary
    ${response}=    POST On Session    techshop    /auth/login    json=${body}
    ...             expected_status=any
    Status Should Be    400    ${response}

Login With Unknown User Returns 401
    [Tags]    auth    negative
    ${body}=        Create Dictionary    email=nobody@unknown.example    password=irrelevant
    ${response}=    POST On Session    techshop    /auth/login    json=${body}
    ...             expected_status=any
    Status Should Be    401    ${response}


# ---------------------------------------------------------------------------
# GET /products
# ---------------------------------------------------------------------------

Get All Products Returns 200 With Product Array
    [Tags]    products    happy-path
    ${response}=    GET On Session    techshop    /products
    Status Should Be    200    ${response}
    ${products}=    Set Variable    ${response.json()}
    Should Not Be Empty    ${products}
    ${first}=    Get From List    ${products}    0
    Dictionary Should Contain Key    ${first}    id
    Dictionary Should Contain Key    ${first}    name
    Dictionary Should Contain Key    ${first}    price
    Dictionary Should Contain Key    ${first}    category
    Dictionary Should Contain Key    ${first}    stock
    Dictionary Should Contain Key    ${first}    inStock

Get Products Filtered By Valid Category Returns 200
    [Tags]    products    happy-path
    ${params}=      Create Dictionary    category=computers
    ${response}=    GET On Session    techshop    /products    params=${params}
    Status Should Be    200    ${response}
    ${products}=    Set Variable    ${response.json()}
    Should Not Be Empty    ${products}
    # Every returned item must belong to the requested category
    FOR    ${product}    IN    @{products}
        ${cat}=    Get From Dictionary    ${product}    category
        Should Be Equal As Strings    ${cat}    computers
    END

Get Products Filtered By Invalid Category Returns Empty Array Or 400
    [Tags]    products    negative
    ${params}=      Create Dictionary    category=invalid-category
    ${response}=    GET On Session    techshop    /products    params=${params}
    ...             expected_status=any
    ${status}=      Set Variable    ${response.status_code}
    Should Be True    ${status} == 200 or ${status} == 400
    Run Keyword If    ${status} == 200
    ...    Should Be Empty    ${response.json()}

Get Products With Unsupported Query Param Stays Valid
    [Tags]    products    negative
    ${params}=      Create Dictionary    limit=10
    ${response}=    GET On Session    techshop    /products    params=${params}
    ...             expected_status=any
    ${status}=      Set Variable    ${response.status_code}
    Should Be True    ${status} == 200 or ${status} == 400

Post To Products Endpoint Returns 405
    [Tags]    products    negative
    ${response}=    POST On Session    techshop    /products    json=${{{}}}
    ...             expected_status=any
    Status Should Be    405    ${response}


# ---------------------------------------------------------------------------
# GET /products/{id}
# ---------------------------------------------------------------------------

Get Product With Valid ID Returns 200
    [Tags]    products    happy-path
    ${response}=    GET On Session    techshop    /products/1
    Status Should Be    200    ${response}
    ${product}=    Set Variable    ${response.json()}
    Dictionary Should Contain Key    ${product}    id
    Dictionary Should Contain Key    ${product}    name
    Dictionary Should Contain Key    ${product}    description
    Dictionary Should Contain Key    ${product}    price
    Dictionary Should Contain Key    ${product}    category
    Dictionary Should Contain Key    ${product}    stock
    Dictionary Should Contain Key    ${product}    inStock

Get Product With Unknown ID Returns 404
    [Tags]    products    negative
    ${response}=    GET On Session    techshop    /products/99999
    ...             expected_status=any
    Status Should Be    404    ${response}

Get Product With Non Numeric ID Returns 400 Or 404
    [Tags]    products    negative
    ${response}=    GET On Session    techshop    /products/abc
    ...             expected_status=any
    ${status}=      Set Variable    ${response.status_code}
    Should Be True    ${status} == 400 or ${status} == 404

Get Product With Negative ID Returns 400 Or 404
    [Tags]    products    negative
    ${response}=    GET On Session    techshop    /products/-1
    ...             expected_status=any
    ${status}=      Set Variable    ${response.status_code}
    Should Be True    ${status} == 400 or ${status} == 404

Get Product With Missing ID In Path Returns 404
    [Tags]    products    negative
    [Documentation]    GET /products/ (trailing slash, no ID) should return 404 or a routing error.
    ${response}=    GET On Session    techshop    /products/
    ...             expected_status=any
    ${status}=      Set Variable    ${response.status_code}
    Should Be True    ${status} == 404 or ${status} == 400


# ---------------------------------------------------------------------------
# GET /cart
# ---------------------------------------------------------------------------

Get Cart With Valid Token Returns 200
    [Tags]    cart    happy-path    auth-required
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    ${response}=    GET On Session    techshop    /cart    headers=${headers}
    Status Should Be    200    ${response}
    ${cart}=    Set Variable    ${response.json()}
    Dictionary Should Contain Key    ${cart}    items
    Dictionary Should Contain Key    ${cart}    total

Get Cart Without Auth Token Returns 401
    [Tags]    cart    negative    auth-required
    ${response}=    GET On Session    techshop    /cart    expected_status=any
    Status Should Be    401    ${response}

Get Cart With Invalid Token Returns 401
    [Tags]    cart    negative    auth-required
    ${headers}=     Create Dictionary    Authorization=Bearer this.is.not.a.valid.token
    ${response}=    GET On Session    techshop    /cart    headers=${headers}
    ...             expected_status=any
    Status Should Be    401    ${response}

Get Cart With Malformed Auth Header Returns 401
    [Tags]    cart    negative    auth-required
    ${headers}=     Create Dictionary    Authorization=Bearer
    ${response}=    GET On Session    techshop    /cart    headers=${headers}
    ...             expected_status=any
    Status Should Be    401    ${response}

Get Cart With Basic Auth Header Returns 401
    [Tags]    cart    negative    auth-required
    ${headers}=     Create Dictionary    Authorization=Basic dXNlcjpwYXNz
    ${response}=    GET On Session    techshop    /cart    headers=${headers}
    ...             expected_status=any
    Status Should Be    401    ${response}


# ---------------------------------------------------------------------------
# POST /cart
# ---------------------------------------------------------------------------

Add Item To Cart With Valid Token Returns 201
    [Tags]    cart    happy-path    auth-required
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    ${body}=        Create Dictionary    productId=${1}    quantity=${2}
    ${response}=    POST On Session    techshop    /cart    headers=${headers}    json=${body}
    Status Should Be    201    ${response}

Add Item To Cart Reflects In GET Cart
    [Tags]    cart    happy-path    auth-required
    [Documentation]    After POST /cart, a subsequent GET /cart must show the new line item.
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    ${body}=        Create Dictionary    productId=${2}    quantity=${3}
    ${post_resp}=   POST On Session    techshop    /cart    headers=${headers}    json=${body}
    Status Should Be    201    ${post_resp}
    ${cart_resp}=   GET On Session    techshop    /cart    headers=${headers}
    Status Should Be    200    ${cart_resp}
    ${items}=       Get From Dictionary    ${cart_resp.json()}    items
    Should Not Be Empty    ${items}
    # Find at least one item matching productId=2
    ${found}=    Set Variable    ${FALSE}
    FOR    ${item}    IN    @{items}
        ${pid}=    Get From Dictionary    ${item}    productId
        Run Keyword If    ${pid} == 2    Set Test Variable    ${found}    ${TRUE}
    END
    Should Be True    ${found}    msg=productId 2 was not found in cart after adding it

Add Item To Cart Without Auth Returns 401
    [Tags]    cart    negative    auth-required
    ${body}=        Create Dictionary    productId=${1}    quantity=${2}
    ${response}=    POST On Session    techshop    /cart    json=${body}
    ...             expected_status=any
    Status Should Be    401    ${response}

Add Item To Cart With Non Existent Product Returns 404
    [Tags]    cart    negative    auth-required
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    ${body}=        Create Dictionary    productId=${99999}    quantity=${1}
    ${response}=    POST On Session    techshop    /cart    headers=${headers}    json=${body}
    ...             expected_status=any
    Status Should Be    404    ${response}

Add Item To Cart With Zero Quantity Returns 400
    [Tags]    cart    negative    auth-required
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    ${body}=        Create Dictionary    productId=${1}    quantity=${0}
    ${response}=    POST On Session    techshop    /cart    headers=${headers}    json=${body}
    ...             expected_status=any
    Status Should Be    400    ${response}

Add Item To Cart With Negative Quantity Returns 400
    [Tags]    cart    negative    auth-required
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    ${body}=        Create Dictionary    productId=${1}    quantity=${-1}
    ${response}=    POST On Session    techshop    /cart    headers=${headers}    json=${body}
    ...             expected_status=any
    Status Should Be    400    ${response}

Add Item To Cart With Missing ProductId Returns 400
    [Tags]    cart    negative    auth-required
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    ${body}=        Create Dictionary    quantity=${2}
    ${response}=    POST On Session    techshop    /cart    headers=${headers}    json=${body}
    ...             expected_status=any
    Status Should Be    400    ${response}

Add Item To Cart With Missing Quantity Returns 400
    [Tags]    cart    negative    auth-required
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    ${body}=        Create Dictionary    productId=${1}
    ${response}=    POST On Session    techshop    /cart    headers=${headers}    json=${body}
    ...             expected_status=any
    Status Should Be    400    ${response}

Add Item To Cart With Non Integer ProductId Returns 400
    [Tags]    cart    negative    auth-required
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    ${body}=        Create Dictionary    productId=abc    quantity=${1}
    ${response}=    POST On Session    techshop    /cart    headers=${headers}    json=${body}
    ...             expected_status=any
    Status Should Be    400    ${response}


# ---------------------------------------------------------------------------
# PUT /cart/{itemId}  &  DELETE /cart/{itemId}
# (These rely on a cart item existing, so we add one first inside the test)
# ---------------------------------------------------------------------------

Update Cart Item Quantity With Valid Token Returns 200
    [Tags]    cart    happy-path    auth-required
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    # Ensure a cart item exists
    ${add_body}=    Create Dictionary    productId=${1}    quantity=${1}
    ${add_resp}=    POST On Session    techshop    /cart    headers=${headers}    json=${add_body}
    Status Should Be    201    ${add_resp}
    # Retrieve the cart to find the item id
    ${cart_resp}=   GET On Session    techshop    /cart    headers=${headers}
    Status Should Be    200    ${cart_resp}
    ${items}=       Get From Dictionary    ${cart_resp.json()}    items
    ${item}=        Get From List    ${items}    0
    ${item_id}=     Get From Dictionary    ${item}    id
    # Update the quantity
    ${upd_body}=    Create Dictionary    quantity=${3}
    ${response}=    PUT On Session    techshop    /cart/${item_id}    headers=${headers}    json=${upd_body}
    Status Should Be    200    ${response}

Update Cart Item Without Auth Returns 401
    [Tags]    cart    negative    auth-required
    ${body}=        Create Dictionary    quantity=${3}
    ${response}=    PUT On Session    techshop    /cart/1    json=${body}
    ...             expected_status=any
    Status Should Be    401    ${response}

Update Non Existent Cart Item Returns 404
    [Tags]    cart    negative    auth-required
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    ${body}=        Create Dictionary    quantity=${3}
    ${response}=    PUT On Session    techshop    /cart/99999    headers=${headers}    json=${body}
    ...             expected_status=any
    Status Should Be    404    ${response}

Update Cart Item With Zero Quantity Returns 400
    [Tags]    cart    negative    auth-required
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    # Ensure an item exists to target
    ${add_body}=    Create Dictionary    productId=${1}    quantity=${1}
    ${add_resp}=    POST On Session    techshop    /cart    headers=${headers}    json=${add_body}
    Status Should Be    201    ${add_resp}
    ${cart_resp}=   GET On Session    techshop    /cart    headers=${headers}
    ${items}=       Get From Dictionary    ${cart_resp.json()}    items
    ${item}=        Get From List    ${items}    0
    ${item_id}=     Get From Dictionary    ${item}    id
    ${body}=        Create Dictionary    quantity=${0}
    ${response}=    PUT On Session    techshop    /cart/${item_id}    headers=${headers}    json=${body}
    ...             expected_status=any
    Status Should Be    400    ${response}

Update Cart Item With Missing Quantity Returns 400
    [Tags]    cart    negative    auth-required
    [Documentation]    Uses a dynamically obtained real item ID to avoid fragility of hardcoded ID=1.
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    # Add an item so we have a guaranteed real ID
    ${add_body}=    Create Dictionary    productId=${1}    quantity=${1}
    ${add_resp}=    POST On Session    techshop    /cart    headers=${headers}    json=${add_body}
    Status Should Be    201    ${add_resp}
    ${cart_resp}=   GET On Session    techshop    /cart    headers=${headers}
    ${items}=       Get From Dictionary    ${cart_resp.json()}    items
    ${item}=        Get From List    ${items}    0
    ${item_id}=     Get From Dictionary    ${item}    id
    ${body}=        Create Dictionary
    ${response}=    PUT On Session    techshop    /cart/${item_id}    headers=${headers}    json=${body}
    ...             expected_status=any
    Status Should Be    400    ${response}

Delete Cart Item With Valid Token Returns 200
    [Tags]    cart    happy-path    auth-required
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    # Add a fresh item to delete
    ${add_body}=    Create Dictionary    productId=${1}    quantity=${1}
    ${add_resp}=    POST On Session    techshop    /cart    headers=${headers}    json=${add_body}
    Status Should Be    201    ${add_resp}
    ${cart_resp}=   GET On Session    techshop    /cart    headers=${headers}
    ${items}=       Get From Dictionary    ${cart_resp.json()}    items
    ${item}=        Get From List    ${items}    0
    ${item_id}=     Get From Dictionary    ${item}    id
    # Delete it
    ${response}=    DELETE On Session    techshop    /cart/${item_id}    headers=${headers}
    Status Should Be    200    ${response}
    # Verify the item is no longer in the cart
    ${verify_resp}=    GET On Session    techshop    /cart    headers=${headers}
    ${updated_items}=    Get From Dictionary    ${verify_resp.json()}    items
    FOR    ${remaining}    IN    @{updated_items}
        ${rid}=    Get From Dictionary    ${remaining}    id
        Should Not Be Equal As Integers    ${rid}    ${item_id}
    END

Delete Cart Item Without Auth Returns 401
    [Tags]    cart    negative    auth-required
    ${response}=    DELETE On Session    techshop    /cart/1
    ...             expected_status=any
    Status Should Be    401    ${response}

Delete Non Existent Cart Item Returns 404
    [Tags]    cart    negative    auth-required
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    ${response}=    DELETE On Session    techshop    /cart/99999    headers=${headers}
    ...             expected_status=any
    Status Should Be    404    ${response}

Delete Same Cart Item Twice Returns 404 On Second Call
    [Tags]    cart    negative    auth-required
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    # Add a fresh item
    ${add_body}=    Create Dictionary    productId=${1}    quantity=${1}
    ${add_resp}=    POST On Session    techshop    /cart    headers=${headers}    json=${add_body}
    Status Should Be    201    ${add_resp}
    ${cart_resp}=   GET On Session    techshop    /cart    headers=${headers}
    ${items}=       Get From Dictionary    ${cart_resp.json()}    items
    ${item}=        Get From List    ${items}    0
    ${item_id}=     Get From Dictionary    ${item}    id
    # First delete — should succeed
    ${first_resp}=    DELETE On Session    techshop    /cart/${item_id}    headers=${headers}
    Status Should Be    200    ${first_resp}
    # Second delete — should fail with 404
    ${second_resp}=    DELETE On Session    techshop    /cart/${item_id}    headers=${headers}
    ...                expected_status=any
    Status Should Be    404    ${second_resp}

Delete Cart Item With Non Numeric ItemId Returns 400 Or 404
    [Tags]    cart    negative    auth-required
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    ${response}=    DELETE On Session    techshop    /cart/abc    headers=${headers}
    ...             expected_status=any
    ${status}=      Set Variable    ${response.status_code}
    Should Be True    ${status} == 400 or ${status} == 404


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
    ${item}=        Create Dictionary    productId=${1}    quantity=${1}
    ${items}=       Create List    ${item}
    ${shipping}=    Create Dictionary
    ...    firstName=Schema    lastName=Check    email=schema@example.com    phone=0411111111
    ${payment}=     Create Dictionary
    ...    cardNumber=4111111111111111    expiryDate=12/28    cvv=321
    ${order_body}=  Create Dictionary    items=${items}    shipping=${shipping}    payment=${payment}
    POST On Session    techshop    /orders    headers=${headers}    json=${order_body}
    # Now fetch orders and validate schema
    ${response}=    GET On Session    techshop    /orders    headers=${headers}
    Status Should Be    200    ${response}
    ${orders}=      Set Variable    ${response.json()}
    Should Not Be Empty    ${orders}
    ${first}=       Get From List    ${orders}    0
    Dictionary Should Contain Key    ${first}    id
    Dictionary Should Contain Key    ${first}    userId
    Dictionary Should Contain Key    ${first}    items
    Dictionary Should Contain Key    ${first}    shipping
    Dictionary Should Contain Key    ${first}    payment
    Dictionary Should Contain Key    ${first}    total
    Dictionary Should Contain Key    ${first}    status
    Dictionary Should Contain Key    ${first}    createdAt
    ${pay}=         Get From Dictionary    ${first}    payment
    Dictionary Should Contain Key    ${pay}    last4

Get Orders Without Auth Returns 401
    [Tags]    orders    negative    auth-required
    ${response}=    GET On Session    techshop    /orders    expected_status=any
    Status Should Be    401    ${response}

Get Orders With Invalid Token Returns 401
    [Tags]    orders    negative    auth-required
    ${headers}=     Create Dictionary    Authorization=Bearer tampered.token.value
    ${response}=    GET On Session    techshop    /orders    headers=${headers}
    ...             expected_status=any
    Status Should Be    401    ${response}

Get Orders Returns Empty Array When User Has No Orders
    [Tags]    orders    negative    auth-required
    [Documentation]    If the test user has no orders, the API should return 200 with [].
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    ${response}=    GET On Session    techshop    /orders    headers=${headers}
    Status Should Be    200    ${response}
    # Either empty or non-empty list is valid depending on prior test state
    Should Be True    isinstance($response.json(), list)


# ---------------------------------------------------------------------------
# POST /orders (checkout)
# ---------------------------------------------------------------------------

Place Order With Valid Payload Returns 201
    [Tags]    orders    happy-path    auth-required
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    ${item}=        Create Dictionary    productId=${1}    quantity=${1}
    ${items}=       Create List    ${item}
    ${shipping}=    Create Dictionary
    ...    firstName=Jane
    ...    lastName=Doe
    ...    email=jane@example.com
    ...    phone=0412345678
    ${payment}=     Create Dictionary
    ...    cardNumber=4111111111111111
    ...    expiryDate=12/28
    ...    cvv=123
    ${body}=        Create Dictionary    items=${items}    shipping=${shipping}    payment=${payment}
    ${response}=    POST On Session    techshop    /orders    headers=${headers}    json=${body}
    Status Should Be    201    ${response}
    ${order}=    Set Variable    ${response.json()}
    # Swagger-documented required fields on the Order schema
    Dictionary Should Contain Key    ${order}    id
    Dictionary Should Contain Key    ${order}    userId
    Dictionary Should Contain Key    ${order}    items
    Dictionary Should Contain Key    ${order}    shipping
    Dictionary Should Contain Key    ${order}    total
    Dictionary Should Contain Key    ${order}    status
    Dictionary Should Contain Key    ${order}    createdAt
    ${payment_resp}=    Get From Dictionary    ${order}    payment
    Dictionary Should Contain Key    ${payment_resp}    last4
    Dictionary Should Contain Key    ${payment_resp}    expiryDate

# ---------------------------------------------------------------------------
# POST /orders — individual required sub-field validation
# (swagger requires firstName, lastName, email, phone; cardNumber, expiryDate, cvv)
# ---------------------------------------------------------------------------

Place Order With Missing Shipping First Name Returns 400
    [Tags]    orders    negative    auth-required
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    ${item}=        Create Dictionary    productId=${1}    quantity=${1}
    ${items}=       Create List    ${item}
    ${shipping}=    Create Dictionary    lastName=Doe    email=jane@example.com    phone=0412345678
    ${payment}=     Create Dictionary
    ...    cardNumber=4111111111111111    expiryDate=12/28    cvv=123
    ${body}=        Create Dictionary    items=${items}    shipping=${shipping}    payment=${payment}
    ${response}=    POST On Session    techshop    /orders    headers=${headers}    json=${body}
    ...             expected_status=any
    Status Should Be    400    ${response}

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

Place Order Without Auth Returns 401
    [Tags]    orders    negative    auth-required
    ${item}=        Create Dictionary    productId=${1}    quantity=${1}
    ${items}=       Create List    ${item}
    ${shipping}=    Create Dictionary
    ...    firstName=Jane    lastName=Doe    email=jane@example.com    phone=0412345678
    ${payment}=     Create Dictionary
    ...    cardNumber=4111111111111111    expiryDate=12/28    cvv=123
    ${body}=        Create Dictionary    items=${items}    shipping=${shipping}    payment=${payment}
    ${response}=    POST On Session    techshop    /orders    json=${body}
    ...             expected_status=any
    Status Should Be    401    ${response}

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

Place Order With Invalid Phone Number Returns 400
    [Tags]    orders    negative    auth-required
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    ${item}=        Create Dictionary    productId=${1}    quantity=${1}
    ${items}=       Create List    ${item}
    ${shipping}=    Create Dictionary
    ...    firstName=Jane    lastName=Doe    email=jane@example.com    phone=12345
    ${payment}=     Create Dictionary
    ...    cardNumber=4111111111111111    expiryDate=12/28    cvv=123
    ${body}=        Create Dictionary    items=${items}    shipping=${shipping}    payment=${payment}
    ${response}=    POST On Session    techshop    /orders    headers=${headers}    json=${body}
    ...             expected_status=any
    Status Should Be    400    ${response}

Place Order With Invalid Card Number Returns 400
    [Tags]    orders    negative    auth-required
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    ${item}=        Create Dictionary    productId=${1}    quantity=${1}
    ${items}=       Create List    ${item}
    ${shipping}=    Create Dictionary
    ...    firstName=Jane    lastName=Doe    email=jane@example.com    phone=0412345678
    ${payment}=     Create Dictionary
    ...    cardNumber=1234    expiryDate=12/28    cvv=123
    ${body}=        Create Dictionary    items=${items}    shipping=${shipping}    payment=${payment}
    ${response}=    POST On Session    techshop    /orders    headers=${headers}    json=${body}
    ...             expected_status=any
    Status Should Be    400    ${response}

Place Order With Past Expiry Date Returns 400
    [Tags]    orders    negative    auth-required
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    ${item}=        Create Dictionary    productId=${1}    quantity=${1}
    ${items}=       Create List    ${item}
    ${shipping}=    Create Dictionary
    ...    firstName=Jane    lastName=Doe    email=jane@example.com    phone=0412345678
    ${payment}=     Create Dictionary
    ...    cardNumber=4111111111111111    expiryDate=01/20    cvv=123
    ${body}=        Create Dictionary    items=${items}    shipping=${shipping}    payment=${payment}
    ${response}=    POST On Session    techshop    /orders    headers=${headers}    json=${body}
    ...             expected_status=any
    Status Should Be    400    ${response}

Place Order With Invalid CVV Returns 400
    [Tags]    orders    negative    auth-required
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    ${item}=        Create Dictionary    productId=${1}    quantity=${1}
    ${items}=       Create List    ${item}
    ${shipping}=    Create Dictionary
    ...    firstName=Jane    lastName=Doe    email=jane@example.com    phone=0412345678
    ${payment}=     Create Dictionary
    ...    cardNumber=4111111111111111    expiryDate=12/28    cvv=12
    ${body}=        Create Dictionary    items=${items}    shipping=${shipping}    payment=${payment}
    ${response}=    POST On Session    techshop    /orders    headers=${headers}    json=${body}
    ...             expected_status=any
    Status Should Be    400    ${response}

Place Order With Invalid Shipping Email Returns 400
    [Tags]    orders    negative    auth-required
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    ${item}=        Create Dictionary    productId=${1}    quantity=${1}
    ${items}=       Create List    ${item}
    ${shipping}=    Create Dictionary
    ...    firstName=Jane    lastName=Doe    email=not-an-email    phone=0412345678
    ${payment}=     Create Dictionary
    ...    cardNumber=4111111111111111    expiryDate=12/28    cvv=123
    ${body}=        Create Dictionary    items=${items}    shipping=${shipping}    payment=${payment}
    ${response}=    POST On Session    techshop    /orders    headers=${headers}    json=${body}
    ...             expected_status=any
    Status Should Be    400    ${response}

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
