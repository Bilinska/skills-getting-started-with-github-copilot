"""
Business logic services for the High School Activities API.
"""

from fastapi import HTTPException


def is_valid_email(email: str) -> bool:
    """Basic email validation - must contain @ and have text before and after."""
    if not email or not isinstance(email, str):
        return False
    parts = email.split("@")
    return len(parts) == 2 and len(parts[0]) > 0 and len(parts[1]) > 0


def get_all_activities(activities: dict) -> dict:
    """Get all activities.
    
    Args:
        activities: Dictionary of activities
        
    Returns:
        Dictionary of all activities
    """
    return activities


def get_activity(activities: dict, activity_name: str) -> dict:
    """Get a specific activity by name.
    
    Args:
        activities: Dictionary of activities
        activity_name: Name of the activity
        
    Returns:
        Activity dictionary
        
    Raises:
        HTTPException: 404 if activity not found
    """
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activities[activity_name]


def signup_participant(activities: dict, activity_name: str, email: str) -> str:
    """Sign up a participant for an activity.
    
    Args:
        activities: Dictionary of activities
        activity_name: Name of the activity
        email: Email of the participant
        
    Returns:
        Success message
        
    Raises:
        HTTPException: 400/404/409 for various validation failures
    """
    # Validate email format
    if not is_valid_email(email):
        raise HTTPException(status_code=400, detail="Invalid email format")
    
    # Check if activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    activity = activities[activity_name]
    
    # Check if participant already registered
    if email in activity["participants"]:
        raise HTTPException(
            status_code=409, 
            detail=f"{email} is already registered for {activity_name}"
        )
    
    # Check capacity limit
    if len(activity["participants"]) >= activity["max_participants"]:
        raise HTTPException(
            status_code=409, 
            detail=f"Activity {activity_name} is at capacity"
        )
    
    # Add participant
    activity["participants"].append(email)
    return f"Signed up {email} for {activity_name}"


def unregister_participant(activities: dict, activity_name: str, email: str) -> str:
    """Unregister a participant from an activity.
    
    Args:
        activities: Dictionary of activities
        activity_name: Name of the activity
        email: Email of the participant
        
    Returns:
        Success message
        
    Raises:
        HTTPException: 400/404 for validation failures
    """
    # Validate email format
    if not is_valid_email(email):
        raise HTTPException(status_code=400, detail="Invalid email format")
    
    # Check if activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    activity = activities[activity_name]
    
    # Check if participant exists
    if email not in activity["participants"]:
        raise HTTPException(
            status_code=404, 
            detail=f"{email} is not registered for {activity_name}"
        )
    
    # Remove participant
    activity["participants"].remove(email)
    return f"Unregistered {email} from {activity_name}"
