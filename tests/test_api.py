import uuid
from fastapi.testclient import TestClient
import src.app as appmod

client = TestClient(appmod.app)


def unique_email():
    return f"test-{uuid.uuid4().hex}@example.com"


def test_get_activities():
    r = client.get("/activities")
    assert r.status_code == 200
    data = r.json()
    # Expect some sample activities from the in-memory DB
    assert "Chess Club" in data
    assert "Basketball Team" in data


def test_signup_and_unregister_flow():
    activity = "Basketball Team"
    email = unique_email()

    # Ensure not present
    client.delete(f"/activities/{activity}/participants", params={"email": email})

    # Signup
    r = client.post(f"/activities/{activity}/signup?email={email}")
    assert r.status_code == 200
    assert "Signed up" in r.json().get("message", "")

    # GET should include participant
    r2 = client.get("/activities")
    participants = r2.json()[activity]["participants"]
    assert email in participants

    # Duplicate signup should return 400
    rdup = client.post(f"/activities/{activity}/signup?email={email}")
    assert rdup.status_code == 400

    # Unregister
    rdel = client.delete(f"/activities/{activity}/participants", params={"email": email})
    assert rdel.status_code == 200
    assert "Unregistered" in rdel.json().get("message", "")

    # Verify removed
    r3 = client.get("/activities")
    assert email not in r3.json()[activity]["participants"]


def test_unregister_nonexistent_and_activity_missing():
    # Non-existent participant
    activity = "Chess Club"
    email = unique_email()  # obviously not present
    r = client.delete(f"/activities/{activity}/participants", params={"email": email})
    assert r.status_code == 404

    # Non-existent activity
    r2 = client.post(f"/activities/NoSuchActivity/signup?email={unique_email()}")
    assert r2.status_code == 404
    r3 = client.delete(f"/activities/NoSuchActivity/participants", params={"email": email})
    assert r3.status_code == 404
