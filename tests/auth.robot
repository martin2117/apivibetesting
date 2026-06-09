*** Settings ***
Resource    ../techshop_keywords.resource

Suite Setup       Create TechShop Session
Suite Teardown    Delete All Sessions


*** Test Cases ***

# ---------------------------------------------------------------------------
# POST /auth/login — happy path
# ---------------------------------------------------------------------------

Login With Valid Credentials Returns 200
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
    Should Not Be Empty    ${json}[token]

# ---------------------------------------------------------------------------
# POST /auth/login — credential errors
# ---------------------------------------------------------------------------

Login With Wrong Password Returns 401
    [Tags]    auth    negative
    ${body}=        Create Dictionary    email=${EMAIL}    password=this-is-definitely-wrong
    ${response}=    POST On Session    techshop    /auth/login    json=${body}
    ...             expected_status=any
    Status Should Be    401    ${response}
    Response Body Should Contain Error    ${response}

Login With Unknown User Returns 401
    [Tags]    auth    negative
    ${body}=        Create Dictionary    email=nobody@unknown-domain-xyz.com    password=irrelevant
    ${response}=    POST On Session    techshop    /auth/login    json=${body}
    ...             expected_status=any
    Status Should Be    401    ${response}
    Response Body Should Contain Error    ${response}

# ---------------------------------------------------------------------------
# POST /auth/login — missing / empty field errors
# ---------------------------------------------------------------------------

Login With Missing Email Returns 400
    [Tags]    auth    negative
    ${body}=        Create Dictionary    password=${PASSWORD}
    ${response}=    POST On Session    techshop    /auth/login    json=${body}
    ...             expected_status=any
    Status Should Be    400    ${response}
    Response Body Should Contain Error    ${response}

Login With Missing Password Returns 400
    [Tags]    auth    negative
    ${body}=        Create Dictionary    email=${EMAIL}
    ${response}=    POST On Session    techshop    /auth/login    json=${body}
    ...             expected_status=any
    Status Should Be    400    ${response}
    Response Body Should Contain Error    ${response}

Login With Empty Body Returns 400
    [Tags]    auth    negative
    ${body}=        Create Dictionary
    ${response}=    POST On Session    techshop    /auth/login    json=${body}
    ...             expected_status=any
    Status Should Be    400    ${response}
    Response Body Should Contain Error    ${response}
