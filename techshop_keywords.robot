*** Settings ***
Library     RequestsLibrary
Library     Collections
Library     OperatingSystem


*** Variables ***
${BASE_URL}     %{BASE_URL}
${EMAIL}        %{TEST_EMAIL}
${PASSWORD}     %{TEST_PASSWORD}


*** Keywords ***
Create TechShop Session
    [Documentation]    Opens a named HTTP session against BASE_URL. Called by Suite Setup.
    Create Session    techshop    ${BASE_URL}    verify=true

Get Auth Token
    [Documentation]    Logs in with the configured credentials and returns the JWT token.
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
