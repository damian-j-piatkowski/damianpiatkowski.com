from extensions import mail

def test_email_sending(client):
    with mail.record_messages() as outbox:
        response = client.post('/submit_contact', data={
            'name': 'John Doe',
            'email': 'john@example.com',
            'message': 'Hello, this is a test message.'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert len(outbox) == 1
        assert outbox[0].subject == "Contact Form Submission"
        assert "John Doe" in outbox[0].body
        assert "john@example.com" in outbox[0].body
        assert "Hello, this is a test message." in outbox[0].body
