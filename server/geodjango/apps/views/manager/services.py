
from apps.models import Manager
import logging
from django.db import IntegrityError

def getManager(cognitoId: str):
    try:
        manager = Manager.objects.get(cognitoId = cognitoId)
        logging.info(f"Found Manager: {manager} (cognitoId: {cognitoId})")
        return manager
    except Manager.DoesNotExist:
        logging.warning(f"No Manager found with cognitoId: {cognitoId} or no favorites")
        return None
    except Exception as e:
        logging.error(f"Error retrieving Manager with cognitoId {cognitoId}: {e}")
        raise

def createManager(cognitoId: str, name: str, email: str, phoneNumber: str):
    """
    Create a new Manager with the given details and optionally add favorite Properties.
    Args:
        cognito_id (str): Unique Cognito ID.
        name (str): Manager name.
        email (str): Manager email.
        phone_number (str): Manager phone number.
        property_ids (list, optional): List of Property IDs to add to favorites.
    Returns:
        Manager: Created Manager instance.
    Raises:
        IntegrityError: If cognito_id already exists.
        ValueError: If input data is invalid.
        Exception: For other unexpected errors.
    """
    try:
        # Validate inputs
        if not all([cognitoId, name, email, phoneNumber]):
            raise ValueError("All fiels (cognitoId, name, email, phoneNumber) are required")
        manager = Manager.objects.create(
            cognitoId=cognitoId, 
            name=name, 
            email=email, 
            phoneNumber=phoneNumber
        )
        logging.info(f"Created Manager: {manager}")
        return manager
    except IntegrityError as e:
        logging.error(f"Failed to create Manager with cognitoId {cognitoId}: Duplicate cognitoId")
        raise ValueError(f"Manager with cognitoId {cognitoId} already exists")
    except ValueError as e:
        logging.error(f"Invalid input for creating Manager: {str(e)}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error creating Manager with cognitoId {cognitoId}: {str(e)}")
        raise
def updateManager(cognitoId: str, name: str, email: str, phoneNumber: str):
    """
    Update a new Manager with the given details and optionally add favorite Properties.
    Args:
        cognito_id (str): Unique Cognito ID.
        name (str): Manager name.
        email (str): Manager email.
        phone_number (str): Manager phone number.
        property_ids (list, optional): List of Property IDs to add to favorites.
    Returns:
        Manager: Created Manager instance.
    Raises:
        IntegrityError: If cognito_id already exists.
        ValueError: If input data is invalid.
        Exception: For other unexpected errors.
    """
    try:
        # Validate inputs
        if not all([cognitoId, name, email, phoneNumber]):
            raise ValueError("All fiels (cognitoId, name, email, phoneNumber) are required")
        updateManager = Manager.objects.get(cognitoId=cognitoId)
        updateManager.name=name, 
        updateManager.email=email, 
        updateManager.phoneNumber=phoneNumber
        updateManager.save()
        logging.info(f"Updated Manager: {updateManager}")
        return updateManager
    except IntegrityError as e:
        logging.error(f"Failed to update Manager with cognitoId {cognitoId}: Duplicate cognitoId")
        raise ValueError(f"Manager with cognitoId {cognitoId} already exists")
    except ValueError as e:
        logging.error(f"Invalid input for updating Manager: {str(e)}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error updating Manager with cognitoId {cognitoId}: {str(e)}")
        raise

    


