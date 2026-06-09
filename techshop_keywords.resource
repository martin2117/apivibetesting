*** Settings ***
Library     RequestsLibrary
Library     Collections
Library     OperatingSystem


*** Variables ***
${BASE_URL}     %{BASE_URL=http://localhost:3000}
${EMAIL}        %{TEST_EMAIL=demo@techshop.com}
${PASSWORD}     %{TEST_PASSWORD=password123}


*** Keywords ***
Create TechShop Session
    [Documentation]    Opens a named HTTP session against BASE_URL with a 10 s timeout.
    ...                Called by Suite Setup in every resource file.
    Create Session    techshop    ${BASE_URL}    verify=true    timeout=10

Get Auth Token
    [Documentation]    Logs in with the configured credentials and returns the JWT.
    ${body}=        Create Dictionary    email=${EMAIL}    password=${PASSWORD}
    ${response}=    POST On Session    techshop    /auth/login    json=${body}
    Status Should Be    200    ${response}
    ${token}=       Get From Dictionary    ${response.json()}    token
    RETURN    ${token}

Auth Header
    [Documentation]    Returns an Authorization header dict for the given token.
    [Arguments]    ${token}
    ${headers}=    Create Dictionary    Authorization=Bearer ${token}
    RETURN    ${headers}

Response Body Should Contain Error
    [Documentation]    Asserts that the JSON response body contains an "error" or "message" key.
    [Arguments]    ${response}
    ${body}=    Set Variable    ${response.json()}
    ${has_error}=      Run Keyword And Return Status
    ...    Dictionary Should Contain Key    ${body}    error
    ${has_message}=    Run Keyword And Return Status
    ...    Dictionary Should Contain Key    ${body}    message
    Should Be True    ${has_error} or ${has_message}
    ...    msg=Response body must contain "error" or "message" key. Got: ${body}

Response Body Should Contain Key
    [Documentation]    Convenience wrapper — asserts a key exists in the JSON body.
    [Arguments]    ${response}    ${key}
    Dictionary Should Contain Key    ${response.json()}    ${key}

Verify Order Schema
    [Documentation]    Asserts that an order dict contains all swagger-required keys.
    [Arguments]    ${order}
    Dictionary Should Contain Key    ${order}    id
    Dictionary Should Contain Key    ${order}    userId
    Dictionary Should Contain Key    ${order}    items
    Dictionary Should Contain Key    ${order}    shipping
    Dictionary Should Contain Key    ${order}    total
    Dictionary Should Contain Key    ${order}    status
    Dictionary Should Contain Key    ${order}    createdAt
    ${payment}=    Get From Dictionary    ${order}    payment
    Dictionary Should Contain Key    ${payment}    last4

Build Valid Order Body
    [Documentation]    Returns a valid POST /orders request body dict.
    [Arguments]
    ...    ${firstName}=Jane    ${lastName}=Doe
    ...    ${email}=jane@example.com    ${phone}=0412345678
    ...    ${cardNumber}=4111111111111111    ${expiryDate}=12/28    ${cvv}=123
    ${item}=        Create Dictionary    productId=${1}    quantity=${1}
    ${items}=       Create List    ${item}
    ${shipping}=    Create Dictionary
    ...    firstName=${firstName}    lastName=${lastName}
    ...    email=${email}    phone=${phone}
    ${payment}=     Create Dictionary
    ...    cardNumber=${cardNumber}    expiryDate=${expiryDate}    cvv=${cvv}
    ${body}=        Create Dictionary    items=${items}    shipping=${shipping}    payment=${payment}
    RETURN    ${body}
