*** Settings ***
Resource    ../techshop_keywords.resource

Suite Setup       Create TechShop Session
Suite Teardown    Delete All Sessions


*** Test Cases ***

# ---------------------------------------------------------------------------
# GET /products — collection
# ---------------------------------------------------------------------------

Get All Products Returns 200 With Non Empty Array
    [Tags]    products    happy-path
    ${response}=    GET On Session    techshop    /products
    Status Should Be    200    ${response}
    ${products}=    Set Variable    ${response.json()}
    Should Not Be Empty    ${products}
    ${first}=    Get From List    ${products}    0
    Dictionary Should Contain Key    ${first}    id
    Dictionary Should Contain Key    ${first}    name
    Dictionary Should Contain Key    ${first}    description
    Dictionary Should Contain Key    ${first}    price
    Dictionary Should Contain Key    ${first}    category
    Dictionary Should Contain Key    ${first}    stock
    Dictionary Should Contain Key    ${first}    inStock

Get Products Filter By Computers Returns 200 With Matching Items
    [Tags]    products    happy-path
    ${params}=      Create Dictionary    category=computers
    ${response}=    GET On Session    techshop    /products    params=${params}
    Status Should Be    200    ${response}
    ${products}=    Set Variable    ${response.json()}
    FOR    ${product}    IN    @{products}
        ${cat}=    Get From Dictionary    ${product}    category
        Should Be Equal As Strings    ${cat}    computers
    END

Get Products Filter By Audio Returns 200
    [Tags]    products    happy-path
    ${params}=      Create Dictionary    category=audio
    ${response}=    GET On Session    techshop    /products    params=${params}
    Status Should Be    200    ${response}
    Should Be True    isinstance($response.json(), list)

Get Products Filter By Accessories Returns 200
    [Tags]    products    happy-path
    ${params}=      Create Dictionary    category=accessories
    ${response}=    GET On Session    techshop    /products    params=${params}
    Status Should Be    200    ${response}
    Should Be True    isinstance($response.json(), list)

Get Products Filter By Peripherals Returns 200
    [Tags]    products    happy-path
    ${params}=      Create Dictionary    category=peripherals
    ${response}=    GET On Session    techshop    /products    params=${params}
    Status Should Be    200    ${response}
    Should Be True    isinstance($response.json(), list)

Get Products Filter Invalid Category Returns 200 Or 400
    [Tags]    products    negative
    ${params}=      Create Dictionary    category=invalid-category
    ${response}=    GET On Session    techshop    /products    params=${params}
    ...             expected_status=any
    ${status}=      Set Variable    ${response.status_code}
    Should Be True    ${status} == 200 or ${status} == 400
    Run Keyword If    ${status} == 200
    ...    Should Be True    isinstance($response.json(), list)

Get Products Unsupported Query Param Returns 200 Or 400
    [Tags]    products    negative
    ${params}=      Create Dictionary    limit=10
    ${response}=    GET On Session    techshop    /products    params=${params}
    ...             expected_status=any
    ${status}=      Set Variable    ${response.status_code}
    Should Be True    ${status} == 200 or ${status} == 400
    Run Keyword If    ${status} == 200
    ...    Should Be True    isinstance($response.json(), list)

Post To Products Returns 405 With Error Body
    [Tags]    products    negative
    ${response}=    POST On Session    techshop    /products    json=${{{}}}
    ...             expected_status=any
    Status Should Be    405    ${response}
    Response Body Should Contain Error    ${response}

# ---------------------------------------------------------------------------
# GET /products/{id} — single resource
# ---------------------------------------------------------------------------

Get Product By Valid Id Returns 200 With Schema
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

Get Product By Unknown Id Returns 404 With Error Body
    [Tags]    products    negative
    ${response}=    GET On Session    techshop    /products/99999
    ...             expected_status=any
    Status Should Be    404    ${response}
    Response Body Should Contain Error    ${response}

Get Product By Non Numeric Id Returns 400 Or 404 With Error Body
    [Tags]    products    negative
    ${response}=    GET On Session    techshop    /products/abc
    ...             expected_status=any
    ${status}=      Set Variable    ${response.status_code}
    Should Be True    ${status} == 400 or ${status} == 404
    Response Body Should Contain Error    ${response}

Get Product By Negative Id Returns 400 Or 404 With Error Body
    [Tags]    products    negative
    ${response}=    GET On Session    techshop    /products/-1
    ...             expected_status=any
    ${status}=      Set Variable    ${response.status_code}
    Should Be True    ${status} == 400 or ${status} == 404
    Response Body Should Contain Error    ${response}

Get Product With Missing Id Segment Returns 200 Or 404
    [Tags]    products    negative
    [Documentation]    GET /products/ (trailing slash) — Express either routes to
    ...                /products (200) or returns 404.
    ${response}=    GET On Session    techshop    /products/
    ...             expected_status=any
    ${status}=      Set Variable    ${response.status_code}
    Should Be True    ${status} == 200 or ${status} == 404
