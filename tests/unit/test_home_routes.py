from extensions import mail


def test_submit_contact_valid_input(client, mocker):
    # Mock the mail send function
    mock_mail_send = mocker.patch.object(mail, 'send', autospec=True)

    # Post a valid contact form submission
    response = client.post('/submit_contact', data={
        'name': 'Test User',
        'email': 'test@example.com',
        'message': 'This is a test message.'
    }, follow_redirects=True)

    # Check if the status code is 200
    assert response.status_code == 200

    # Check for the presence of the success message in the response data
    assert b'Message sent successfully!' in response.data

    # Ensure the mail send function was called once
    mock_mail_send.assert_called_once()

    # Check for the success flash message in the response data
    assert b'Message sent successfully!' in response.data


def test_submit_contact_invalid_input(client, mocker):
    # Mock the mail send function
    mock_mail_send = mocker.patch.object(mail, 'send', autospec=True)

    # Post an invalid contact form submission (empty data)
    response = client.post('/submit_contact', data={}, follow_redirects=True)

    # Check if the status code is 200
    assert response.status_code == 200

    # Check for the presence of the error message in the response data
    assert b'All fields are required!' in response.data

    # Ensure the mail send function was not called
    mock_mail_send.assert_not_called()

    # Check for the error flash message in the response data
    assert b'All fields are required!' in response.data
