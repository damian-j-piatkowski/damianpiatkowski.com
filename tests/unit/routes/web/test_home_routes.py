"""Tests for the contact form submission.

This module contains tests for the /submit_contact endpoint,
ensuring that contact form submissions are processed correctly, with valid and
invalid inputs, and that appropriate flash messages are shown based on form
input.

Test functions:
- test_submit_contact_invalid_input: Tests submitting an invalid contact form.
- test_submit_contact_valid_input: Tests submitting a valid contact form.
"""


def test_submit_contact_invalid_input(client, mocker):
    """Test submitting an invalid contact form.

    This test checks the behavior of the form submission when invalid data
    is provided (in this case, empty data). It ensures that the response is
    handled correctly, the error message is displayed, and the controller
    function is not successful.
    """
    # Mock the contact controller
    mocker.patch(
        'app.controllers.contact_controller.handle_contact_form_submission',
        return_value=(False, 'All fields are required!', 'danger')
    )

    # Post an invalid contact form submission (empty data)
    response = client.post('/submit_contact', data={}, follow_redirects=True)

    # Check if the status code is 200
    assert response.status_code == 200

    # Check for the presence of the error message in the response data
    assert b'All fields are required!' in response.data


def test_submit_contact_valid_input(client, mocker):
    """Test submitting a valid contact form.

    This test checks that the form submission works correctly when valid data
    is provided. It mocks the controller to ensure the correct flash messages
    are shown for a successful submission.
    """
    # Mock the contact controller
    mocker.patch(
        'app.controllers.contact_controller.handle_contact_form_submission',
        return_value=(True, 'Message sent successfully!', 'success')
    )

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
