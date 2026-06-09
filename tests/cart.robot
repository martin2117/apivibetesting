*** Settings ***
Resource    ../techshop_keywords.resource

Suite Setup       Create TechShop Session
Suite Teardown    Delete All Sessions


*** Test Cases ***

# ---------------------------------------------------------------------------
# GET /cart
# ---------------------------------------------------------------------------

Get Cart With Valid Token Returns 200 With Schema
    [Tags]    cart    happy-path    auth-required
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    ${response}=    GET On Session    techshop    /cart    headers=${headers}
    Status Should Be    200    ${response}
    ${cart}=    Set Variable    ${response.json()}
    Dictionary Should Contain Key    ${cart}    items
    Dictionary Should Contain Key    ${cart}    total
    Should Be True    isinstance($cart['items'], list)
    Should Be True    isinstance($cart['total'], (int, float))

Get Cart Without Auth Token Returns 401 With Error Body
    [Tags]    cart    negative    auth-required
    ${response}=    GET On Session    techshop    /cart    expected_status=any
    Status Should Be    401    ${response}
    Response Body Should Contain Error    ${response}

Get Cart With Invalid Token Returns 401 With Error Body
    [Tags]    cart    negative    auth-required
    ${headers}=     Create Dictionary    Authorization=Bearer this.is.not.a.valid.token
    ${response}=    GET On Session    techshop    /cart    headers=${headers}
    ...             expected_status=any
    Status Should Be    401    ${response}
    Response Body Should Contain Error    ${response}

Get Cart With Malformed Auth Header Returns 401 With Error Body
    [Tags]    cart    negative    auth-required
    ${headers}=     Create Dictionary    Authorization=Bearer
    ${response}=    GET On Session    techshop    /cart    headers=${headers}
    ...             expected_status=any
    Status Should Be    401    ${response}
    Response Body Should Contain Error    ${response}

Get Cart With Basic Auth Scheme Returns 401 With Error Body
    [Tags]    cart    negative    auth-required
    ${headers}=     Create Dictionary    Authorization=Basic dXNlcjpwYXNz
    ${response}=    GET On Session    techshop    /cart    headers=${headers}
    ...             expected_status=any
    Status Should Be    401    ${response}
    Response Body Should Contain Error    ${response}

# ---------------------------------------------------------------------------
# POST /cart
# ---------------------------------------------------------------------------

Add Item To Cart Returns 201 With Body
    [Tags]    cart    happy-path    auth-required
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    ${body}=        Create Dictionary    productId=${1}    quantity=${2}
    ${response}=    POST On Session    techshop    /cart    headers=${headers}    json=${body}
    Status Should Be    201    ${response}
    Should Not Be Empty    ${response.json()}

Add Item Reflected In Get Cart
    [Tags]    cart    happy-path    auth-required
    [Documentation]    POST /cart then GET /cart — the added product must appear in the items list.
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    ${body}=        Create Dictionary    productId=${2}    quantity=${3}
    ${post_resp}=   POST On Session    techshop    /cart    headers=${headers}    json=${body}
    Status Should Be    201    ${post_resp}
    ${cart_resp}=   GET On Session    techshop    /cart    headers=${headers}
    Status Should Be    200    ${cart_resp}
    ${items}=       Get From Dictionary    ${cart_resp.json()}    items
    Should Not Be Empty    ${items}
    ${found}=    Set Variable    ${FALSE}
    FOR    ${item}    IN    @{items}
        ${pid}=    Get From Dictionary    ${item}    productId
        Run Keyword If    ${pid} == 2    Set Test Variable    ${found}    ${TRUE}
    END
    Should Be True    ${found}    msg=productId 2 should appear in cart after adding

Add Item Without Auth Returns 401 With Error Body
    [Tags]    cart    negative    auth-required
    ${body}=        Create Dictionary    productId=${1}    quantity=${2}
    ${response}=    POST On Session    techshop    /cart    json=${body}
    ...             expected_status=any
    Status Should Be    401    ${response}
    Response Body Should Contain Error    ${response}

Add Non Existent Product Returns 404 With Error Body
    [Tags]    cart    negative    auth-required
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    ${body}=        Create Dictionary    productId=${99999}    quantity=${1}
    ${response}=    POST On Session    techshop    /cart    headers=${headers}    json=${body}
    ...             expected_status=any
    Status Should Be    404    ${response}
    Response Body Should Contain Error    ${response}

Add Item With Zero Quantity Returns 400 With Error Body
    [Tags]    cart    negative    auth-required
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    ${body}=        Create Dictionary    productId=${1}    quantity=${0}
    ${response}=    POST On Session    techshop    /cart    headers=${headers}    json=${body}
    ...             expected_status=any
    Status Should Be    400    ${response}
    Response Body Should Contain Error    ${response}

Add Item With Negative Quantity Returns 400 With Error Body
    [Tags]    cart    negative    auth-required
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    ${body}=        Create Dictionary    productId=${1}    quantity=${-1}
    ${response}=    POST On Session    techshop    /cart    headers=${headers}    json=${body}
    ...             expected_status=any
    Status Should Be    400    ${response}
    Response Body Should Contain Error    ${response}

Add Item With Missing ProductId Returns 400 With Error Body
    [Tags]    cart    negative    auth-required
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    ${body}=        Create Dictionary    quantity=${2}
    ${response}=    POST On Session    techshop    /cart    headers=${headers}    json=${body}
    ...             expected_status=any
    Status Should Be    400    ${response}
    Response Body Should Contain Error    ${response}

Add Item With Missing Quantity Returns 400 With Error Body
    [Tags]    cart    negative    auth-required
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    ${body}=        Create Dictionary    productId=${1}
    ${response}=    POST On Session    techshop    /cart    headers=${headers}    json=${body}
    ...             expected_status=any
    Status Should Be    400    ${response}
    Response Body Should Contain Error    ${response}

Add Item With Non Integer ProductId Returns 400 With Error Body
    [Tags]    cart    negative    auth-required
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    ${body}=        Create Dictionary    productId=abc    quantity=${1}
    ${response}=    POST On Session    techshop    /cart    headers=${headers}    json=${body}
    ...             expected_status=any
    Status Should Be    400    ${response}
    Response Body Should Contain Error    ${response}

# ---------------------------------------------------------------------------
# PUT /cart/{itemId}
# ---------------------------------------------------------------------------

Update Cart Item Quantity Returns 200 With Body
    [Tags]    cart    happy-path    auth-required
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    ${add_body}=    Create Dictionary    productId=${1}    quantity=${1}
    ${add_resp}=    POST On Session    techshop    /cart    headers=${headers}    json=${add_body}
    Status Should Be    201    ${add_resp}
    ${cart_resp}=   GET On Session    techshop    /cart    headers=${headers}
    ${items}=       Get From Dictionary    ${cart_resp.json()}    items
    ${item}=        Get From List    ${items}    0
    ${item_id}=     Get From Dictionary    ${item}    id
    ${upd_body}=    Create Dictionary    quantity=${3}
    ${response}=    PUT On Session    techshop    /cart/${item_id}    headers=${headers}    json=${upd_body}
    Status Should Be    200    ${response}
    Should Not Be Empty    ${response.json()}

Update Cart Item Without Auth Returns 401 With Error Body
    [Tags]    cart    negative    auth-required
    ${body}=        Create Dictionary    quantity=${3}
    ${response}=    PUT On Session    techshop    /cart/1    json=${body}
    ...             expected_status=any
    Status Should Be    401    ${response}
    Response Body Should Contain Error    ${response}

Update Non Existent Cart Item Returns 404 With Error Body
    [Tags]    cart    negative    auth-required
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    ${body}=        Create Dictionary    quantity=${3}
    ${response}=    PUT On Session    techshop    /cart/99999    headers=${headers}    json=${body}
    ...             expected_status=any
    Status Should Be    404    ${response}
    Response Body Should Contain Error    ${response}

Update Cart Item With Zero Quantity Returns 400 With Error Body
    [Tags]    cart    negative    auth-required
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
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
    Response Body Should Contain Error    ${response}

Update Cart Item With Missing Quantity Returns 400 With Error Body
    [Tags]    cart    negative    auth-required
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
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
    Response Body Should Contain Error    ${response}

# ---------------------------------------------------------------------------
# DELETE /cart/{itemId}
# ---------------------------------------------------------------------------

Delete Cart Item Returns 200 And Removes Item
    [Tags]    cart    happy-path    auth-required
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    ${add_body}=    Create Dictionary    productId=${1}    quantity=${1}
    ${add_resp}=    POST On Session    techshop    /cart    headers=${headers}    json=${add_body}
    Status Should Be    201    ${add_resp}
    ${cart_resp}=   GET On Session    techshop    /cart    headers=${headers}
    ${items}=       Get From Dictionary    ${cart_resp.json()}    items
    ${item}=        Get From List    ${items}    0
    ${item_id}=     Get From Dictionary    ${item}    id
    ${response}=    DELETE On Session    techshop    /cart/${item_id}    headers=${headers}
    Status Should Be    200    ${response}
    ${verify}=      GET On Session    techshop    /cart    headers=${headers}
    ${remaining}=   Get From Dictionary    ${verify.json()}    items
    FOR    ${r}    IN    @{remaining}
        ${rid}=    Get From Dictionary    ${r}    id
        Should Not Be Equal As Integers    ${rid}    ${item_id}
    END

Delete Cart Item Without Auth Returns 401 With Error Body
    [Tags]    cart    negative    auth-required
    ${response}=    DELETE On Session    techshop    /cart/1
    ...             expected_status=any
    Status Should Be    401    ${response}
    Response Body Should Contain Error    ${response}

Delete Non Existent Cart Item Returns 404 With Error Body
    [Tags]    cart    negative    auth-required
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    ${response}=    DELETE On Session    techshop    /cart/99999    headers=${headers}
    ...             expected_status=any
    Status Should Be    404    ${response}
    Response Body Should Contain Error    ${response}

Delete Same Cart Item Twice Second Returns 404 With Error Body
    [Tags]    cart    negative    auth-required
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    ${add_body}=    Create Dictionary    productId=${1}    quantity=${1}
    ${add_resp}=    POST On Session    techshop    /cart    headers=${headers}    json=${add_body}
    Status Should Be    201    ${add_resp}
    ${cart_resp}=   GET On Session    techshop    /cart    headers=${headers}
    ${items}=       Get From Dictionary    ${cart_resp.json()}    items
    ${item}=        Get From List    ${items}    0
    ${item_id}=     Get From Dictionary    ${item}    id
    ${first}=       DELETE On Session    techshop    /cart/${item_id}    headers=${headers}
    Status Should Be    200    ${first}
    ${second}=      DELETE On Session    techshop    /cart/${item_id}    headers=${headers}
    ...             expected_status=any
    Status Should Be    404    ${second}
    Response Body Should Contain Error    ${second}

Delete Cart Item With Non Numeric Id Returns 400 Or 404 With Error Body
    [Tags]    cart    negative    auth-required
    ${token}=       Get Auth Token
    ${headers}=     Auth Header    ${token}
    ${response}=    DELETE On Session    techshop    /cart/abc    headers=${headers}
    ...             expected_status=any
    ${status}=      Set Variable    ${response.status_code}
    Should Be True    ${status} == 400 or ${status} == 404
    Response Body Should Contain Error    ${response}
